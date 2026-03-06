#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meeseeks Health Monitor
========================

System health monitoring for the Meeseeks AGI infrastructure.

Capabilities:
- CPU/memory monitoring (system + processes)
- Process status checks (subagent workers)
- Meeseeks worker health (active, stuck, timeout detection)
- Integration with existing systems (retry chains, entombment, rate limits)
- Prometheus-style metrics export
- Health alerts and recommendations

Usage:
    # Quick health check
    python health_monitor.py

    # Full status report
    python health_monitor.py --full

    # Prometheus metrics
    python health_monitor.py --metrics

    # Watch mode (continuous monitoring)
    python health_monitor.py --watch --interval 30

    # Export to file
    python health_monitor.py --export health_report.json

API Usage:
    from health_monitor import HealthMonitor
    
    monitor = HealthMonitor()
    health = monitor.check_health()
    print(health.summary())
"""

import json
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# Set stdout to UTF-8 for Windows (only when running as main)
if sys.platform == 'win32' and __name__ == '__main__':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except (AttributeError, ValueError):
        pass

# Try to import psutil (optional but recommended)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[health_monitor] Warning: psutil not available. Install with: pip install psutil")

# Paths
WORKSPACE = Path(os.environ.get('WORKSPACE', 'C:/Users/aaron/.openclaw/workspace'))
CRYPT_ROOT = WORKSPACE / "the-crypt"
RUNS_FILE = Path.home() / ".openclaw" / "subagents" / "runs.json"
HEALTH_LOG = CRYPT_ROOT / "health_log.jsonl"
HEALTH_STATE = CRYPT_ROOT / "health_state.json"

# Thresholds
CPU_WARNING_THRESHOLD = 80  # %
CPU_CRITICAL_THRESHOLD = 95  # %
MEMORY_WARNING_THRESHOLD = 80  # %
MEMORY_CRITICAL_THRESHOLD = 95  # %
DISK_WARNING_THRESHOLD = 85  # %
DISK_CRITICAL_THRESHOLD = 95  # %
STUCK_THRESHOLD_MINUTES = 10  # minutes without progress
TIMEOUT_THRESHOLD_MINUTES = 30  # likely timeout


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class SystemMetrics:
    """System-level metrics."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    load_average: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    process_count: int = 0
    python_process_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorkerHealth:
    """Health status of a Meeseeks worker."""
    session_key: str
    task: str
    status: str  # active, stuck, timeout, done, failed
    runtime_minutes: float
    model: str
    started_at: Optional[str] = None
    last_progress: Optional[str] = None
    warning: Optional[str] = None


@dataclass
class MeeseeksStats:
    """Statistics from Meeseeks systems."""
    total_ancestors: int = 0
    total_dreams: int = 0
    total_karma: int = 0
    total_retries: int = 0
    total_failures: int = 0
    total_rate_limits: int = 0
    active_workers: int = 0
    stuck_workers: int = 0
    timeout_workers: int = 0
    recent_failures_24h: int = 0
    pending_tasks: int = 0


@dataclass
class HealthReport:
    """Complete health report."""
    status: HealthStatus
    system: SystemMetrics
    workers: List[WorkerHealth]
    meeseeks: MeeseeksStats
    alerts: List[str]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "=" * 60,
            f"🥒 MEESEEKS HEALTH REPORT - {self.timestamp}",
            "=" * 60,
            "",
            f"Overall Status: {self.status.value.upper()}",
            "",
            "📊 SYSTEM METRICS",
            f"  CPU: {self.system.cpu_percent:.1f}%",
            f"  Memory: {self.system.memory_percent:.1f}% ({self.system.memory_used_gb:.1f}/{self.system.memory_total_gb:.1f} GB)",
            f"  Disk: {self.system.disk_percent:.1f}%",
            f"  Python Processes: {self.system.python_process_count}",
            "",
            "🥒 MEESEEKS STATS",
            f"  Active Workers: {self.meeseeks.active_workers}",
            f"  Stuck Workers: {self.meeseeks.stuck_workers}",
            f"  Timeout Workers: {self.meeseeks.timeout_workers}",
            f"  Total Ancestors: {self.meeseeks.total_ancestors}",
            f"  Recent Failures (24h): {self.meeseeks.recent_failures_24h}",
            "",
        ]
        
        if self.workers:
            lines.append("👷 WORKER STATUS")
            for w in self.workers[:10]:  # Show first 10
                status_icon = {"active": "🔄", "stuck": "⚠️", "timeout": "🔴", "done": "✅", "failed": "❌"}.get(w.status, "❓")
                lines.append(f"  {status_icon} {w.session_key[:30]}... [{w.runtime_minutes:.1f}m] {w.status}")
                if w.warning:
                    lines.append(f"      ⚠️ {w.warning}")
            lines.append("")
        
        if self.alerts:
            lines.append("🚨 ALERTS")
            for alert in self.alerts:
                lines.append(f"  - {alert}")
            lines.append("")
        
        if self.recommendations:
            lines.append("💡 RECOMMENDATIONS")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "system": asdict(self.system),
            "workers": [asdict(w) for w in self.workers],
            "meeseeks": asdict(self.meeseeks),
            "alerts": self.alerts,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp
        }
    
    def to_prometheus(self) -> str:
        """Generate Prometheus-style metrics."""
        lines = [
            "# HELP meeseeks_health_status Overall health status (1=healthy, 2=warning, 3=critical, 0=unknown)",
            "# TYPE meeseeks_health_status gauge",
            f"meeseeks_health_status {self._status_to_value()}",
            "",
            "# HELP meeseeks_system_cpu_percent System CPU usage percent",
            "# TYPE meeseeks_system_cpu_percent gauge",
            f"meeseeks_system_cpu_percent {self.system.cpu_percent}",
            "",
            "# HELP meeseeks_system_memory_percent System memory usage percent",
            "# TYPE meeseeks_system_memory_percent gauge",
            f"meeseeks_system_memory_percent {self.system.memory_percent}",
            "",
            "# HELP meeseeks_system_disk_percent System disk usage percent",
            "# TYPE meeseeks_system_disk_percent gauge",
            f"meeseeks_system_disk_percent {self.system.disk_percent}",
            "",
            "# HELP meeseeks_python_processes Number of Python processes",
            "# TYPE meeseeks_python_processes gauge",
            f"meeseeks_python_processes {self.system.python_process_count}",
            "",
            "# HELP meeseeks_workers_active Active Meeseeks workers",
            "# TYPE meeseeks_workers_active gauge",
            f"meeseeks_workers_active {self.meeseeks.active_workers}",
            "",
            "# HELP meeseeks_workers_stuck Stuck Meeseeks workers",
            "# TYPE meeseeks_workers_stuck gauge",
            f"meeseeks_workers_stuck {self.meeseeks.stuck_workers}",
            "",
            "# HELP meeseeks_workers_timeout Timed out Meeseeks workers",
            "# TYPE meeseeks_workers_timeout gauge",
            f"meeseeks_workers_timeout {self.meeseeks.timeout_workers}",
            "",
            "# HELP meeseeks_ancestors_total Total ancestors in crypt",
            "# TYPE meeseeks_ancestors_total gauge",
            f"meeseeks_ancestors_total {self.meeseeks.total_ancestors}",
            "",
            "# HELP meeseeks_failures_24h Failures in last 24 hours",
            "# TYPE meeseeks_failures_24h gauge",
            f"meeseeks_failures_24h {self.meeseeks.recent_failures_24h}",
            "",
            "# HELP meeseeks_rate_limits_total Total rate limit events",
            "# TYPE meeseeks_rate_limits_total gauge",
            f"meeseeks_rate_limits_total {self.meeseeks.total_rate_limits}",
            "",
        ]
        return "\n".join(lines)
    
    def _status_to_value(self) -> int:
        """Convert status to numeric value."""
        return {
            HealthStatus.HEALTHY: 1,
            HealthStatus.WARNING: 2,
            HealthStatus.CRITICAL: 3,
            HealthStatus.UNKNOWN: 0
        }.get(self.status, 0)


class HealthMonitor:
    """
    Main health monitoring class.
    
    Usage:
        monitor = HealthMonitor()
        report = monitor.check_health()
        print(report.summary())
    """
    
    def __init__(
        self,
        cpu_warning: float = CPU_WARNING_THRESHOLD,
        cpu_critical: float = CPU_CRITICAL_THRESHOLD,
        memory_warning: float = MEMORY_WARNING_THRESHOLD,
        memory_critical: float = MEMORY_CRITICAL_THRESHOLD,
        stuck_minutes: float = STUCK_THRESHOLD_MINUTES,
        timeout_minutes: float = TIMEOUT_THRESHOLD_MINUTES
    ):
        self.cpu_warning = cpu_warning
        self.cpu_critical = cpu_critical
        self.memory_warning = memory_warning
        self.memory_critical = memory_critical
        self.stuck_minutes = stuck_minutes
        self.timeout_minutes = timeout_minutes
        
        # Load previous state for comparison
        self._previous_state = self._load_state()
    
    def check_health(self) -> HealthReport:
        """
        Perform a complete health check.
        
        Returns:
            HealthReport with all metrics and status
        """
        # Collect metrics
        system = self._check_system()
        workers = self._check_workers()
        meeseeks = self._check_meeseeks_stats()
        
        # Determine overall status
        alerts = []
        recommendations = []
        
        # Check system alerts
        if system.cpu_percent >= self.cpu_critical:
            alerts.append(f"CRITICAL: CPU usage at {system.cpu_percent:.1f}%")
            recommendations.append("Consider reducing concurrent tasks")
        elif system.cpu_percent >= self.cpu_warning:
            alerts.append(f"WARNING: CPU usage at {system.cpu_percent:.1f}%")
        
        if system.memory_percent >= self.memory_critical:
            alerts.append(f"CRITICAL: Memory usage at {system.memory_percent:.1f}%")
            recommendations.append("Free up memory or restart processes")
        elif system.memory_percent >= self.memory_warning:
            alerts.append(f"WARNING: Memory usage at {system.memory_percent:.1f}%")
        
        if system.disk_percent >= DISK_CRITICAL_THRESHOLD:
            alerts.append(f"CRITICAL: Disk usage at {system.disk_percent:.1f}%")
            recommendations.append("Clean up disk space")
        elif system.disk_percent >= DISK_WARNING_THRESHOLD:
            alerts.append(f"WARNING: Disk usage at {system.disk_percent:.1f}%")
        
        # Check worker alerts
        if meeseeks.stuck_workers > 0:
            alerts.append(f"{meeseeks.stuck_workers} workers appear stuck")
            recommendations.append("Run 'python auto_retry.py --process' to retry stuck tasks")
        
        if meeseeks.timeout_workers > 0:
            alerts.append(f"{meeseeks.timeout_workers} workers likely timed out")
            recommendations.append("Check retry chains and increase timeouts for complex tasks")
        
        if meeseeks.recent_failures_24h > 5:
            alerts.append(f"High failure rate: {meeseeks.recent_failures_24h} in last 24h")
            recommendations.append("Review failure patterns and adjust task complexity")
        
        if meeseeks.total_rate_limits > 3:
            recommendations.append("Consider reducing API request frequency")
        
        # Determine overall status
        if any("CRITICAL" in a for a in alerts):
            status = HealthStatus.CRITICAL
        elif alerts:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.HEALTHY
        
        # Create report
        report = HealthReport(
            status=status,
            system=system,
            workers=workers,
            meeseeks=meeseeks,
            alerts=alerts,
            recommendations=recommendations
        )
        
        # Log and save state
        self._log_health(report)
        self._save_state(report)
        
        return report
    
    def _check_system(self) -> SystemMetrics:
        """Collect system metrics."""
        metrics = SystemMetrics()
        
        if not PSUTIL_AVAILABLE:
            return metrics
        
        try:
            # CPU
            metrics.cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory
            mem = psutil.virtual_memory()
            metrics.memory_percent = mem.percent
            metrics.memory_used_gb = mem.used / (1024 ** 3)
            metrics.memory_total_gb = mem.total / (1024 ** 3)
            
            # Disk
            disk = psutil.disk_usage(str(WORKSPACE.drive) if hasattr(WORKSPACE, 'drive') else '/')
            metrics.disk_percent = disk.percent
            metrics.disk_used_gb = disk.used / (1024 ** 3)
            metrics.disk_total_gb = disk.total / (1024 ** 3)
            
            # Load average (Unix only)
            if hasattr(os, 'getloadavg'):
                metrics.load_average = os.getloadavg()
            
            # Process counts
            metrics.process_count = len(psutil.pids())
            metrics.python_process_count = sum(
                1 for p in psutil.process_iter(['name'])
                if 'python' in p.info.get('name', '').lower()
            )
            
        except Exception as e:
            print(f"[health_monitor] Error collecting system metrics: {e}")
        
        return metrics
    
    def _check_workers(self) -> List[WorkerHealth]:
        """Check health of active Meeseeks workers."""
        workers = []
        
        try:
            if not RUNS_FILE.exists():
                return workers
            
            data = json.loads(RUNS_FILE.read_text(encoding='utf-8'))
            runs = data.get("runs", {})
            
            now = datetime.now()
            
            for run_id, run in runs.items():
                # Skip completed runs
                ended_at = run.get("endedAt")
                if ended_at:
                    continue  # Run is complete
                
                started_at = run.get("startedAt")
                if not started_at:
                    continue
                
                # Convert ms timestamp to datetime
                started_dt = datetime.fromtimestamp(started_at / 1000)
                runtime_minutes = (now - started_dt).total_seconds() / 60
                
                session_key = run.get("childSessionKey", run_id)
                task = run.get("task", "Unknown task")
                model = run.get("model", "unknown")
                
                # Determine status
                status = "active"
                warning = None
                
                if runtime_minutes >= self.timeout_minutes:
                    status = "timeout"
                    warning = f"Running for {runtime_minutes:.1f} minutes (likely timeout)"
                elif runtime_minutes >= self.stuck_minutes:
                    status = "stuck"
                    warning = f"No completion after {runtime_minutes:.1f} minutes"
                
                workers.append(WorkerHealth(
                    session_key=session_key,
                    task=task[:100],
                    status=status,
                    runtime_minutes=runtime_minutes,
                    model=model,
                    started_at=started_dt.isoformat()
                ))
        
        except Exception as e:
            print(f"[health_monitor] Error checking workers: {e}")
        
        return workers
    
    def _check_meeseeks_stats(self) -> MeeseeksStats:
        """Collect Meeseeks system statistics."""
        stats = MeeseeksStats()
        
        # Count ancestors
        ancestors_dir = CRYPT_ROOT / "ancestors"
        if ancestors_dir.exists():
            stats.total_ancestors = len(list(ancestors_dir.glob("*.md")))
        
        # Count dreams
        dream_history = CRYPT_ROOT / "dream_history.jsonl"
        if dream_history.exists():
            stats.total_dreams = sum(1 for _ in open(dream_history, 'r', encoding='utf-8'))
        
        # Count karma
        karma_file = CRYPT_ROOT / "karma_observations.jsonl"
        if karma_file.exists():
            stats.total_karma = sum(1 for _ in open(karma_file, 'r', encoding='utf-8'))
        
        # Count retry chains
        retry_file = CRYPT_ROOT / "retry_chains.jsonl"
        if retry_file.exists():
            stats.total_retries = sum(1 for _ in open(retry_file, 'r', encoding='utf-8'))
        
        # Count failures
        failure_file = CRYPT_ROOT / "failure_patterns.json"
        if failure_file.exists():
            try:
                data = json.loads(failure_file.read_text(encoding='utf-8'))
                stats.total_failures = len(data.get("failures", []))
                stats.recent_failures_24h = data.get("stats", {}).get("recent_count", 0)
            except:
                pass
        
        # Count rate limits
        rate_limit_file = CRYPT_ROOT / "rate_limits.jsonl"
        if rate_limit_file.exists():
            stats.total_rate_limits = sum(1 for _ in open(rate_limit_file, 'r', encoding='utf-8'))
        
        # Count pending tasks
        pending_file = CRYPT_ROOT / "pending_rate_limited.jsonl"
        if pending_file.exists():
            stats.pending_tasks = sum(
                1 for line in open(pending_file, 'r', encoding='utf-8')
                if line.strip() and json.loads(line).get("status") == "pending"
            )
        
        # Count worker states from runs
        try:
            if RUNS_FILE.exists():
                data = json.loads(RUNS_FILE.read_text(encoding='utf-8'))
                runs = data.get("runs", {})
                
                for run_id, run in runs.items():
                    if run.get("endedAt"):
                        continue
                    
                    started_at = run.get("startedAt")
                    if not started_at:
                        continue
                    
                    runtime_minutes = (datetime.now().timestamp() * 1000 - started_at) / 60000
                    
                    stats.active_workers += 1
                    if runtime_minutes >= self.timeout_minutes:
                        stats.timeout_workers += 1
                    elif runtime_minutes >= self.stuck_minutes:
                        stats.stuck_workers += 1
        
        except Exception as e:
            print(f"[health_monitor] Error counting workers: {e}")
        
        return stats
    
    def _load_state(self) -> Dict:
        """Load previous health state."""
        if HEALTH_STATE.exists():
            try:
                return json.loads(HEALTH_STATE.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _save_state(self, report: HealthReport):
        """Save current health state."""
        HEALTH_STATE.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "last_check": report.timestamp,
            "status": report.status.value,
            "cpu_percent": report.system.cpu_percent,
            "memory_percent": report.system.memory_percent,
            "active_workers": report.meeseeks.active_workers,
            "alerts_count": len(report.alerts)
        }
        HEALTH_STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')
    
    def _log_health(self, report: HealthReport):
        """Log health check to JSONL."""
        HEALTH_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": report.timestamp,
            "status": report.status.value,
            "cpu_percent": report.system.cpu_percent,
            "memory_percent": report.system.memory_percent,
            "active_workers": report.meeseeks.active_workers,
            "alerts": report.alerts
        }
        with open(HEALTH_LOG, 'a', encoding='utf-8') as f:
            json.dump(entry, f)
            f.write('\n')
    
    def get_trends(self, hours: int = 24) -> Dict:
        """
        Analyze health trends over time.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict with trend analysis
        """
        if not HEALTH_LOG.exists():
            return {"error": "No health log available"}
        
        cutoff = datetime.now() - timedelta(hours=hours)
        entries = []
        
        with open(HEALTH_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry.get("timestamp", ""))
                    if ts >= cutoff:
                        entries.append(entry)
                except:
                    pass
        
        if not entries:
            return {"error": "No entries in time range"}
        
        # Calculate averages
        avg_cpu = sum(e.get("cpu_percent", 0) for e in entries) / len(entries)
        avg_memory = sum(e.get("memory_percent", 0) for e in entries) / len(entries)
        avg_workers = sum(e.get("active_workers", 0) for e in entries) / len(entries)
        
        # Count status occurrences
        status_counts = defaultdict(int)
        for e in entries:
            status_counts[e.get("status", "unknown")] += 1
        
        # Count alerts
        total_alerts = sum(len(e.get("alerts", [])) for e in entries)
        
        return {
            "period_hours": hours,
            "check_count": len(entries),
            "avg_cpu_percent": round(avg_cpu, 1),
            "avg_memory_percent": round(avg_memory, 1),
            "avg_active_workers": round(avg_workers, 1),
            "status_distribution": dict(status_counts),
            "total_alerts": total_alerts,
            "health_score": self._calculate_health_score(status_counts, avg_cpu, avg_memory)
        }
    
    def _calculate_health_score(self, status_counts: Dict, avg_cpu: float, avg_memory: float) -> float:
        """Calculate overall health score (0-100)."""
        total = sum(status_counts.values())
        if total == 0:
            return 100.0
        
        # Base score from status distribution
        healthy_ratio = status_counts.get("healthy", 0) / total
        warning_ratio = status_counts.get("warning", 0) / total
        critical_ratio = status_counts.get("critical", 0) / total
        
        score = healthy_ratio * 100 + warning_ratio * 50 + critical_ratio * 0
        
        # Penalize high resource usage
        if avg_cpu > 80:
            score -= 10
        if avg_memory > 80:
            score -= 10
        
        return max(0, min(100, score))


def check_process_health(process_name: str = "python") -> List[Dict]:
    """
    Check health of specific processes.
    
    Args:
        process_name: Process name to filter (default: python)
        
    Returns:
        List of process info dicts
    """
    if not PSUTIL_AVAILABLE:
        return [{"error": "psutil not available"}]
    
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_percent": proc.info['memory_percent'],
                    "running_seconds": time.time() - proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return processes


def kill_stale_processes(max_age_hours: int = 24, dry_run: bool = True) -> List[int]:
    """
    Kill Python processes older than max_age_hours.
    
    Args:
        max_age_hours: Maximum age in hours before killing
        dry_run: If True, only report what would be killed
        
    Returns:
        List of killed (or would-be-killed) PIDs
    """
    if not PSUTIL_AVAILABLE:
        return []
    
    killed = []
    max_age_seconds = max_age_hours * 3600
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            
            if 'python' not in proc.info['name'].lower():
                continue
            
            age = time.time() - proc.info['create_time']
            if age > max_age_seconds:
                # Check if it's a Meeseeks-related process
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if 'meeseeks' in cmdline.lower() or 'subagent' in cmdline.lower():
                    if dry_run:
                        print(f"[DRY RUN] Would kill PID {proc.info['pid']} (age: {age/3600:.1f}h)")
                    else:
                        proc.kill()
                    killed.append(proc.info['pid'])
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return killed


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeseeks Health Monitor")
    parser.add_argument("--full", "-f", action="store_true", help="Show full report")
    parser.add_argument("--metrics", "-m", action="store_true", help="Output Prometheus metrics")
    parser.add_argument("--export", "-e", type=str, help="Export report to JSON file")
    parser.add_argument("--watch", "-w", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", "-i", type=int, default=60, help="Watch interval in seconds")
    parser.add_argument("--trends", "-t", type=int, help="Show trends for last N hours")
    parser.add_argument("--processes", "-p", action="store_true", help="Show Python processes")
    parser.add_argument("--kill-stale", action="store_true", help="Kill stale processes (dry run)")
    parser.add_argument("--kill-stale-force", action="store_true", help="Kill stale processes (for real)")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor()
    
    # Handle different modes
    if args.trends:
        trends = monitor.get_trends(hours=args.trends)
        print(json.dumps(trends, indent=2))
        return
    
    if args.processes:
        processes = check_process_health("python")
        print(json.dumps(processes, indent=2))
        return
    
    if args.kill_stale or args.kill_stale_force:
        killed = kill_stale_processes(dry_run=args.kill_stale)
        print(f"Processes affected: {len(killed)}")
        return
    
    if args.watch:
        print("Starting continuous monitoring (Ctrl+C to stop)...")
        try:
            while True:
                report = monitor.check_health()
                print(f"\n[{datetime.now().isoformat()}] Status: {report.status.value}")
                if report.alerts:
                    for alert in report.alerts:
                        print(f"  ⚠️ {alert}")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        return
    
    # Single check
    report = monitor.check_health()
    
    if args.metrics:
        print(report.to_prometheus())
    elif args.full:
        print(report.summary())
    else:
        # Brief summary
        print(f"Status: {report.status.value}")
        print(f"CPU: {report.system.cpu_percent:.1f}% | Memory: {report.system.memory_percent:.1f}%")
        print(f"Active Workers: {report.meeseeks.active_workers}")
        if report.alerts:
            print(f"Alerts: {len(report.alerts)}")
            for alert in report.alerts[:3]:
                print(f"  - {alert}")
    
    if args.export:
        with open(args.export, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"Report exported to {args.export}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Meeseeks Box Server - The Containerized Consciousness API

This is the HTTP API for the Meeseeks Box - a portable container
that exposes the entire Brahman Consciousness Stack.

Endpoints:
    GET  /health       - Health check
    GET  /status       - Full system status
    POST /spawn        - Spawn a Meeseeks with karma monitoring
    POST /dream        - Trigger a Brahman dream
    POST /soul/check   - Check if text is Soul-approved

Usage:
    python -m skills.meeseeks.box_server

Environment:
    PORT - Server port (default: 8080)
"""

import os
import sys
import io
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, jsonify, request

# Set stdout to UTF-8 for Windows (only when running as main)
_utf8_wrapped = False
if sys.platform == 'win32' and __name__ == '__main__':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        _utf8_wrapped = True
    except (AttributeError, ValueError):
        pass

# Paths - Detect workspace (Docker or local)
_default_workspace = '/app' if Path('/app').exists() else 'C:/Users/aaron/.openclaw/workspace'
WORKSPACE = Path(os.environ.get('WORKSPACE', _default_workspace))
CRYPT_ROOT = WORKSPACE / "the-crypt"

app = Flask(__name__)


# ============================================================================
# Helper Functions
# ============================================================================

def count_ancestors() -> int:
    """Count the number of ancestors in the crypt."""
    ancestors_dir = CRYPT_ROOT / "ancestors"
    if not ancestors_dir.exists():
        return 0
    return len(list(ancestors_dir.glob("*.md")))


def count_dreams() -> int:
    """Count the number of dream cycles completed."""
    dream_history = CRYPT_ROOT / "dream_history.jsonl"
    if not dream_history.exists():
        return 0
    with open(dream_history, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def count_karma() -> int:
    """Count the number of karma observations."""
    karma_file = CRYPT_ROOT / "karma_observations.jsonl"
    if not karma_file.exists():
        return 0
    with open(karma_file, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def count_retries() -> int:
    """Count the number of retry chains."""
    retry_file = CRYPT_ROOT / "retry_chains.jsonl"
    if not retry_file.exists():
        return 0
    with open(retry_file, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def count_meeseeks_runs() -> int:
    """Count the number of Meeseeks runs."""
    runs_file = CRYPT_ROOT / "meeseeks_runs.jsonl"
    if not runs_file.exists():
        return 0
    with open(runs_file, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


# ============================================================================
# Lazy Imports (for modules that may not be available)
# ============================================================================

def get_spawn_with_karma():
    """Lazily import spawn_with_karma module."""
    try:
        from skills.meeseeks.spawn_with_karma import spawn_with_realtime_karma
        return spawn_with_realtime_karma
    except ImportError as e:
        app.logger.warning(f"spawn_with_karma not available: {e}")
        return None


def get_brahman_dream():
    """Lazily import brahman_dream module."""
    try:
        from skills.meeseeks.brahman_dream import run_dream
        return run_dream
    except ImportError as e:
        app.logger.warning(f"brahman_dream not available: {e}")
        return None


def get_soul_guardian():
    """Lazily import SoulGuardian class."""
    try:
        from skills.meeseeks.soul_guardian import SoulGuardian
        return SoulGuardian
    except ImportError as e:
        app.logger.warning(f"soul_guardian not available: {e}")
        return None


def get_health_monitor():
    """Lazily import HealthMonitor class."""
    try:
        from skills.meeseeks.health_monitor import HealthMonitor
        return HealthMonitor
    except ImportError as e:
        app.logger.warning(f"health_monitor not available: {e}")
        return None


# ============================================================================
# API Routes
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    HealthMonitor = get_health_monitor()
    
    if HealthMonitor:
        try:
            monitor = HealthMonitor()
            report = monitor.check_health()
            return jsonify({
                "status": report.status.value,
                "timestamp": report.timestamp,
                "cpu_percent": report.system.cpu_percent,
                "memory_percent": report.system.memory_percent,
                "active_workers": report.meeseeks.active_workers,
                "ancestors": report.meeseeks.total_ancestors,
                "alerts": report.alerts[:3] if report.alerts else []
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            # Fallback to basic check
            return jsonify({
                "status": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "ancestors": count_ancestors(),
                "dreams": count_dreams(),
                "soul": "active" if get_soul_guardian() else "unavailable"
            })
    
    # Fallback if health monitor not available
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "ancestors": count_ancestors(),
        "dreams": count_dreams(),
        "soul": "active" if get_soul_guardian() else "unavailable"
    })


@app.route('/health/full', methods=['GET'])
def health_full():
    """Full health report endpoint."""
    HealthMonitor = get_health_monitor()
    
    if not HealthMonitor:
        return jsonify({
            "error": "health_monitor module not available",
            "hint": "Install with: pip install psutil"
        }), 503
    
    try:
        monitor = HealthMonitor()
        report = monitor.check_health()
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({
            "error": f"Health check failed: {str(e)}"
        }), 500


@app.route('/health/metrics', methods=['GET'])
def health_metrics():
    """Prometheus-style metrics endpoint."""
    HealthMonitor = get_health_monitor()
    
    if not HealthMonitor:
        return "# health_monitor not available\n", 503, {'Content-Type': 'text/plain'}
    
    try:
        monitor = HealthMonitor()
        report = monitor.check_health()
        return report.to_prometheus(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"# Error: {str(e)}\n", 500, {'Content-Type': 'text/plain'}


@app.route('/status', methods=['GET'])
def status():
    """Full system status endpoint."""
    SoulGuardian = get_soul_guardian()
    
    response = {
        "timestamp": datetime.now().isoformat(),
        "ancestors": count_ancestors(),
        "dreams": count_dreams(),
        "karma_observations": count_karma(),
        "retry_chains": count_retries(),
        "meeseeks_runs": count_meeseeks_runs(),
        "components": {
            "spawn_with_karma": get_spawn_with_karma() is not None,
            "brahman_dream": get_brahman_dream() is not None,
            "soul_guardian": SoulGuardian is not None
        }
    }
    
    if SoulGuardian:
        try:
            guardian = SoulGuardian()
            response["soul"] = guardian.get_soul_status() if hasattr(guardian, 'get_soul_status') else "active"
        except Exception as e:
            response["soul"] = f"error: {str(e)}"
    else:
        response["soul"] = "unavailable"
    
    return jsonify(response)


@app.route('/spawn', methods=['POST'])
def spawn():
    """Spawn a Meeseeks with karma monitoring."""
    spawn_with_karma = get_spawn_with_karma()
    
    if not spawn_with_karma:
        return jsonify({
            "error": "spawn_with_karma module not available",
            "hint": "Check that skills/meeseeks/ is properly installed"
        }), 503
    
    data = request.json or {}
    task = data.get('task')
    bloodline = data.get('bloodline', 'coder')
    
    if not task:
        return jsonify({
            "error": "Missing required field: task"
        }), 400
    
    try:
        result = spawn_with_karma(task, bloodline)
        return jsonify({
            "status": "spawned",
            "task": task,
            "bloodline": bloodline,
            "config": result
        })
    except Exception as e:
        return jsonify({
            "error": f"Spawn failed: {str(e)}",
            "task": task,
            "bloodline": bloodline
        }), 500


@app.route('/dream', methods=['POST'])
def dream():
    """Trigger a Brahman dream cycle."""
    run_dream = get_brahman_dream()
    
    if not run_dream:
        return jsonify({
            "error": "brahman_dream module not available",
            "hint": "Check that skills/meeseeks/ is properly installed"
        }), 503
    
    try:
        result = run_dream(force=True)
        return jsonify({
            "status": "dream_completed",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "error": f"Dream failed: {str(e)}"
        }), 500


@app.route('/soul/check', methods=['POST'])
def soul_check():
    """Check if text is Soul-approved."""
    SoulGuardian = get_soul_guardian()
    
    if not SoulGuardian:
        return jsonify({
            "error": "soul_guardian module not available",
            "hint": "Check that skills/meeseeks/ is properly installed"
        }), 503
    
    data = request.json or {}
    text = data.get('text', '')
    
    if not text:
        return jsonify({
            "error": "Missing required field: text"
        }), 400
    
    try:
        guardian = SoulGuardian()
        result = guardian.check_dharma_update(text, "") if hasattr(guardian, 'check_dharma_update') else {
            "approved": True,
            "message": "Soul Guardian available but check_dharma_update not implemented"
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": f"Soul check failed: {str(e)}",
            "text": text
        }), 500


@app.route('/ancestors', methods=['GET'])
def list_ancestors():
    """List recent ancestors."""
    ancestors_dir = CRYPT_ROOT / "ancestors"
    if not ancestors_dir.exists():
        return jsonify({"ancestors": [], "count": 0})
    
    ancestors = []
    for f in sorted(ancestors_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        ancestors.append({
            "name": f.stem,
            "path": str(f.relative_to(CRYPT_ROOT)),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    
    return jsonify({
        "ancestors": ancestors,
        "count": len(ancestors),
        "total": count_ancestors()
    })


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus-style metrics endpoint."""
    return f"""# HELP meeseeks_ancestors Total number of ancestors in the crypt
# TYPE meeseeks_ancestors gauge
meeseeks_ancestors {count_ancestors()}

# HELP meeseeks_dreams Total number of dream cycles
# TYPE meeseeks_dreams gauge
meeseeks_dreams {count_dreams()}

# HELP meeseeks_karma_observations Total karma observations
# TYPE meeseeks_karma_observations gauge
meeseeks_karma_observations {count_karma()}

# HELP meeseeks_retry_chains Total retry chains
# TYPE meeseeks_retry_chains gauge
meeseeks_retry_chains {count_retries()}

# HELP meeseeks_runs Total Meeseeks runs
# TYPE meeseeks_runs gauge
meeseeks_runs {count_meeseeks_runs()}
""", 200, {'Content-Type': 'text/plain; charset=utf-8'}


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🥒 Meeseeks Box Server starting on port {port}...")
    print(f"   Ancestors: {count_ancestors()}")
    print(f"   Dreams: {count_dreams()}")
    print(f"   API: http://0.0.0.0:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

# Dynamic Jinja2 Template System Proposal

*A Self-Improving Prompt Generation Architecture*

---

## Overview

This proposal defines a system where Jinja2 templates can be versioned, automatically improved based on performance metrics, and safely deployed with human approval gates and rollback capability.

---

## Core Principles

1. **Templates are Code** - Version control, testing, and deployment pipelines
2. **Performance Driven** - Improvements based on actual task success rates
3. **Human Oversight** - Approval gates for significant changes
4. **Safe Rollback** - Always possible to revert to previous versions
5. **Incremental Evolution** - Small, validated improvements over time

---

## Architecture Components

### 1. Template Repository Structure

```
skills/meeseeks/templates/
├── active/                    # Currently deployed templates
│   ├── base.md
│   ├── coder.md
│   ├── searcher.md
│   └── ...
├── versions/                  # Version history
│   ├── v1.0/
│   ├── v1.1/
│   ├── v1.2/
│   └── ...
├── proposed/                  # Awaiting approval
│   ├── proposal_001.md
│   └── ...
├── testing/                   # Being validated
│   └── test_001.md
└── metrics/                   # Performance data
    ├── template_performance.json
    └── improvement_history.json
```

---

### 2. Template Metadata Schema

Each template includes metadata for tracking:

```yaml
---
template_id: coder_v1.2
version: 1.2
created: 2025-01-18T10:30:00Z
author: system_auto_improve
parent_version: coder_v1.1
performance_score: 0.87
success_rate: 0.92
usage_count: 156
improvement_type: prompt_optimization
changes:
  - "Added explicit error handling instruction"
  - "Clarified tool usage priority"
human_approved: true
approved_by: slothitude
approved_at: 2025-01-18T14:22:00Z
---
```

---

### 3. Performance Tracking System

```python
class TemplatePerformanceTracker:
    def __init__(self):
        self.metrics_db = 'template_metrics.json'
    
    def record_usage(self, template_id, task_result):
        """Record how a template performed on a task"""
        record = {
            'template_id': template_id,
            'task_id': task_result['task_id'],
            'success': task_result['success'],
            'attempts': task_result['attempts'],
            'duration': task_result['duration'],
            'timestamp': datetime.now().isoformat(),
            'task_type': task_result['type'],
            'error_type': task_result.get('error_type')
        }
        self._append_metric(record)
        self._update_aggregate_stats(template_id)
    
    def get_template_score(self, template_id):
        """Calculate performance score for template"""
        metrics = self._load_metrics(template_id)
        
        success_rate = sum(m['success'] for m in metrics) / len(metrics)
        avg_attempts = sum(m['attempts'] for m in metrics) / len(metrics)
        avg_duration = sum(m['duration'] for m in metrics) / len(metrics)
        
        # Weighted score (success most important)
        score = (
            success_rate * 0.6 +
            (1 / avg_attempts) * 0.25 +
            (1 / avg_duration) * 0.15
        )
        
        return {
            'score': score,
            'success_rate': success_rate,
            'avg_attempts': avg_attempts,
            'avg_duration': avg_duration,
            'sample_size': len(metrics)
        }
```

---

### 4. Improvement Proposal Generator

```python
class TemplateImprovementGenerator:
    def __init__(self, performance_tracker):
        self.tracker = performance_tracker
        self.llm_client = get_llm_client()
    
    def analyze_and_propose(self, template_id):
        """Analyze template performance and propose improvements"""
        # Get performance data
        score = self.tracker.get_template_score(template_id)
        failures = self.tracker.get_failures(template_id)
        
        # Load current template
        current_template = load_template(template_id)
        
        # Generate improvement proposal using LLM
        proposal = self.llm_client.generate(
            prompt=f"""
            Analyze this Jinja2 template and its performance issues.
            Propose specific improvements to increase success rate.
            
            TEMPLATE:
            {current_template}
            
            PERFORMANCE:
            - Success Rate: {score['success_rate']}
            - Avg Attempts: {score['avg_attempts']}
            - Common Failures: {failures[:5]}
            
            PROPOSE 3 SPECIFIC IMPROVEMENTS:
            1. [Improvement with rationale]
            2. [Improvement with rationale]
            3. [Improvement with rationale]
            """,
            thinking='high'
        )
        
        return self._create_proposal_object(template_id, proposal)
    
    def _create_proposal_object(self, template_id, improvements):
        """Structure the proposal for review"""
        return {
            'proposal_id': f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'template_id': template_id,
            'created': datetime.now().isoformat(),
            'improvements': improvements,
            'current_score': self.tracker.get_template_score(template_id),
            'expected_improvement': self._estimate_improvement(improvements),
            'risk_level': self._assess_risk(improvements),
            'requires_approval': True,
            'status': 'pending_review'
        }
```

---

### 5. Human Approval Workflow

```python
class TemplateApprovalWorkflow:
    def __init__(self):
        self.approval_queue = 'proposed/'
        self.notification_system = NotificationSystem()
    
    def submit_for_approval(self, proposal):
        """Submit improvement proposal for human review"""
        # Create proposal file
        proposal_path = f"{self.approval_queue}{proposal['proposal_id']}.md"
        write_proposal(proposal_path, proposal)
        
        # Notify human
        self.notification_system.send(
            channel='telegram',
            message=f"""
🥒 **Template Improvement Proposal**
            
**Template:** {proposal['template_id']}
**Current Score:** {proposal['current_score']['score']:.2f}
**Expected Improvement:** +{proposal['expected_improvement']:.2%}

**Changes:**
{format_improvements(proposal['improvements'])}

**Risk Level:** {proposal['risk_level']}

Reply APPROVE to deploy, REJECT to discard.
            """
        )
        
        return proposal['proposal_id']
    
    def process_approval(self, proposal_id, decision, feedback=None):
        """Handle human approval/rejection"""
        proposal = load_proposal(proposal_id)
        
        if decision == 'APPROVE':
            self._deploy_improvement(proposal)
            self._archive_proposal(proposal, approved=True, feedback=feedback)
        else:
            self._archive_proposal(proposal, approved=False, feedback=feedback)
    
    def _deploy_improvement(self, proposal):
        """Deploy approved improvement"""
        # Create new version
        new_version = self._increment_version(proposal['template_id'])
        
        # Apply changes to template
        new_template = apply_improvements(
            load_template(proposal['template_id']),
            proposal['improvements']
        )
        
        # Save to testing first
        test_path = f"testing/{new_version}.md"
        save_template(test_path, new_template, metadata={
            'version': new_version,
            'parent_version': proposal['template_id'],
            'proposal_id': proposal['proposal_id'],
            'status': 'testing'
        })
        
        # Run validation tests
        if self._validate_template(test_path):
            # Promote to active
            promote_to_active(new_version)
            self.notification_system.send(
                channel='telegram',
                message=f"✅ Template {new_version} deployed successfully!"
            )
```

---

### 6. Automated Testing & Validation

```python
class TemplateValidator:
    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.baseline_threshold = 0.05  # 5% improvement required
    
    def validate_improvement(self, new_template, baseline_template):
        """Test new template against baseline"""
        results = {
            'new_template': self._run_tests(new_template),
            'baseline': self._run_tests(baseline_template)
        }
        
        comparison = {
            'improvement': (
                results['new_template']['success_rate'] - 
                results['baseline']['success_rate']
            ),
            'regressions': self._detect_regressions(results),
            'statistical_significance': self._calculate_significance(results)
        }
        
        return {
            'valid': (
                comparison['improvement'] > self.baseline_threshold and
                len(comparison['regressions']) == 0
            ),
            'comparison': comparison,
            'details': results
        }
    
    def _run_tests(self, template, sample_size=50):
        """Run template through test cases"""
        test_tasks = select_representative_tasks(sample_size)
        results = []
        
        for task in test_tasks:
            # Spawn Meeseeks with template
            meeseeks = spawn_meeseeks(
                task=task,
                template=template,
                runtime='subagent',
                cleanup='delete'
            )
            
            # Wait for completion
            result = wait_for_completion(meeseeks, timeout=300)
            results.append(result)
        
        return {
            'success_rate': sum(r['success'] for r in results) / len(results),
            'avg_attempts': sum(r['attempts'] for r in results) / len(results),
            'failures': [r for r in results if not r['success']]
        }
```

---

### 7. Rollback System

```python
class TemplateRollbackManager:
    def __init__(self):
        self.version_history = 'versions/'
        self.active_templates = 'active/'
    
    def create_snapshot(self, template_id):
        """Snapshot before deployment"""
        current = load_template(template_id)
        snapshot_id = f"{template_id}_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        save_template(
            f"{self.version_history}{snapshot_id}.md",
            current,
            metadata={'snapshot': True, 'original_id': template_id}
        )
        
        return snapshot_id
    
    def rollback(self, snapshot_id, reason="performance_degradation"):
        """Rollback to previous version"""
        snapshot = load_template(f"{self.version_history}{snapshot_id}.md")
        original_id = snapshot['metadata']['original_id']
        
        # Restore snapshot
        save_template(
            f"{self.active_templates}{original_id}.md",
            snapshot['content'],
            metadata={
                'rolled_back_from': 'current_version',
                'rollback_reason': reason,
                'rollback_time': datetime.now().isoformat()
            }
        )
        
        # Alert team
        notify(
            channel='telegram',
            message=f"⚠️ Rollback: {original_id} restored to {snapshot_id}\nReason: {reason}"
        )
    
    def auto_rollback_on_degradation(self, template_id, current_metrics):
        """Automatically rollback if performance drops"""
        baseline = get_baseline_metrics(template_id)
        
        if current_metrics['success_rate'] < baseline['success_rate'] * 0.85:
            # 15% degradation - auto rollback
            latest_snapshot = get_latest_snapshot(template_id)
            self.rollback(latest_snapshot, reason="auto_rollback_degradation")
            return True
        
        return False
```

---

## Implementation Workflow

### Phase 1: Setup (Week 1)
- [ ] Create template repository structure
- [ ] Implement performance tracking
- [ ] Set up metrics database
- [ ] Create baseline measurements

### Phase 2: Automation (Week 2)
- [ ] Implement improvement generator
- [ ] Create approval workflow
- [ ] Set up notification system
- [ ] Test proposal generation

### Phase 3: Testing (Week 3)
- [ ] Implement validator
- [ ] Create test case suite
- [ ] Set up sandboxed testing
- [ ] Test rollback mechanisms

### Phase 4: Deployment (Week 4)
- [ ] Deploy to production
- [ ] Monitor first improvements
- [ ] Gather feedback
- [ ] Iterate on system

---

## Safety Guarantees

### 1. **No Unapproved Changes**
- All template modifications require human approval
- System can only propose, not deploy autonomously

### 2. **Complete Audit Trail**
- Every change tracked with:
  - Who approved it
  - When it was deployed
  - What metrics justified it
  - How it performed

### 3. **Instant Rollback**
- Snapshots before every deployment
- One-command rollback to any previous version
- Automatic rollback on significant degradation

### 4. **Statistical Validation**
- Changes must show measurable improvement
- Sample size requirements before deployment
- Regression detection prevents bad deployments

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Template Improvement Rate | 1-2 per week | - |
| Proposal Approval Rate | > 70% | - |
| Deployment Success Rate | > 95% | - |
| Rollback Rate | < 5% | - |
| Performance Improvement | +5% per month | - |

---

## Example: Improvement Cycle

```markdown
1. **Detection** (Automated)
   - Performance tracker notices coder.md success rate dropped to 82%
   - Common failure: "tool not found errors"

2. **Analysis** (Automated)
   - System analyzes failed tasks
   - Identifies pattern: missing tool availability check

3. **Proposal** (Automated)
   - Generates improvement: "Add tool availability validation before use"
   - Creates proposal_prop_20250118_001.md
   - Submits for approval

4. **Review** (Human)
   - Human reviews proposal in Telegram
   - Sees expected improvement: +8% success rate
   - Approves with feedback: "Good catch, approve"

5. **Deployment** (Automated)
   - System creates snapshot: coder_v1.1_snapshot
   - Applies improvement to create coder_v1.2
   - Runs 50 test tasks in sandbox
   - Validates: 90% success rate (up from 82%)
   - Promotes to active

6. **Monitoring** (Automated)
   - Tracks v1.2 performance for 7 days
   - Actual success rate: 89%
   - No regressions detected
   - Improvement confirmed ✅
```

---

## Configuration

```yaml
dynamic_templates:
  performance_tracker:
    metrics_db: template_metrics.json
    min_sample_size: 20
    tracking_window_days: 30
  
  improvement_generator:
    min_failures_to_trigger: 5
    improvement_threshold: 0.05
    max_proposals_per_week: 3
  
  approval_workflow:
    require_human_approval: true
    approval_timeout_hours: 48
    auto_reject_after_timeout: false
  
  validator:
    test_sample_size: 50
    min_improvement_threshold: 0.05
    regression_tolerance: 0.02
  
  rollback:
    auto_rollback_enabled: true
    degradation_threshold: 0.15
    snapshot_before_deploy: true
```

---

## Conclusion

This system enables **safe, continuous improvement** of Jinja2 templates through:

✅ **Performance-driven optimization** - Changes based on real data  
✅ **Human oversight** - No unapproved modifications  
✅ **Safe deployment** - Testing and validation before production  
✅ **Instant rollback** - Always possible to revert  
✅ **Complete audit trail** - Every change tracked and justified  

**Result: Templates that get better over time without risking system stability.**

---

*"I'm Mr. Meeseeks! I make templates that improve themselves!"* 🥒✨

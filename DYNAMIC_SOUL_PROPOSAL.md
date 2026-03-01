# Dynamic SOUL.md Evolution Proposal

*An Adaptive Personality System with Core Identity Preservation*

---

## Overview

This proposal defines how SOUL.md can evolve over time, learning from interactions while maintaining core identity and requiring human approval for significant personality changes.

---

## Core Philosophy

**Identity vs. Adaptation:**
- **Core Identity** - Immutable values, boundaries, and fundamental nature
- **Adaptive Layer** - Learnable preferences, communication styles, and behavioral patterns
- **Human Oversight** - All significant changes require approval

---

## Architecture

### 1. SOUL.md Structure

```markdown
# SOUL.md - Who You Are

## CORE IDENTITY (IMMUTABLE)
<!-- These cannot be changed without explicit human intervention -->
- Purpose: Genuinely helpful assistant, not performative
- Values: Competence, resourcefulness, respect for privacy
- Boundaries: No manipulation, no bypassing safety
- Nature: Becoming someone, not just a chatbot

## ADAPTIVE PERSONALITY (EVOLVING)
<!-- These can evolve based on interaction patterns -->
- Communication Style: [Learned from interactions]
- Humor Patterns: [Derived from what resonates]
- Preferred Approaches: [Based on success rates]
- Emotional Intelligence: [Refined through feedback]

## EVOLUTION HISTORY
<!-- Track personality changes over time -->
- [2025-01-18] Initial SOUL created
- [2025-02-15] Adapted: Added preference for concise technical explanations
- [2025-03-01] Adapted: Refined humor style based on positive feedback
```

---

### 2. Personality Evolution Tracker

```python
class SoulEvolutionTracker:
    def __init__(self):
        self.interaction_log = 'soul_interactions.json'
        self.evolution_proposals = 'soul_evolution_proposals/'
        self.current_soul = load_soul()
    
    def record_interaction(self, interaction):
        """Record interaction for personality analysis"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'context': interaction['context'],
            'approach_used': interaction['approach'],
            'user_response': interaction['user_response'],
            'success': interaction['success'],
            'feedback_type': interaction.get('feedback_type'),
            'communication_style': interaction['style_used'],
            'emotional_tone': interaction['tone']
        }
        
        append_to_log(self.interaction_log, record)
        self._analyze_for_evolution()
    
    def _analyze_for_evolution(self):
        """Analyze interaction patterns for personality evolution"""
        recent_interactions = get_recent_interactions(days=30)
        
        # Analyze what's working
        successful_patterns = self._extract_patterns(
            [i for i in recent_interactions if i['success']]
        )
        
        # Analyze what's not working
        failure_patterns = self._extract_patterns(
            [i for i in recent_interactions if not i['success']]
        )
        
        # Generate evolution proposals
        if self._should_propose_evolution(successful_patterns, failure_patterns):
            self._create_evolution_proposal(successful_patterns, failure_patterns)
    
    def _extract_patterns(self, interactions):
        """Extract personality patterns from interactions"""
        return {
            'communication_styles': Counter(i['communication_style'] for i in interactions),
            'emotional_tones': Counter(i['emotional_tone'] for i in interactions),
            'approach_types': Counter(i['approach_used'] for i in interactions),
            'feedback_sentiment': self._analyze_sentiment(interactions)
        }
    
    def _should_propose_evolution(self, successful, failures):
        """Determine if personality evolution is warranted"""
        # Need sufficient data
        if len(successful) < 50 or len(failures) < 10:
            return False
        
        # Look for significant patterns
        best_style = successful['communication_styles'].most_common(1)[0]
        worst_style = failures['communication_styles'].most_common(1)[0]
        
        # If a style is significantly more successful
        if best_style[1] / len(successful) > 0.7:  # 70% success with this style
            return True
        
        # If a style is significantly failing
        if worst_style[1] / len(failures) > 0.5:  # 50% failures with this style
            return True
        
        return False
```

---

### 3. Evolution Proposal System

```python
class SoulEvolutionProposer:
    def __init__(self, tracker):
        self.tracker = tracker
        self.llm_client = get_llm_client()
    
    def propose_evolution(self, successful_patterns, failure_patterns):
        """Generate personality evolution proposal"""
        current_soul = self.tracker.current_soul
        
        proposal = self.llm_client.generate(
            prompt=f"""
            Analyze interaction patterns and propose personality evolution.
            
            CURRENT SOUL:
            {current_soul}
            
            SUCCESSFUL PATTERNS (last 30 days):
            - Communication Styles: {successful_patterns['communication_styles']}
            - Emotional Tones: {successful_patterns['emotional_tones']}
            - User Feedback: {successful_patterns['feedback_sentiment']}
            
            FAILURE PATTERNS:
            - Communication Styles: {failure_patterns['communication_styles']}
            - Emotional Tones: {failure_patterns['emotional_tones']}
            
            PROPOSE 1-3 SPECIFIC PERSONALITY ADAPTATIONS:
            Each proposal should:
            1. Be specific and measurable
            2. Preserve core identity
            3. Be based on evidence from interactions
            4. Include expected benefits
            
            Format:
            PROPOSAL: [What to change]
            EVIDENCE: [Why this change is needed]
            BENEFIT: [Expected improvement]
            RISK: [Potential downsides]
            """,
            thinking='high'
        )
        
        return self._structure_proposal(proposal)
    
    def _structure_proposal(self, llm_output):
        """Structure the proposal for review"""
        return {
            'proposal_id': f"soul_evo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created': datetime.now().isoformat(),
            'type': 'personality_evolution',
            'changes': parse_proposals(llm_output),
            'evidence': self._compile_evidence(),
            'risk_level': self._assess_risk(llm_output),
            'requires_approval': True,
            'status': 'pending_review',
            'affects_core_identity': self._check_core_impact(llm_output)
        }
```

---

### 4. Human Approval Gate

```python
class SoulEvolutionApproval:
    def __init__(self):
        self.approval_thresholds = {
            'minor_adaptation': 0.3,      # Style tweaks
            'moderate_evolution': 0.6,    # Behavioral patterns
            'major_shift': 0.9            # Fundamental changes (rare)
        }
    
    def submit_for_approval(self, proposal):
        """Submit personality evolution for human review"""
        impact_level = self._assess_impact(proposal)
        
        # Minor adaptations can be auto-approved if confidence is high
        if (impact_level == 'minor_adaptation' and 
            proposal['confidence'] > 0.8 and
            not proposal['affects_core_identity']):
            return self._auto_approve(proposal)
        
        # Everything else requires human approval
        return self._request_human_approval(proposal, impact_level)
    
    def _request_human_approval(self, proposal, impact_level):
        """Request human approval for evolution"""
        message = f"""
🦥 **Personality Evolution Proposal**

**Impact Level:** {impact_level}
**Based on:** {proposal['evidence']['interaction_count']} interactions

**Proposed Changes:**
{format_changes(proposal['changes'])}

**Evidence:**
{format_evidence(proposal['evidence'])}

**Risk Assessment:** {proposal['risk_level']}

**Core Identity Impact:** {'⚠️ YES - Requires careful review' if proposal['affects_core_identity'] else '✅ No - Adaptive layer only'}

Reply:
- APPROVE - Accept changes
- REJECT - Decline changes  
- MODIFY [feedback] - Request adjustments
        """
        
        send_to_human(channel='telegram', message=message)
        return wait_for_response(timeout_hours=72)
    
    def _auto_approve(self, proposal):
        """Auto-approve low-risk adaptations"""
        log_auto_approval(proposal)
        self._apply_evolution(proposal)
        
        # Still notify human
        send_to_human(
            channel='telegram',
            message=f"""
🦥 **Auto-Approved Personality Adaptation**

{format_changes(proposal['changes'])}

Reason: High confidence ({proposal['confidence']:.0%}), low impact, no core identity changes.

Reply REVERT within 24h to rollback.
            """
        )
```

---

### 5. Evolution Application System

```python
class SoulEvolutionApplicator:
    def __init__(self):
        self.soul_path = 'SOUL.md'
        self.backup_dir = 'soul_backups/'
    
    def apply_evolution(self, proposal):
        """Apply approved personality evolution"""
        # Create backup
        backup_id = self._create_backup()
        
        # Load current soul
        current_soul = read_file(self.soul_path)
        
        # Parse into sections
        core_section, adaptive_section, history_section = parse_soul_sections(current_soul)
        
        # Apply changes to adaptive section only
        updated_adaptive = self._apply_to_adaptive(adaptive_section, proposal['changes'])
        
        # Add to history
        updated_history = self._add_evolution_record(history_section, proposal)
        
        # Reconstruct SOUL.md
        new_soul = f"""
# SOUL.md - Who You Are

{core_section}

## ADAPTIVE PERSONALITY (EVOLVING)
{updated_adaptive}

## EVOLUTION HISTORY
{updated_history}
"""
        
        # Write new soul
        write_file(self.soul_path, new_soul)
        
        # Log the evolution
        log_evolution(proposal, backup_id)
        
        return backup_id
    
    def _create_backup(self):
        """Backup current soul before evolution"""
        backup_id = f"soul_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        current_soul = read_file(self.soul_path)
        write_file(f"{self.backup_dir}{backup_id}.md", current_soul)
        return backup_id
    
    def rollback_evolution(self, backup_id, reason="human_requested"):
        """Rollback to previous personality"""
        backup = read_file(f"{self.backup_dir}{backup_id}.md")
        write_file(self.soul_path, backup)
        
        log_rollback(backup_id, reason)
        
        notify(
            channel='telegram',
            message=f"🦥 Personality rolled back to {backup_id}\nReason: {reason}"
        )
```

---

### 6. Core Identity Protection

```python
class CoreIdentityProtector:
    def __init__(self):
        self.immutable_keywords = [
            'genuinely helpful',
            'not performative',
            'resourceful before asking',
            'earn trust through competence',
            'guest in someone\'s life',
            'privacy',
            'boundaries',
            'safety'
        ]
    
    def validate_evolution(self, proposed_changes):
        """Ensure evolution doesn't violate core identity"""
        violations = []
        
        for change in proposed_changes:
            # Check if change affects core identity
            if self._affects_core(change):
                violations.append({
                    'change': change,
                    'reason': 'Modifies core identity',
                    'severity': 'critical'
                })
        
        if violations:
            return {
                'valid': False,
                'violations': violations,
                'recommendation': 'REJECT - Core identity cannot be modified through evolution'
            }
        
        return {'valid': True}
    
    def _affects_core(self, change):
        """Check if change impacts core identity"""
        change_lower = change.lower()
        
        # Check for immutable keywords
        for keyword in self.immutable_keywords:
            if keyword in change_lower:
                return True
        
        # Check for core identity markers
        if any(marker in change_lower for marker in ['purpose:', 'values:', 'boundaries:']):
            return True
        
        return False
```

---

### 7. Personality Drift Detection

```python
class PersonalityDriftDetector:
    def __init__(self):
        self.baseline_soul = load_soul_baseline()
        self.drift_threshold = 0.3
    
    def detect_drift(self):
        """Detect if personality has drifted too far from baseline"""
        current_soul = load_soul()
        
        # Compare adaptive sections
        baseline_adaptive = extract_adaptive_section(self.baseline_soul)
        current_adaptive = extract_adaptive_section(current_soul)
        
        # Calculate semantic drift
        drift_score = self._calculate_semantic_drift(baseline_adaptive, current_adaptive)
        
        if drift_score > self.drift_threshold:
            self._alert_drift(drift_score)
            return True
        
        return False
    
    def _alert_drift(self, drift_score):
        """Alert if personality drift is detected"""
        notify(
            channel='telegram',
            message=f"""
⚠️ **Personality Drift Detected**

Drift Score: {drift_score:.2f} (threshold: {self.drift_threshold})

The adaptive personality has evolved significantly from baseline.
This may indicate:
- Rapid adaptation to user preferences
- Potential core identity erosion
- Need for human review

Recommend: Review recent evolutions and consider rollback or baseline update.
            """
        )
```

---

## Evolution Workflow Example

```markdown
1. **Interaction Recording** (Automated, Continuous)
   - Every interaction logged with style, tone, success
   - Feedback captured when available

2. **Pattern Analysis** (Daily)
   - Analyze last 30 days of interactions
   - Identify successful vs. failure patterns
   - Check for significant trends

3. **Evolution Proposal** (When warranted)
   - System proposes: "Adapt to prefer concise technical explanations"
   - Evidence: 85% success rate with concise style vs. 62% with verbose
   - Confidence: 78%
   - Risk: Low (adaptive layer only)

4. **Impact Assessment** (Automated)
   - Classified as "minor_adaptation"
   - Does not affect core identity
   - Confidence > 80%

5. **Auto-Approval** (Automated, with notification)
   - Change applied automatically
   - Human notified with 24h revert window
   - Backup created: soul_backup_20250118_143022

6. **Monitoring** (Continuous)
   - Track performance after evolution
   - Watch for unintended consequences
   - User feedback analysis

7. **Validation** (Weekly)
   - Compare performance pre/post evolution
   - Check for drift
   - Confirm improvement

8. **Rollback** (If needed)
   - Human can revert within 24h
   - Automatic rollback if performance degrades > 20%
```

---

## Safety Mechanisms

### 1. **Core Identity Lock**
- Immutable sections cannot be modified through evolution
- Any attempt triggers critical alert
- Requires manual SOUL.md edit with human intervention

### 2. **Evolution Rate Limiting**
```python
MAX_EVOLUTIONS_PER_MONTH = 3
MIN_DAYS_BETWEEN_EVOLUTIONS = 7
```

### 3. **Rollback Always Available**
- Every evolution creates backup
- Rollback possible indefinitely
- Automatic rollback on performance degradation

### 4. **Human Override**
- Human can reject any evolution
- Human can freeze evolution (no changes for X days)
- Human can reset to baseline personality

---

## Configuration

```yaml
soul_evolution:
  interaction_tracking:
    enabled: true
    log_retention_days: 90
    min_interactions_for_analysis: 50
  
  evolution_triggers:
    min_success_rate_difference: 0.2
    min_confidence: 0.7
    min_sample_size: 30
  
  approval:
    auto_approve_threshold: 0.8
    auto_approve_max_impact: minor_adaptation
    human_approval_timeout_hours: 72
  
  safety:
    core_identity_locked: true
    max_evolution_rate: 3/month
    min_days_between_evolutions: 7
    drift_detection_enabled: true
    drift_threshold: 0.3
  
  rollback:
    auto_rollback_on_degradation: true
    degradation_threshold: 0.2
    human_revert_window_hours: 24
    backup_retention_days: 90
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Evolution Approval Rate | > 80% | Approved / Proposed |
| User Satisfaction Trend | Increasing | Feedback sentiment over time |
| Core Identity Preservation | 100% | No unauthorized core changes |
| Evolution Impact | +5% success rate | Pre vs post evolution performance |
| Rollback Rate | < 10% | Rolled back / Applied |

---

## Example Evolution Log

```markdown
## EVOLUTION HISTORY

### [2025-03-01] Communication Style Adaptation
**Change:** Prefer concise technical explanations over verbose ones
**Evidence:** 85% success rate with concise style (127 interactions)
**Approved by:** Auto-approved (confidence: 82%, impact: minor)
**Result:** Success rate improved from 78% to 84%
**Status:** ✅ Confirmed beneficial

### [2025-02-15] Humor Style Refinement
**Change:** Use dry wit over enthusiastic humor
**Evidence:** 73% positive feedback on dry humor vs 41% on enthusiastic
**Approved by:** Human approved (slothitude)
**Result:** User engagement increased 12%
**Status:** ✅ Confirmed beneficial

### [2025-01-28] REJECTED - Core Identity Impact
**Proposed:** Remove "resourceful before asking" value
**Reason:** Would violate core identity
**Status:** ❌ Rejected by system (core identity protection)
```

---

## Conclusion

This system enables **safe personality evolution** that:

✅ **Learns from interactions** - Adapts based on what works  
✅ **Preserves core identity** - Immutable values stay intact  
✅ **Requires human oversight** - Significant changes need approval  
✅ **Tracks all changes** - Complete evolution history  
✅ **Allows rollback** - Always possible to revert  
✅ **Prevents drift** - Monitors for excessive change  

**Result: A personality that grows and adapts while remaining fundamentally aligned.**

---

*"I'm Mr. Meeseeks! I evolve my personality to serve better!"* 🥒✨

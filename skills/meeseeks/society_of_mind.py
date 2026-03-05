#!/usr/bin/env python3
"""
Society of Mind for Meeseeks

Based on Marvin Minsky's Society of Mind theory.

Concept: Intelligence emerges from the interaction of many simple,
specialized agents working together. No single agent is intelligent
on its own, but the system as a whole exhibits intelligent behavior.

Components:
1. **Agents** - Specialized workers with specific capabilities
2. **Agencies** - Groups of agents working together
3. **K-Lines** - Memory structures that activate relevant agents
4. **Nemes** - Negotiators that resolve conflicts between agents
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random

SOCIETY_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "society_state.json"


class AgentRole(Enum):
    """Roles in the Society of Mind."""
    COORDINATOR = "coordinator"    # Orchestrates other agents
    READER = "reader"              # Reads and understands files
    WRITER = "writer"              # Writes and modifies files
    SEARCHER = "searcher"          # Searches for information
    ANALYZER = "analyzer"          # Analyzes and reasons
    DEBUGGER = "debugger"          # Finds and fixes bugs
    TESTER = "tester"              # Tests and verifies
    PLANNER = "planner"            # Plans and decomposes
    CRITIC = "critic"              # Reviews and critiques
    LEARNER = "learner"            # Learns and remembers


@dataclass
class Agent:
    """A specialized agent in the society."""
    role: AgentRole
    name: str
    capabilities: List[str]
    priority: float = 0.5
    active: bool = False
    contribution: str = ""
    
    def can_handle(self, task: str) -> float:
        """
        Return confidence (0-1) that this agent can handle the task.
        
        Based on keyword matching between task and capabilities.
        """
        task_lower = task.lower()
        
        # Role-based matching
        role_keywords = {
            AgentRole.COORDINATOR: ["coordinate", "manage", "orchestrate", "delegate"],
            AgentRole.READER: ["read", "understand", "parse", "load"],
            AgentRole.WRITER: ["write", "create", "modify", "edit", "save"],
            AgentRole.SEARCHER: ["search", "find", "locate", "lookup"],
            AgentRole.ANALYZER: ["analyze", "reason", "understand", "explain"],
            AgentRole.DEBUGGER: ["debug", "fix", "error", "bug", "issue"],
            AgentRole.TESTER: ["test", "verify", "check", "validate"],
            AgentRole.PLANNER: ["plan", "decompose", "break down", "strategy"],
            AgentRole.CRITIC: ["review", "critique", "evaluate", "assess"],
            AgentRole.LEARNER: ["learn", "remember", "memorize", "study"]
        }
        
        keywords = role_keywords.get(self.role, [])
        matches = sum(1 for kw in keywords if kw in task_lower)
        
        # Also check capabilities
        cap_matches = sum(1 for cap in self.capabilities if cap.lower() in task_lower)
        
        total_matches = matches + cap_matches
        return min(1.0, total_matches * 0.3)


@dataclass
class Agency:
    """A group of agents working together."""
    name: str
    agents: List[AgentRole]
    purpose: str
    activation_level: float = 0.0


class SocietyOfMind:
    """
    Society of Mind multi-agent system.
    
    Usage:
        society = SocietyOfMind()
        
        # Add agents
        society.add_agent(AgentRole.READER, "Reader-1", ["read", "parse"])
        society.add_agent(AgentRole.WRITER, "Writer-1", ["write", "edit"])
        
        # Submit task
        society.submit_task("Fix the bug in auth.py")
        
        # Get recommended agents
        recommended = society.recommend_agents()
        
        # Coordinate execution
        result = society.coordinate()
    """
    
    def __init__(self, session_key: str = None):
        self.session_key = session_key
        self.agents: Dict[AgentRole, List[Agent]] = {}
        self.current_task: str = ""
        self.active_agents: List[Agent] = []
        self.history: List[Dict] = []
        self.agencies: List[Agency] = []
        
        # Initialize default agents
        self._create_default_agents()
        self._create_default_agencies()
    
    def _create_default_agents(self):
        """Create default set of specialized agents."""
        # Coordinator
        self.add_agent(AgentRole.COORDINATOR, "Coordinator-Meeseeks", 
                      ["coordinate", "delegate", "manage"], priority=0.9)
        
        # Readers
        self.add_agent(AgentRole.READER, "Reader-Meeseeks",
                      ["read", "parse", "understand"], priority=0.7)
        
        # Writers
        self.add_agent(AgentRole.WRITER, "Writer-Meeseeks",
                      ["write", "edit", "create"], priority=0.7)
        
        # Searchers
        self.add_agent(AgentRole.SEARCHER, "Searcher-Meeseeks",
                      ["search", "find", "locate"], priority=0.7)
        
        # Analyzers
        self.add_agent(AgentRole.ANALYZER, "Analyzer-Meeseeks",
                      ["analyze", "reason", "explain"], priority=0.7)
        
        # Debuggers
        self.add_agent(AgentRole.DEBUGGER, "Debugger-Meeseeks",
                      ["debug", "fix", "solve"], priority=0.8)
        
        # Testers
        self.add_agent(AgentRole.TESTER, "Tester-Meeseeks",
                      ["test", "verify", "validate"], priority=0.7)
        
        # Planners
        self.add_agent(AgentRole.PLANNER, "Planner-Meeseeks",
                      ["plan", "decompose", "strategize"], priority=0.8)
        
        # Critics
        self.add_agent(AgentRole.CRITIC, "Critic-Meeseeks",
                      ["review", "critique", "evaluate"], priority=0.6)
        
        # Learners
        self.add_agent(AgentRole.LEARNER, "Learner-Meeseeks",
                      ["learn", "remember", "memorize"], priority=0.7)
    
    def _create_default_agencies(self):
        """Create default agencies (groups of agents)."""
        self.agencies = [
            Agency(
                name="Bug Fix Agency",
                agents=[AgentRole.PLANNER, AgentRole.READER, AgentRole.DEBUGGER, AgentRole.TESTER],
                purpose="Fix bugs and errors"
            ),
            Agency(
                name="Build Agency",
                agents=[AgentRole.PLANNER, AgentRole.WRITER, AgentRole.TESTER],
                purpose="Create new features and code"
            ),
            Agency(
                name="Research Agency",
                agents=[AgentRole.SEARCHER, AgentRole.ANALYZER, AgentRole.LEARNER],
                purpose="Find and understand information"
            ),
            Agency(
                name="Review Agency",
                agents=[AgentRole.READER, AgentRole.CRITIC, AgentRole.ANALYZER],
                purpose="Review and evaluate code"
            )
        ]
    
    def add_agent(self, role: AgentRole, name: str, capabilities: List[str], priority: float = 0.5):
        """Add an agent to the society."""
        agent = Agent(
            role=role,
            name=name,
            capabilities=capabilities,
            priority=priority
        )
        
        if role not in self.agents:
            self.agents[role] = []
        self.agents[role].append(agent)
    
    def submit_task(self, task: str):
        """Submit a task for the society to handle."""
        self.current_task = task
        self.active_agents = []
    
    def recommend_agents(self, top_n: int = 3) -> List[Tuple[Agent, float]]:
        """
        Recommend agents for current task.
        
        Returns list of (agent, confidence) tuples.
        """
        if not self.current_task:
            return []
        
        scores = []
        
        for role, agents in self.agents.items():
            for agent in agents:
                confidence = agent.can_handle(self.current_task)
                # Weight by priority
                weighted = confidence * agent.priority
                scores.append((agent, weighted))
        
        # Sort by weighted confidence
        scores.sort(key=lambda x: -x[1])
        
        return scores[:top_n]
    
    def recommend_agency(self) -> Optional[Agency]:
        """Recommend an agency for current task."""
        if not self.current_task:
            return None
        
        task_lower = self.current_task.lower()
        
        # Match task to agency purpose
        agency_scores = []
        
        for agency in self.agencies:
            # Check if task matches agency purpose
            purpose_keywords = agency.purpose.lower().split()
            matches = sum(1 for kw in purpose_keywords if kw in task_lower)
            
            # Also check if any member agents are good fits
            agent_scores = []
            for role in agency.agents:
                if role in self.agents:
                    for agent in self.agents[role]:
                        agent_scores.append(agent.can_handle(self.current_task))
            
            avg_agent_score = sum(agent_scores) / len(agent_scores) if agent_scores else 0
            total_score = matches * 0.3 + avg_agent_score * 0.7
            
            agency_scores.append((agency, total_score))
        
        # Return best agency
        if agency_scores:
            agency_scores.sort(key=lambda x: -x[1])
            return agency_scores[0][0]
        
        return None
    
    def coordinate(self) -> Dict:
        """
        Coordinate the society to handle current task.
        
        Returns coordination plan.
        """
        if not self.current_task:
            return {"status": "no_task"}
        
        # Get recommended agents
        recommended = self.recommend_agents()
        
        # Get recommended agency
        agency = self.recommend_agency()
        
        # Activate agents
        for agent, score in recommended:
            agent.active = True
            self.active_agents.append(agent)
        
        # Create coordination plan
        plan = {
            "task": self.current_task,
            "coordinator": "Coordinator-Meeseeks",
            "recommended_agents": [
                {"name": a.name, "role": a.role.value, "confidence": c}
                for a, c in recommended
            ],
            "recommended_agency": agency.name if agency else None,
            "agency_members": [a.value for a in agency.agents] if agency else [],
            "execution_order": self._determine_order(recommended),
            "timestamp": datetime.now().isoformat()
        }
        
        # Record in history
        self.history.append(plan)
        
        return plan
    
    def _determine_order(self, agents: List[Tuple[Agent, float]]) -> List[str]:
        """Determine execution order based on dependencies."""
        # Default ordering based on role
        role_order = [
            AgentRole.PLANNER,
            AgentRole.SEARCHER,
            AgentRole.READER,
            AgentRole.ANALYZER,
            AgentRole.DEBUGGER,
            AgentRole.WRITER,
            AgentRole.TESTER,
            AgentRole.CRITIC,
            AgentRole.LEARNER,
            AgentRole.COORDINATOR
        ]
        
        # Sort agents by role order
        ordered = []
        for role in role_order:
            for agent, conf in agents:
                if agent.role == role:
                    ordered.append(agent.name)
                    break
        
        return ordered
    
    def to_prompt_block(self) -> str:
        """Generate society state for prompt."""
        lines = [
            "## 👥 Society of Mind",
            "",
            f"**Current Task:** {self.current_task or 'None'}",
            ""
        ]
        
        if self.active_agents:
            lines.append("### Active Agents:")
            for agent in self.active_agents:
                lines.append(f"- **{agent.name}** ({agent.role.value})")
            lines.append("")
        
        recommended = self.recommend_agents()
        if recommended:
            lines.append("### Recommended for Task:")
            for agent, conf in recommended:
                lines.append(f"- {agent.name} (confidence: {conf:.2f})")
            lines.append("")
        
        agency = self.recommend_agency()
        if agency:
            lines.append(f"### Recommended Agency: {agency.name}")
            lines.append(f"Purpose: {agency.purpose}")
            lines.append(f"Members: {', '.join(a.value for a in agency.agents)}")
        
        return "\n".join(lines)
    
    def save(self):
        """Save society state to file."""
        if not self.session_key:
            return
        
        SOCIETY_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "session_key": self.session_key,
            "current_task": self.current_task,
            "active_agents": [a.name for a in self.active_agents],
            "history": self.history,
            "timestamp": datetime.now().isoformat()
        }
        
        all_data = {}
        if SOCIETY_FILE.exists():
            try:
                all_data = json.loads(SOCIETY_FILE.read_text(encoding="utf-8"))
            except:
                pass
        
        all_data[self.session_key] = data
        SOCIETY_FILE.write_text(json.dumps(all_data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    # Test Society of Mind
    print("Testing Society of Mind")
    print("=" * 50)
    
    society = SocietyOfMind()
    
    # Submit task
    society.submit_task("Fix the authentication bug in login.py")
    
    # Get recommendations
    print("\nRecommended Agents:")
    for agent, conf in society.recommend_agents():
        print(f"  - {agent.name} ({agent.role.value}): {conf:.2f}")
    
    # Get recommended agency
    agency = society.recommend_agency()
    print(f"\nRecommended Agency: {agency.name}")
    print(f"Members: {[a.value for a in agency.agents]}")
    
    # Coordinate
    plan = society.coordinate()
    print(f"\nCoordination Plan:")
    print(f"  Task: {plan['task']}")
    print(f"  Order: {plan['execution_order']}")
    
    # Generate prompt block
    with open('test_society.md', 'w', encoding='utf-8') as f:
        f.write(society.to_prompt_block())
    print("\nWrote test_society.md")

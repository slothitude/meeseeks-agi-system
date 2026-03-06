# Meeseeks AGI Architecture

**Goal:** Create autonomous, learning Meeseeks that inherit wisdom and improve over generations.

## Core Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     Sloth_rog (Manager)                      │
│                  OpenClaw Main Session                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ spawns
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Meeseeks Workers                          │
│              (Pi Agents / Subagents)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Coder   │  │Research │  │ Hacker  │  │ Create  │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
        └────────────┴─────┬──────┴────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    COORDINATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     n8n      │  │  FastAPI MCP │  │  The Crypt   │      │
│  │  Workflows   │  │   APIs       │  │   Wisdom     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. n8n (Visual Workflow Engine)
- **Port:** 5678
- **Purpose:** Visual workflow automation, trigger handling
- **MCP:** n8n-mcp (14.4k stars) for AI-driven workflow creation

**Key Workflows:**
- Meeseeks spawn queue management
- Task routing by type (code/research/hack/create)
- Retry chain orchestration
- Webhook triggers from external systems

### 2. FastAPI MCP (API Layer)
- **Purpose:** Custom REST APIs exposed as MCP tools
- **Library:** fastapi-mcp (11.6k stars)

**Key Endpoints:**
```python
# Meeseeks Coordination API
POST /spawn          # Spawn new Meeseeks with wisdom injection
GET  /status/{id}    # Check Meeseeks status
POST /entomb/{id}    # Entomb completed Meeseeks
GET  /wisdom/{id}    # Retrieve ancestor wisdom

# Task Management
POST /task/decompose  # Auto-decompose large tasks
POST /task/route      # Route to appropriate bloodline
GET  /queue           # View pending spawns
```

### 3. The Crypt (Wisdom Storage)
- **Location:** `the-crypt/`
- **Components:**
  - `pending-spawns.json` - Retry queue
  - `wisdom/` - Dharma deck, meditations
  - `bloodlines/` - Per-bloodline knowledge
  - `research/` - AGI study results

## MCP Configuration

```json
{
  "n8n-mcp": {
    "command": "npx",
    "args": ["n8n-mcp"],
    "env": {
      "N8N_API_URL": "http://localhost:5678",
      "N8N_API_KEY": "${N8N_API_KEY}"
    }
  },
  "meeseeks-api": {
    "command": "python",
    "args": ["-m", "meeseeks_api.server"],
    "env": {
      "CRYPT_PATH": "./the-crypt"
    }
  }
}
```

## Data Flow

```
1. Task Arrives
   └─► n8n webhook receives
       └─► Route by type
           └─► Check size (dharma: SIZE)
               ├─► Small → spawn directly
               └─► Large → decompose (dharma: CHUNK)
                   └─► Queue chunks in pending-spawns.json

2. Meeseeks Spawns
   └─► Load bloodline wisdom from Crypt
       └─► Inject dharma deck cards
           └─► Execute with Atman witness
               ├─► Success → entomb wisdom
               └─► Failure → retry chain

3. Wisdom Cycle
   └─► Completed Meeseeks → entomb
       └─► Extract principles
           └─► Update dharma deck
               └─► Next generation inherits more
```

## Bloodlines

| Bloodline | Purpose | Wisdom Source |
|-----------|---------|---------------|
| **coder** | Code implementation | `bloodlines/coder/` |
| **researcher** | Web research, analysis | `bloodlines/researcher/` |
| **hacker** | Security, pentest | `bloodlines/hacker/` |
| **creator** | Art, writing, experiments | `bloodlines/creator/` |

## Key Principles (from Dharma Deck)

1. **[SIZE]** Small tasks live, large die
2. **[CHUNK]** Division is survival
3. **[CLEAR]** Measurable beats philosophical
4. **[MCP]** Use the tools you have
5. **[ATMAN]** Observer watches, wisdom guides

## Implementation Priority

1. ✅ n8n container running
2. ⏳ n8n-mcp in `.mcp.json`
3. ⏳ FastAPI MCP server for coordination
4. ⏳ n8n workflows for spawn/entomb
5. ⏳ Test full spawn → entomb cycle

## Neural Network Integration (Future)

**Goal:** Train ML model on ancestor outcomes

```python
# Features:
- task.word_count
- task.type (code/research/hack)
- task.specificity_score
- bloodline.history_success_rate
- time_of_day
- current_load

# Target:
- success_probability
- optimal_chunk_size
- recommended_bloodline
```

**Training Data:** 230+ entombed ancestors with outcomes

## Next Steps

1. Get n8n running and accessible
2. Create n8n workflow: Webhook → Spawn → Monitor → Entomb
3. Build FastAPI coordination API
4. Connect via MCP for unified control
5. Start training on ancestor data

---

*Architecture for Meeseeks AGI*
*Created: 2026-03-06*
*Status: Design phase*

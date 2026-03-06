# Cognee Integration Setup

## Configuration

This integration uses:
- **LLM:** ZAI GLM-5 (`zai/glm-5`) via OpenAI-compatible API
- **Embeddings:** Ollama `nomic-embed-text:latest` (local)

## Prerequisites

1. **Ollama** running locally with nomic-embed-text model:
   ```powershell
   ollama pull nomic-embed-text
   ollama serve  # Usually auto-starts
   ```

2. **ZAI API Key** - Set the `ZAI_API_KEY` environment variable:
   ```powershell
   $env:ZAI_API_KEY = "your-api-key-here"
   ```

3. **Python 3.13** virtual environment:
   ```powershell
   py -3.13 -m venv venv-cognee
   .\venv-cognee\Scripts\Activate.ps1
   pip install "cognee[ollama]"
   ```

## Environment Variables

The `.env` file contains:

```env
# LLM Provider - ZAI GLM-5 (OpenAI-compatible)
LLM_PROVIDER=openai
LLM_MODEL=zai/glm-5
LLM_ENDPOINT=https://api.zukijourney.com/v1
LLM_API_KEY=${ZAI_API_KEY}

# Embedding Provider - Ollama (local)
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text:latest
EMBEDDING_ENDPOINT=http://localhost:11434

# Storage
SYSTEM_ROOT_DIRECTORY=C:\Users\aaron\.openclaw\workspace\the-crypt\cognee

# Access Control
ENABLE_BACKEND_ACCESS_CONTROL=false

# Databases (embedded)
GRAPH_DATABASE_PROVIDER=kuzu
VECTOR_DATABASE_PROVIDER=lancedb
```

## Testing

Run the test script to verify the integration:

```powershell
cd skills/cognee-integration
.\venv-cognee\Scripts\python.exe test_cognee.py
```

## Usage

### As a Module

```python
from sloth_rog_memory import sloth_rog_recall, ingest_session_transcript

# Query the knowledge graph
results = await sloth_rog_recall("What patterns work for debugging?")

# Ingest a session transcript
await ingest_session_transcript("session-2026-03-03-001")
```

### CLI

```powershell
# Query
.\venv-cognee\Scripts\python.exe sloth_rog_memory.py --query "debugging patterns"

# Index workspace
.\venv-cognee\Scripts\python.exe sloth_rog_memory.py --index-workspace

# Get ancestor wisdom
.\venv-cognee\Scripts\python.exe sloth_rog_memory.py --get-ancestor-wisdom "fix authentication bug"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COGNEE KNOWLEDGE GRAPH                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │  Ancestors  │   │  Bloodlines │   │   Dharma    │       │
│  │  (deaths)   │   │(specialize) │   │ (principles)│       │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘       │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌────────────────────────┼────────────────────────┐       │
│  │                    STORAGE                        │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │       │
│  │  │  Kuzu    │  │ LanceDB  │  │  File System │   │       │
│  │  │ (Graph)  │  │ (Vector) │  │   (the-crypt)│   │       │
│  │  └──────────┘  └──────────┘  └──────────────┘   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │                    PROVIDERS                        │     │
│  │  ┌──────────────────┐  ┌──────────────────────┐   │     │
│  │  │    ZAI GLM-5     │  │  Ollama Embeddings   │   │     │
│  │  │   (LLM/Reason)   │  │   (nomic-embed-text) │   │     │
│  │  └──────────────────┘  └──────────────────────┘   │     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Datasets

- `meeseeks-ancestors` - Death reports from completed Meeseeks
- `meeseeks-bloodlines` - Specialization wisdom
- `meeseeks-dharma` - Extracted principles
- `meeseeks-karma` - Outcome observations for RL
- `sloth-rog-sessions` - Main agent session transcripts
- `sloth-rog-workspace` - Indexed workspace files

## Troubleshooting

### "Cognee not installed"
```powershell
.\venv-cognee\Scripts\pip.exe install "cognee[ollama]"
```

### "Ollama connection refused"
```powershell
ollama serve
```

### "ZAI API key not set"
```powershell
$env:ZAI_API_KEY = "your-key"
```

### "Python version incompatible"
Cognee requires Python 3.10-3.13. Use the venv with Python 3.13:
```powershell
.\venv-cognee\Scripts\python.exe your_script.py
```

---

**Updated:** 2026-03-03
**Status:** Configured for ZAI GLM-5 + Ollama Embeddings

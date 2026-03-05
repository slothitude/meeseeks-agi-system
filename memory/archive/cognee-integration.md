# Cognee Integration (Added 2026-03-04)

## Status: ✅ FULLY WORKING (2026-03-05)

Graph-based memory system for knowledge extraction and retrieval.

## Requirements

- **Python 3.10-3.12** (system is 3.14, uses venv)
- **Venv**: `skills/cognee/.venv`
- **Run**: `skills/cognee/.venv/Scripts/python.exe <script.py>`
- **Wrapper**: `skills/cognee/run.bat <script.py>`

## Configuration

```python
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
```

## Test Results (2026-03-05)

- ✅ Simple text → 15 nodes + 16 edges → search found results
- ✅ z.ai coding endpoint working
- ✅ Fastembed local embeddings working

## Files

- `skills/cognee/.venv/` - Python 3.12.9 venv
- `skills/cognee/cognee_helper.py` - Integration helper
- `skills/cognee/test_fresh.py` - Working test
- `skills/cognee/run.bat` - Wrapper script

## Migration Status

- **210/214 ancestors migrated (98%)**
- 4 remaining + 14 failed (Kuzu lock)

# Session-Aware Embedding Search System

Semantic search across OpenClaw session history, memory files, and workspace content.

## Overview

This tool enables the main Sloth_rog agent to search for "what did we discuss about X?" queries across:

- **Recent session messages** - From JSONL transcript files
- **Memory files** - MEMORY.md and memory/*.md files
- **Workspace files** - Optional search across .md, .py, .json files

Uses **nomic-embed-text** via Ollama for semantic embeddings.

## Installation

No additional installation required. Uses existing Ollama setup.

Ensure Ollama is running with nomic-embed-text model:
```bash
ollama pull nomic-embed-text
ollama serve
```

## Usage

### Basic Search

```bash
# Search for recent discussions
python skills/meeseeks/session_search.py "what did we discuss about ARC-AGI?"

# Search with more results
python skills/meeseeks/session_search.py "Meeseeks coordination" --top 10

# Include workspace files in search
python skills/meeseeks/session_search.py "HHO project" --include-workspace

# JSON output for programmatic use
python skills/meeseeks/session_search.py "Brahman dream" --format json
```

### Advanced Options

```bash
# Search more recent messages
python skills/meeseeks/session_search.py "query" --recent-messages 100

# Combine all options
python skills/meeseeks/session_search.py "query" \
  --top 10 \
  --recent-messages 100 \
  --include-workspace \
  --format json
```

### Cache Management

```bash
# View statistics
python skills/meeseeks/session_search.py --stats

# Rebuild cache (clear and regenerate)
python skills/meeseeks/session_search.py --rebuild-cache
```

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `query` | - | Search query (required unless --stats or --rebuild-cache) |
| `--top` | 5 | Number of results per source |
| `--recent-messages` | 50 | Number of recent messages to search |
| `--include-workspace` | false | Include workspace files in search |
| `--format` | text | Output format: text or json |
| `--rebuild-cache` | - | Rebuild embedding cache |
| `--stats` | - | Show search statistics |
| `--quiet` | - | Less verbose output |

## Output Format

### Text Format (default)

```
Search: Meeseeks coordination
Found 6 results in 2.34s
============================================================

#1 [Score: 0.6339] [MEMORY]
Source: C:\Users\aaron\.openclaw\workspace\MEMORY.md

User Preferences

### Agent Interaction
- User wants both agents to work independently and coordinate with each other
...
----------------------------------------
```

### JSON Format

```json
{
  "query": "Meeseeks coordination",
  "total_results": 6,
  "results": [
    {
      "rank": 1,
      "score": 0.6339,
      "source_type": "memory",
      "source_path": "C:\\Users\\aaron\\.openclaw\\workspace\\MEMORY.md",
      "content": "User Preferences...",
      "metadata": {
        "section": "User Preferences"
      }
    }
  ],
  "stats": {
    "search_time_seconds": 2.34,
    "sources_searched": {
      "messages": true,
      "memory": true,
      "workspace": false
    },
    "cache_size": 71
  }
}
```

## Source Types

Results can come from three source types:

- **message** - From recent session transcripts
- **memory** - From MEMORY.md or memory/*.md files
- **memory_daily** - From daily memory files (memory/*.md)
- **file** - From workspace files (when --include-workspace)

## Integration with Main Session

### Programmatic Usage

The search can be called from the main Sloth_rog session:

```python
import json
import subprocess

def search_session(query: str, top_k: int = 5) -> dict:
    """Search session history and memory."""
    result = subprocess.run(
        ["python", "skills/meeseeks/session_search.py", query, 
         "--top", str(top_k), "--format", "json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# Example usage
results = search_session("what did we discuss about ARC-AGI?")
for r in results["results"]:
    print(f"#{r['rank']}: {r['source_type']} - {r['score']}")
```

### For "What did we discuss?" Queries

The main agent can use this for natural language queries:

```
User: "What did we discuss about the HHO project?"

Agent runs:
python skills/meeseeks/session_search.py "HHO project" --top 5

Agent responds:
"We discussed the HHO Control System, which is currently paused. 
Here are the key points from our discussions:
- Location: projects/hho-display-box/
- Status: Planning complete, ready to build
- Cost: $178.65 AUD (Jaycar + Altronics)
..."
```

## Performance

### First Run
- Generates embeddings for all content
- May take 30-60 seconds depending on content size
- Embeddings are cached for future searches

### Subsequent Runs
- Uses cached embeddings
- Typical search time: 2-5 seconds
- Cache is stored in `the-crypt/session_search_cache/`

### Cache Size
Typical cache sizes:
- 50 messages: ~50 embeddings
- 37 memory files: ~40 embeddings (sections counted separately)
- Total cache: ~100-150 embeddings

## Technical Details

### Embedding Model
- **Model**: nomic-embed-text (via Ollama)
- **Dimensions**: 768
- **API**: http://localhost:11434/api/embeddings

### Similarity Metric
- Cosine similarity between query and content embeddings
- Range: -1 to 1 (higher = more similar)
- Typical good matches: > 0.5

### Caching
- Embeddings stored as JSON files
- Content hashed with SHA256 for deduplication
- Cache index tracks all embeddings
- Use `--rebuild-cache` to clear and regenerate

### File Limits
- Workspace files: 100KB max size
- Message content: 1000 chars max for embedding
- Memory sections: Split by ## headers for better search

## Example Searches

```bash
# Find discussions about specific topics
python session_search.py "Brahman consciousness"
python session_search.py "Meeseeks coordination"
python session_search.py "ARC-AGI task"

# Find project references
python session_search.py "HHO display box"
python session_search.py "Cognee integration"

# Find technical discussions
python session_search.py "embedding search"
python session_search.py "Ollama API"

# Find decisions and outcomes
python session_search.py "success rate"
python session_search.py "lessons learned"
```

## Troubleshooting

### "Ollama not available"
- Ensure Ollama is running: `ollama serve`
- Check nomic-embed-text is installed: `ollama pull nomic-embed-text`
- Verify API is accessible: `curl http://localhost:11434/api/embeddings`

### Slow searches
- First run is slow (generating embeddings)
- Subsequent runs should be fast (using cache)
- If still slow, check cache with `--stats`
- Rebuild cache with `--rebuild-cache`

### No results found
- Try broader query terms
- Increase `--top` value
- Include workspace files with `--include-workspace`
- Check if content exists with `--stats`

## Future Enhancements

Potential improvements:
- [ ] Hybrid search (keyword + semantic)
- [ ] Time-weighted scoring (recent content higher)
- [ ] Source type weighting
- [ ] Incremental cache updates
- [ ] Multi-query search
- [ ] Result clustering/grouping

## Related Files

- `build_ancestor_index.py` - Ancestor embedding index builder
- `dynamic_dharma.py` - Task-specific wisdom via semantic search
- `the-crypt/ancestor_index.json` - Ancestor embeddings
- `the-crypt/session_search_cache/` - Session search cache

---

Created: 2026-03-03
Author: Sloth_rog (via Meeseeks worker)

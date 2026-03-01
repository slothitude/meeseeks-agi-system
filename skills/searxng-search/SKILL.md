---
name: searxng-search
description: Use SearXNG as the primary search engine for Meeseeks. Fast, local, no API keys.
---

# 🔍 SearXNG Search Skill

## Overview

SearXNG is a local metasearch engine that aggregates results from multiple sources (Google, Bing, Brave, DuckDuckGo, Wikipedia, etc.). It provides a JSON API with no rate limits, no API keys, and complete privacy.

**Endpoint:** `http://localhost:8888/search?q=<query>&format=json`

## Why SearXNG?

| Feature | SearXNG | DuckDuckGo MCP | Brave API |
|---------|---------|----------------|-----------|
| **Speed** | < 1s | 10-30s | 5-15s |
| **API Key** | ❌ None | ❌ None | ✅ Required |
| **Rate Limits** | ❌ None | ⚠️ Yes | ✅ Yes |
| **Privacy** | ✅ Local | ⚠️ External | ⚠️ External |
| **Sources** | 70+ | 1 | 1 |

## Usage

### Basic Search

```bash
curl -s "http://localhost:8888/search?q=your+query&format=json"
```

### With PowerShell

```powershell
$results = Invoke-RestMethod -Uri "http://localhost:8888/search?q=AI+agents&format=json"
$results.results | Select-Object -First 5 | ForEach-Object { $_.title; $_.url }
```

### In Meeseeks

```python
# In exec command
exec(command='curl -s "http://localhost:8888/search?q=python+async&format=json"')
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query | `q=AI+agents` |
| `format` | Output format | `format=json` |
| `engines` | Specific engines | `engines=google,brave` |
| `categories` | Result type | `categories=images` |
| `pageno` | Page number | `pageno=2` |
| `safesearch` | Filter level | `safesearch=0` |

## Response Format

```json
{
  "query": "AI agents",
  "number_of_results": 5000,
  "results": [
    {
      "url": "https://example.com",
      "title": "Result Title",
      "content": "Snippet of content...",
      "engine": "brave",
      "engines": ["brave", "google"],
      "score": 12.6
    }
  ]
}
```

## Best Practices

### 1. Limit Results

```bash
# Get top 5 results
curl -s "http://localhost:8888/search?q=query&format=json" | jq '.results[:5]'
```

### 2. Extract Titles and URLs

```bash
curl -s "http://localhost:8888/search?q=query&format=json" | jq '.results[] | {title, url}'
```

### 3. Search Specific Engines

```bash
# Only Wikipedia and GitHub
curl -s "http://localhost:8888/search?q=rust+programming&format=json&engines=wikipedia,github"
```

### 4. Category Search

```bash
# Images only
curl -s "http://localhost:8888/search?q=cats&format=json&categories=images"
```

## Integration with Meeseeks

### Fast Template Addition

Add to `fast.md` template:

```markdown
### Search (SearXNG)
```
exec(command='curl -s "http://localhost:8888/search?q=QUERY&format=json"')
```
Fast, local, no API keys. Returns JSON.
```

### Search Function

```python
def search(query, n=5):
    """Search SearXNG and return top N results."""
    import json
    import subprocess
    
    cmd = f'curl -s "http://localhost:8888/search?q={query}&format=json"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    return data['results'][:n]
```

## Available Engines

Some popular engines available:

- **General:** google, bing, brave, duckduckgo, startpage
- **Tech:** github, stackoverflow, npm, pypi
- **Academic:** arxiv, semantic scholar, pubmed
- **Media:** youtube, flickr, deviantart
- **Wiki:** wikipedia, wikidata

Check all: `curl -s "http://localhost:8888/engines" | jq '.'`

## Status Check

```bash
# Check if SearXNG is running
curl -s "http://localhost:8888/health" || echo "SearXNG not running"
```

## Troubleshooting

### No Results

```bash
# Check enabled engines
curl -s "http://localhost:8888/config" | jq '.engines'
```

### Slow Response

```bash
# Reduce engines
curl -s "http://localhost:8888/search?q=query&format=json&engines=brave,google"
```

### Timeout

```bash
# Increase timeout (default 10s)
curl -s --max-time 30 "http://localhost:8888/search?q=query&format=json"
```

---

**SearXNG: Fast, private, unlimited search.** 🔍

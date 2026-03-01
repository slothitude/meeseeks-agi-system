# SearXNG for Sloth_rog 🦥

A privacy-respecting metasearch engine with JSON API support, running in Docker.

## Quick Start

### Start SearXNG
```powershell
cd C:\Users\aaron\.openclaw\workspace\searxng
docker-compose up -d
```

### Stop SearXNG
```powershell
cd C:\Users\aaron\.openclaw\workspace\searxng
docker-compose down
```

### Check Status
```powershell
docker ps --filter "name=searxng"
```

## JSON API Endpoint

### Base URL
```
http://localhost:8888/search
```

### Query Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Search query (required) | `q=python+tutorial` |
| `format` | Output format | `format=json` |
| `engines` | Specific engines | `engines=google,duckduckgo` |
| `categories` | Search categories | `categories=general,images` |
| `pageno` | Page number | `pageno=2` |
| `safesearch` | 0=off, 1=moderate, 2=strict | `safesearch=0` |

### Example Queries

**Basic search:**
```
http://localhost:8888/search?q=rust+programming&format=json
```

**PowerShell example:**
```powershell
$query = "rust programming"
$url = "http://localhost:8888/search?q=$($query -replace ' ','+')&format=json"
$results = Invoke-RestMethod -Uri $url
$results.results | Select-Object -First 5 | ForEach-Object { Write-Host "$($_.title): $($_.url)" }
```

**Using curl:**
```bash
curl "http://localhost:8888/search?q=rust+programming&format=json"
```

### JSON Response Structure

```json
{
  "query": "rust programming",
  "number_of_results": 100,
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "content": "Snippet of content...",
      "engine": "duckduckgo",
      "engines": ["duckduckgo", "google"],
      "score": 0.8,
      "category": "general",
      "publishedDate": "2024-01-15T00:00:00"
    }
  ],
  "suggestions": ["rust lang", "rust vs go"],
  "answers": [],
  "infoboxes": [],
  "unresponsive_engines": []
}
```

## Enabled Search Engines

- **google** - Google Search
- **duckduckgo** - DuckDuckGo
- **bing** - Microsoft Bing
- **wikipedia** - Wikipedia
- **github** - GitHub code search

## Configuration Files

- `docker-compose.yml` - Docker configuration
- `searxng/settings.yml` - SearXNG settings (JSON API enabled)
- `searxng/uwsgi.ini` - Application server config

## Management Commands

**View logs:**
```powershell
docker logs searxng -f
```

**Restart container:**
```powershell
docker restart searxng
```

**Update to latest image:**
```powershell
cd C:\Users\aaron\.openclaw\workspace\searxng
docker-compose pull
docker-compose up -d
```

## Integration with Sloth_rog

The JSON API is designed for AI assistant integration:

```powershell
# Function for Sloth_rog to search
function Search-Web {
    param([string]$Query, [int]$MaxResults = 5)
    
    $url = "http://localhost:8888/search?q=$([uri]::EscapeDataString($Query))&format=json"
    $results = Invoke-RestMethod -Uri $url
    
    return $results.results | Select-Object -First $MaxResults | 
        Select-Object title, url, content, engine
}

# Usage
Search-Web "docker compose best practices"
```

## Troubleshooting

**Container won't start:**
```powershell
docker logs searxng
```

**API not responding:**
```powershell
# Check container is running
docker ps --filter "name=searxng"

# Test basic connectivity
Invoke-WebRequest -Uri "http://localhost:8888" -UseBasicParsing
```

**Reset everything:**
```powershell
docker-compose down -v
docker-compose up -d
```

---

🦥 *Powered by SearXNG - Privacy-respecting metasearch*

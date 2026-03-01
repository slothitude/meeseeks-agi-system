---
name: search-workflow
description: Cascading search workflow - Local SearXNG first, then Playwright fallback for JS-heavy or blocked sites.
---

# 🔍 Search Workflow

## Philosophy

**Fast first, thorough second.**

1. Try local SearXNG (instant, private, no rate limits)
2. If SearXNG fails or content needs JS/rendering → Playwright

This gives us speed when possible, fallback when necessary.

## The Workflow

### Step 1: SearXNG (Default)

**When to use:**
- General web searches
- Finding documentation
- Quick lookups
- When you don't need to interact with the page

**Endpoint:**
```
http://localhost:8888/search?q=<query>&format=json
```

**Example call:**
```powershell
$results = Invoke-RestMethod -Uri "http://localhost:8888/search?q=rust+programming&format=json"
$results.results | Select-Object -First 5 | ForEach-Object { $_.title; $_.url }
```

**Pros:**
- Fast (aggregates multiple engines)
- No API keys needed
- Private (local instance)
- JSON output ready to parse

**Cons:**
- Some engines block it (CAPTCHA, timeouts)
- Can't handle JS-rendered content
- Rate limited by upstream search engines

### Step 2: Playwright Fallback

**When to use:**
- SearXNG returns nothing useful
- Site requires JavaScript
- Need to interact with page (click, scroll, login)
- Site blocks automated requests but works in real browser

**Using the browser tool:**
```
browser action=navigate targetUrl="https://example.com"
browser action=snapshot
```

**Or for scraping specific content:**
```
browser action=navigate targetUrl="https://example.com/search?q=rust"
browser action=snapshot refs=aria
# Then extract content from the snapshot
```

**Pros:**
- Full browser (handles JS, dynamic content)
- Can interact with pages
- Harder to block

**Cons:**
- Slower
- More resource intensive
- Requires more tokens to parse

## Decision Matrix

| Task | Start With | Fallback |
|------|-----------|----------|
| General search | SearXNG | Playwright (Google directly) |
| Documentation lookup | SearXNG | Playwright (visit docs site) |
| JS-heavy site | Playwright | N/A |
| Need to login/interact | Playwright | N/A |
| Price/product comparison | SearXNG | Playwright |
| News/articles | SearXNG | Playwright |
| API documentation | SearXNG | Playwright |

## Implementation Pattern

```python
async function search(query) {
    // Try SearXNG first
    try {
        const searxResults = await searxngSearch(query);
        if (searxResults && searxResults.length > 0) {
            return { source: 'searxng', results: searxResults };
        }
    } catch (e) {
        console.log('SearXNG failed:', e.message);
    }

    // Fallback to Playwright
    console.log('Falling back to Playwright...');
    const playwrightResults = await playwrightSearch(query);
    return { source: 'playwright', results: playwrightResults };
}
```

## When to Skip SearXNG

Go directly to Playwright when:
- You know the specific URL to visit
- The site is JS-heavy (SPA, React, Vue)
- You need to interact with the page
- Previous SearXNG attempts failed for this domain

## SearXNG Status

**Running at:** `http://localhost:8888`

**Config location:** `C:\Users\aaron\.openclaw\workspace\searxng\`

**Check status:**
```powershell
docker ps | Select-String "searxng"
```

**Restart if needed:**
```powershell
cd C:\Users\aaron\.openclaw\workspace\searxng
docker-compose restart
```

## Playwright Status

**Already installed** via browser tool.

**Usage:**
```
browser action=open targetUrl="https://example.com"
browser action=snapshot
```

---

**Fast when we can. Thorough when we must.** 🔍

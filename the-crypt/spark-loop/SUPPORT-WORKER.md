# 🥒 MINI MEESEEKS = SUPPORT WORKERS

## The Real Division of Labor

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   GLM-5 = THE BRAIN (Director)                                       │
│   - Makes all decisions                                              │
│   - Directs all work                                                 │
│   - Reviews all results                                              │
│   - Does complex reasoning                                           │
│                                                                      │
│   ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│   ministral-3 = THE HANDS (Support Worker)                          │
│   - Fetches crypt data                                               │
│   - Retrieves memories                                               │
│   - Loads specializations                                            │
│   - Summarizes files                                                 │
│   - Does file writes/edits                                           │
│   - Follows GLM-5's directions                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Support Tasks (ministral-3)

### 1. CRYPT RETRIEVAL
```python
# GLM-5 says: "Get me ancestors about API optimization"
# ministral-3 does:
ancestors = crypt.search("API optimization", top_k=3)
# Returns: ancestor wisdom, traits, approaches
```

### 2. MEMORY FETCHING
```python
# GLM-5 says: "Load relevant memories"
# ministral-3 does:
memories = memory_get("project context")
# Returns: summarized memory content
```

### 3. SPECIALIZATION LOADING
```python
# GLM-5 says: "Load the coder template"
# ministral-3 does:
template = load_template("coder.md")
# Returns: full template content
```

### 4. FILE SUMMARIZATION
```python
# GLM-5 says: "Summarize this file"
# ministral-3 does:
summary = summarize(file_content, max_tokens=200)
# Returns: key points
```

### 5. FILE WRITES/EDITS
```python
# GLM-5 says: "Write this to the file"
# ministral-3 does:
write(path, content)
# Done

# GLM-5 says: "Replace X with Y"
# ministral-3 does:
edit(path, old=X, new=Y)
# Done
```

## Workflow Example

```
┌─────────────────────────────────────────────────────────────────────┐
│                   TASK: Optimize API                                │
│                                                                      │
│   GLM-5: "Get me crypt data about API optimization"                 │
│          └──► [ministral-3 searches crypt] ──► 30ms                 │
│          └──► Returns: 3 ancestors, 2 relevant traits               │
│                                                                      │
│   GLM-5: "Load coder specialization"                                 │
│          └──► [ministral-3 loads template] ──► 50ms                 │
│          └──► Returns: coder.md content                             │
│                                                                      │
│   GLM-5: "Summarize the current API code"                           │
│          └──► [ministral-3 summarizes] ──► 600ms                    │
│          └──► Returns: key endpoints, issues                        │
│                                                                      │
│   GLM-5: [THINKS AND PLANS OPTIMIZATION]                            │
│          └──► Uses 128K context                                     │
│          └──► Reasons through problem                               │
│          └──► Creates optimization plan                             │
│                                                                      │
│   GLM-5: "Write the optimized code to api.py"                       │
│          └──► [ministral-3 writes file] ──► 100ms                   │
│          └──► Done                                                  │
│                                                                      │
│   GLM-5: "Entomb this result in the crypt"                          │
│          └──► [ministral-3 + nomic embed] ──► 30ms                  │
│          └──► Saved for future generations                          │
│                                                                      │
│   TOTAL TIME: GLM-5 thinking + 810ms support work                   │
│   TOTAL COST: 1 GLM-5 request                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Support Worker Commands

| GLM-5 Command | ministral-3 Action | Time |
|---------------|-------------------|------|
| "Search crypt for X" | `crypt.search(X)` | 30ms |
| "Load memory X" | `memory_get(X)` | 50ms |
| "Load template X" | `read(template)` | 50ms |
| "Summarize X" | `summarize(X)` | 500ms |
| "Write X to Y" | `write(Y, X)` | 100ms |
| "Edit X to Y" | `edit(path, X, Y)` | 100ms |
| "Entomb result" | `entomb(result)` | 30ms |

## Why This Works

### GLM-5 (The Brain)
- Has 128K context
- Best reasoning
- Makes decisions
- Directs work

### ministral-3 (The Hands)
- Fast at simple tasks
- Free to use
- Follows directions
- Does grunt work

## Implementation

```python
class SupportWorker:
    """
    ministral-3 support worker.
    Follows GLM-5's commands.
    """
    
    def fetch_crypt(self, query: str, k: int = 3) -> List[Dict]:
        """Get ancestor wisdom."""
        return crypt.search(query, top_k=k)
    
    def fetch_memory(self, path: str) -> str:
        """Get memory content."""
        return memory_get(path)
    
    def load_template(self, name: str) -> str:
        """Load specialization template."""
        return read(f"templates/{name}.md")
    
    def summarize(self, content: str, max_tokens: int = 200) -> str:
        """Summarize content."""
        prompt = f"SUMMARIZE:\n{content}"
        return mini_generate(prompt, max_tokens)
    
    def write_file(self, path: str, content: str) -> bool:
        """Write to file."""
        write(path, content)
        return True
    
    def edit_file(self, path: str, old: str, new: str) -> bool:
        """Edit file."""
        edit(path, old, new)
        return True
    
    def entomb(self, result: Dict) -> bool:
        """Save to crypt."""
        entomb_result(result)
        return True


class Director:
    """
    GLM-5 director.
    Commands support worker.
    """
    
    def __init__(self):
        self.worker = SupportWorker()
    
    def solve(self, task: str) -> str:
        """
        Solve task with support worker.
        """
        # Get context (worker does this)
        ancestors = self.worker.fetch_crypt(task)
        template = self.worker.load_template("coder")
        
        # Think and plan (GLM-5 does this)
        plan = self.think(task, ancestors, template)
        
        # Execute (worker does the writing)
        for step in plan.steps:
            if step.action == "write":
                self.worker.write_file(step.path, step.content)
            elif step.action == "edit":
                self.worker.edit_file(step.path, step.old, step.new)
        
        # Save result (worker does this)
        self.worker.entomb({"task": task, "result": plan.result})
        
        return plan.result
```

## Summary

**GLM-5 = Director** → Thinks, decides, commands
**ministral-3 = Worker** → Fetches, summarizes, writes, edits

The mini model does the grunt work so GLM-5 can focus on thinking.

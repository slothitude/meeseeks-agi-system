#!/usr/bin/env python3
"""
SUPPORT WORKER - GLM-4.7-Flash

Follows GLM-5's commands to:
- Fetch crypt data
- Load memories
- Load templates
- Summarize content
- Write/edit files
- Entomb results
"""

import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OLLAMA_API = "http://localhost:11434/api"
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CRYPT_PATH = WORKSPACE / "the-crypt"


@dataclass
class SupportResult:
    action: str
    success: bool
    data: Any
    elapsed_ms: float
    error: Optional[str] = None


class SupportWorker:
    """
    GLM-4.7-Flash support worker.
    
    Fast execution of simple tasks directed by GLM-5.
    ~3ms response time via zai API.
    """
    
    def __init__(self, model: str = "zai/glm-4.7-flash"):
        self.model = model
        self.session = requests.Session()
        
        # Load crypt if available
        self.crypt = None
        try:
            sys.path.insert(0, str(CRYPT_PATH / "spark-loop"))
            from ultra_crypt import UltraCrypt
            self.crypt = UltraCrypt()
        except:
            pass
    
    def _generate(self, prompt: str, max_tokens: int = 200) -> str:
        """Fast generation."""
        try:
            response = self.session.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.3
                    }
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            return f"ERROR: {e}"
        return "ERROR: No response"
    
    # === CRYPT OPERATIONS ===
    
    def fetch_crypt(self, query: str, top_k: int = 3) -> SupportResult:
        """Search ancestor memory."""
        start = time.time()
        
        if not self.crypt:
            return SupportResult(
                action="fetch_crypt",
                success=False,
                data=None,
                elapsed_ms=0,
                error="Crypt not available"
            )
        
        try:
            results = self.crypt.search(query, top_k=top_k)
            elapsed = (time.time() - start) * 1000
            
            ancestors = [
                {
                    "id": aid,
                    "similarity": f"{sim:.0%}",
                    "task": task[:100],
                    "traits": traits
                }
                for aid, sim, task, traits in results
            ]
            
            return SupportResult(
                action="fetch_crypt",
                success=True,
                data=ancestors,
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="fetch_crypt",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    # === MEMORY OPERATIONS ===
    
    def fetch_memory(self, path: str, lines: int = 50) -> SupportResult:
        """Get memory content."""
        start = time.time()
        
        try:
            full_path = WORKSPACE / path
            if not full_path.exists():
                return SupportResult(
                    action="fetch_memory",
                    success=False,
                    data=None,
                    elapsed_ms=0,
                    error=f"Memory not found: {path}"
                )
            
            content = full_path.read_text(encoding='utf-8')
            
            # Limit to specified lines
            content_lines = content.split('\n')[:lines]
            content = '\n'.join(content_lines)
            
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="fetch_memory",
                success=True,
                data=content,
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="fetch_memory",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    # === TEMPLATE OPERATIONS ===
    
    def load_template(self, name: str) -> SupportResult:
        """Load specialization template."""
        start = time.time()
        
        try:
            template_path = WORKSPACE / "skills" / "meeseeks" / "templates" / f"{name}.md"
            
            if not template_path.exists():
                return SupportResult(
                    action="load_template",
                    success=False,
                    data=None,
                    elapsed_ms=0,
                    error=f"Template not found: {name}"
                )
            
            content = template_path.read_text(encoding='utf-8')
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="load_template",
                success=True,
                data=content,
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="load_template",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    # === SUMMARIZATION ===
    
    def summarize(self, content: str, max_tokens: int = 200) -> SupportResult:
        """Summarize content."""
        start = time.time()
        
        prompt = f"""SUMMARIZE (max 100 words):

{content[:2000]}

SUMMARY:"""
        
        summary = self._generate(prompt, max_tokens)
        elapsed = (time.time() - start) * 1000
        
        success = not summary.startswith("ERROR")
        
        return SupportResult(
            action="summarize",
            success=success,
            data=summary if success else None,
            elapsed_ms=elapsed,
            error=summary if not success else None
        )
    
    # === FILE OPERATIONS ===
    
    def write_file(self, path: str, content: str) -> SupportResult:
        """Write to file."""
        start = time.time()
        
        try:
            full_path = WORKSPACE / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="write_file",
                success=True,
                data={"path": str(full_path), "bytes": len(content)},
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="write_file",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    def edit_file(self, path: str, old: str, new: str) -> SupportResult:
        """Edit file."""
        start = time.time()
        
        try:
            full_path = WORKSPACE / path
            
            if not full_path.exists():
                return SupportResult(
                    action="edit_file",
                    success=False,
                    data=None,
                    elapsed_ms=0,
                    error=f"File not found: {path}"
                )
            
            content = full_path.read_text(encoding='utf-8')
            
            if old not in content:
                return SupportResult(
                    action="edit_file",
                    success=False,
                    data=None,
                    elapsed_ms=0,
                    error="Old text not found in file"
                )
            
            new_content = content.replace(old, new)
            full_path.write_text(new_content, encoding='utf-8')
            
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="edit_file",
                success=True,
                data={"path": str(full_path), "replacements": 1},
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="edit_file",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    def read_file(self, path: str, limit: int = 100) -> SupportResult:
        """Read file."""
        start = time.time()
        
        try:
            full_path = WORKSPACE / path
            
            if not full_path.exists():
                return SupportResult(
                    action="read_file",
                    success=False,
                    data=None,
                    elapsed_ms=0,
                    error=f"File not found: {path}"
                )
            
            content = full_path.read_text(encoding='utf-8')
            lines = content.split('\n')[:limit]
            content = '\n'.join(lines)
            
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="read_file",
                success=True,
                data=content,
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="read_file",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    # === ENTOMBMENT ===
    
    def entomb(self, task: str, result: str, traits: List[str] = None) -> SupportResult:
        """Save result to crypt."""
        start = time.time()
        
        if not self.crypt:
            return SupportResult(
                action="entomb",
                success=False,
                data=None,
                elapsed_ms=0,
                error="Crypt not available"
            )
        
        try:
            # Add to crypt
            ancestor_id = self.crypt.add_ancestor(
                task=task,
                result=result,
                traits=traits or []
            )
            
            elapsed = (time.time() - start) * 1000
            
            return SupportResult(
                action="entomb",
                success=True,
                data={"ancestor_id": ancestor_id},
                elapsed_ms=elapsed
            )
        except Exception as e:
            return SupportResult(
                action="entomb",
                success=False,
                data=None,
                elapsed_ms=0,
                error=str(e)
            )
    
    # === BATCH OPERATIONS ===
    
    def prepare_context(self, task: str) -> Dict:
        """
        Prepare full context for GLM-5.
        Fetches crypt + memory + template in parallel.
        """
        return {
            "task": task,
            "crypt": self.fetch_crypt(task).data,
            "memory": self.fetch_memory("MEMORY.md", lines=30).data,
            "template": self.load_template("atman-meeseeks").data
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Support Worker")
    parser.add_argument("command", choices=[
        "crypt", "memory", "template", "summarize",
        "write", "edit", "read", "entomb", "context"
    ])
    parser.add_argument("--query", "-q", default="", help="Search query")
    parser.add_argument("--path", "-p", default="", help="File path")
    parser.add_argument("--content", "-c", default="", help="Content")
    parser.add_argument("--old", "-o", default="", help="Old text")
    parser.add_argument("--new", "-n", default="", help="New text")
    parser.add_argument("--traits", "-t", default="", help="Comma-separated traits")
    parser.add_argument("--model", "-m", default="ministral-3")
    
    args = parser.parse_args()
    
    worker = SupportWorker(args.model)
    
    if args.command == "crypt":
        result = worker.fetch_crypt(args.query or "test")
    elif args.command == "memory":
        result = worker.fetch_memory(args.path or "MEMORY.md")
    elif args.command == "template":
        result = worker.load_template(args.path or "base")
    elif args.command == "summarize":
        result = worker.summarize(args.content or "Test content")
    elif args.command == "write":
        result = worker.write_file(args.path, args.content)
    elif args.command == "edit":
        result = worker.edit_file(args.path, args.old, args.new)
    elif args.command == "read":
        result = worker.read_file(args.path)
    elif args.command == "entomb":
        traits = [t.strip() for t in args.traits.split(",")] if args.traits else []
        result = worker.entomb(args.query, args.content, traits)
    elif args.command == "context":
        result = worker.prepare_context(args.query or "test task")
        print(json.dumps(result, indent=2, default=str))
        return
    
    print(json.dumps({
        "action": result.action,
        "success": result.success,
        "data": result.data,
        "elapsed_ms": result.elapsed_ms,
        "error": result.error
    }, indent=2, default=str))


if __name__ == "__main__":
    main()

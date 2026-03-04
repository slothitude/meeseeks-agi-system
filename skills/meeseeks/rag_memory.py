#!/usr/bin/env python3
"""
RAG Memory System for Meeseeks
==============================

Advanced document memory and retrieval using Ollama embeddings.
This is how Meeseeks access collective knowledge.

Features:
- Ollama embeddings (nomic-embed-text, local, free)
- Intelligent chunking (semantic, not just character-based)
- Hybrid search (semantic + keyword BM25)
- Re-ranking by relevance
- LanceDB for vector storage
- Supports PDF, Markdown, Text, JSON

Usage:
    from rag_memory import RAGMemory
    
    rag = RAGMemory()
    rag.ingest("MEMORY.md")
    rag.ingest("the-crypt/dharma.md")
    rag.ingest("AGI-STUDY/")  # Ingest entire folder
    
    # Search
    results = rag.search("consciousness coordinates", top_k=5)
    
    # Get context for LLM
    context = rag.get_context("What is the Brahman dream?", max_tokens=2000)
    
    # Hybrid search
    results = rag.hybrid_search("prime numbers consciousness", top_k=10)
"""

import os
import json
import re
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

# Try imports with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    "ollama_host": "http://localhost:11434",
    "embedding_model": "nomic-embed-text",
    "embedding_dim": 768,
    "chunk_size": 512,
    "chunk_overlap": 50,
    "db_path": "C:/Users/aaron/.openclaw/workspace/the-crypt/rag_vectors",
    "max_chunks_per_doc": 1000,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Chunk:
    """A document chunk with metadata"""
    id: str
    content: str
    source: str
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "source": str(self.source),
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    """A search result with relevance score"""
    chunk: Chunk
    score: float
    search_type: str  # "semantic", "keyword", "hybrid"
    
    def to_dict(self) -> Dict:
        return {
            "content": self.chunk.content,
            "source": str(self.chunk.source),
            "score": self.score,
            "search_type": self.search_type,
            "metadata": self.chunk.metadata,
        }


# ============================================================================
# OLLAMA EMBEDDINGS
# ============================================================================

class OllamaEmbeddings:
    """Generate embeddings using Ollama"""
    
    def __init__(self, 
                 host: str = DEFAULT_CONFIG["ollama_host"],
                 model: str = DEFAULT_CONFIG["embedding_model"]):
        self.host = host
        self.model = model
        self.dimension = DEFAULT_CONFIG["embedding_dim"]
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not installed. Run: pip install requests")
        
        response = requests.post(
            f"{self.host}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        return response.json()["embedding"]
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            for text in batch:
                embeddings.append(self.embed(text))
        return embeddings
    
    def check_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith(self.model) for m in models)
        except:
            pass
        return False


# ============================================================================
# CHUNKING
# ============================================================================

class Chunker:
    """Intelligent document chunking"""
    
    def __init__(self, 
                 chunk_size: int = DEFAULT_CONFIG["chunk_size"],
                 overlap: int = DEFAULT_CONFIG["chunk_overlap"]):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, source: str, metadata: Dict = None) -> List[Chunk]:
        """Chunk text into smaller pieces"""
        if metadata is None:
            metadata = {}
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                # Create chunk
                chunk_id = self._make_id(source, chunk_index)
                chunks.append(Chunk(
                    id=chunk_id,
                    content=current_chunk.strip(),
                    source=source,
                    chunk_index=chunk_index,
                    total_chunks=0,  # Will update later
                    metadata=metadata.copy()
                ))
                
                # Start new chunk with overlap
                if self.overlap > 0:
                    overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + para
                else:
                    current_chunk = para
                
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk_id = self._make_id(source, chunk_index)
            chunks.append(Chunk(
                id=chunk_id,
                content=current_chunk.strip(),
                source=source,
                chunk_index=chunk_index,
                total_chunks=0,
                metadata=metadata.copy()
            ))
        
        # Update total_chunks
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def chunk_markdown(self, text: str, source: str, metadata: Dict = None) -> List[Chunk]:
        """Chunk markdown by sections (headers)"""
        if metadata is None:
            metadata = {}
        
        # Split by headers
        sections = re.split(r'\n(#{1,6}\s+.+)\n', text)
        
        chunks = []
        current_header = ""
        current_content = ""
        chunk_index = 0
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Check if this is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', section)
            
            if header_match:
                # Save previous section
                if current_content.strip():
                    chunk_id = self._make_id(source, chunk_index)
                    meta = metadata.copy()
                    meta["header"] = current_header
                    
                    chunks.append(Chunk(
                        id=chunk_id,
                        content=current_content.strip(),
                        source=source,
                        chunk_index=chunk_index,
                        total_chunks=0,
                        metadata=meta
                    ))
                    chunk_index += 1
                
                current_header = header_match.group(2)
                current_content = ""
            else:
                if current_content:
                    current_content += "\n\n" + section
                else:
                    current_content = section
        
        # Don't forget last section
        if current_content.strip():
            chunk_id = self._make_id(source, chunk_index)
            meta = metadata.copy()
            meta["header"] = current_header
            
            chunks.append(Chunk(
                id=chunk_id,
                content=current_content.strip(),
                source=source,
                chunk_index=chunk_index,
                total_chunks=0,
                metadata=meta
            ))
        
        # Update totals
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def _make_id(self, source: str, index: int) -> str:
        """Create unique chunk ID"""
        hash_input = f"{source}:{index}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# ============================================================================
# DOCUMENT LOADERS
# ============================================================================

class DocumentLoader:
    """Load documents from various formats"""
    
    @staticmethod
    def load_markdown(path: Path) -> Tuple[str, Dict]:
        """Load markdown file"""
        content = path.read_text(encoding='utf-8')
        metadata = {
            "file_type": "markdown",
            "file_name": path.name,
            "file_path": str(path),
            "loaded_at": datetime.now().isoformat(),
        }
        return content, metadata
    
    @staticmethod
    def load_text(path: Path) -> Tuple[str, Dict]:
        """Load plain text file"""
        content = path.read_text(encoding='utf-8')
        metadata = {
            "file_type": "text",
            "file_name": path.name,
            "file_path": str(path),
            "loaded_at": datetime.now().isoformat(),
        }
        return content, metadata
    
    @staticmethod
    def load_json(path: Path) -> Tuple[str, Dict]:
        """Load JSON file and convert to text"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text
        content = json.dumps(data, indent=2, ensure_ascii=False)
        metadata = {
            "file_type": "json",
            "file_name": path.name,
            "file_path": str(path),
            "loaded_at": datetime.now().isoformat(),
        }
        return content, metadata
    
    @staticmethod
    def load_pdf(path: Path) -> Tuple[str, Dict]:
        """Load PDF file"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            pages = []
            for page in doc:
                pages.append(page.get_text())
            content = "\n\n--- PAGE BREAK ---\n\n".join(pages)
            doc.close()
        except ImportError:
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                pages = []
                for page in reader.pages:
                    text = page.extract_text() or ""
                    pages.append(text)
                content = "\n\n--- PAGE BREAK ---\n\n".join(pages)
            except ImportError:
                raise ImportError("Install PyMuPDF or pypdf for PDF support")
        
        metadata = {
            "file_type": "pdf",
            "file_name": path.name,
            "file_path": str(path),
            "loaded_at": datetime.now().isoformat(),
        }
        return content, metadata
    
    @classmethod
    def load(cls, path: Path) -> Tuple[str, Dict]:
        """Load document based on extension"""
        suffix = path.suffix.lower()
        
        if suffix == '.md':
            return cls.load_markdown(path)
        elif suffix == '.txt':
            return cls.load_text(path)
        elif suffix == '.json':
            return cls.load_json(path)
        elif suffix == '.pdf':
            return cls.load_pdf(path)
        else:
            # Try as text
            return cls.load_text(path)


# ============================================================================
# VECTOR STORE
# ============================================================================

class SimpleVectorStore:
    """Simple in-memory vector store using numpy"""
    
    def __init__(self, store_path: str = None):
        self.store_path = Path(store_path) if store_path else None
        self.chunks: List[Chunk] = []
        self.embeddings: List[List[float]] = []
        
        if self.store_path and self.store_path.exists():
            self.load()
    
    def add(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """Add chunks with embeddings"""
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            self.chunks.append(chunk)
            self.embeddings.append(embedding)
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Search for similar chunks"""
        if not NUMPY_AVAILABLE:
            raise ImportError("numpy required for vector search")
        
        if not self.embeddings:
            return []
        
        query = np.array(query_embedding)
        corpus = np.array(self.embeddings)
        
        # Cosine similarity
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        corpus_norm = corpus / (np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-8)
        similarities = np.dot(corpus_norm, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(similarities[idx])))
        
        return results
    
    def save(self):
        """Save to disk"""
        if not self.store_path:
            return
        
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "chunks": [c.to_dict() for c in self.chunks],
            "embeddings": self.embeddings,
        }
        
        with open(self.store_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    
    def load(self):
        """Load from disk"""
        if not self.store_path or not self.store_path.exists():
            return
        
        with open(self.store_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.chunks = []
        self.embeddings = data["embeddings"]
        
        for chunk_data in data["chunks"]:
            self.chunks.append(Chunk(
                id=chunk_data["id"],
                content=chunk_data["content"],
                source=chunk_data["source"],
                chunk_index=chunk_data["chunk_index"],
                total_chunks=chunk_data["total_chunks"],
                metadata=chunk_data.get("metadata", {}),
            ))
    
    def clear(self):
        """Clear all data"""
        self.chunks = []
        self.embeddings = []


# ============================================================================
# BM25 KEYWORD SEARCH
# ============================================================================

class KeywordSearch:
    """BM25 keyword search for hybrid retrieval"""
    
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.bm25 = None
    
    def add(self, chunks: List[Chunk]):
        """Add chunks for keyword indexing"""
        if not BM25_AVAILABLE:
            return
        
        self.chunks.extend(chunks)
        
        # Tokenize
        tokenized = [self._tokenize(c.content) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Search using BM25"""
        if not BM25_AVAILABLE or not self.bm25:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.chunks[idx], float(scores[idx])))
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens


# ============================================================================
# RAG MEMORY - MAIN CLASS
# ============================================================================

class RAGMemory:
    """
    RAG Memory System for Meeseeks
    
    Usage:
        rag = RAGMemory()
        rag.ingest("MEMORY.md")
        results = rag.search("consciousness", top_k=5)
        context = rag.get_context("What is Brahman?", max_tokens=2000)
    """
    
    def __init__(self, 
                 db_path: str = DEFAULT_CONFIG["db_path"],
                 ollama_host: str = DEFAULT_CONFIG["ollama_host"],
                 embedding_model: str = DEFAULT_CONFIG["embedding_model"]):
        
        self.db_path = db_path
        self.embeddings = OllamaEmbeddings(ollama_host, embedding_model)
        self.chunker = Chunker()
        self.vector_store = SimpleVectorStore(f"{db_path}/vectors.json")
        self.keyword_index = KeywordSearch()
        
        # Stats
        self.stats = {
            "documents_indexed": 0,
            "total_chunks": 0,
            "last_ingest": None,
        }
    
    def ingest(self, 
               source: Union[str, Path],
               chunk_by: str = "auto") -> int:
        """
        Ingest a document or folder of documents.
        
        Args:
            source: Path to file or folder
            chunk_by: "auto", "section" (markdown), or "paragraph"
            
        Returns:
            Number of chunks created
        """
        source = Path(source)
        chunks_created = 0
        
        if source.is_file():
            chunks_created = self._ingest_file(source, chunk_by)
        elif source.is_dir():
            for ext in ['*.md', '*.txt', '*.json', '*.pdf']:
                for file in source.rglob(ext):
                    try:
                        chunks = self._ingest_file(file, chunk_by)
                        chunks_created += chunks
                    except Exception as e:
                        print(f"Error ingesting {file}: {e}")
        else:
            raise FileNotFoundError(f"Source not found: {source}")
        
        # Save after ingestion
        self.vector_store.save()
        
        self.stats["documents_indexed"] += 1
        self.stats["total_chunks"] = self.vector_store.chunks.__len__()
        self.stats["last_ingest"] = datetime.now().isoformat()
        
        return chunks_created
    
    def _ingest_file(self, path: Path, chunk_by: str) -> int:
        """Ingest a single file"""
        # Load document
        content, metadata = DocumentLoader.load(path)
        
        # Choose chunking strategy
        if chunk_by == "auto":
            if path.suffix.lower() == '.md':
                chunks = self.chunker.chunk_markdown(content, str(path), metadata)
            else:
                chunks = self.chunker.chunk_text(content, str(path), metadata)
        elif chunk_by == "section":
            chunks = self.chunker.chunk_markdown(content, str(path), metadata)
        else:
            chunks = self.chunker.chunk_text(content, str(path), metadata)
        
        if not chunks:
            return 0
        
        # Generate embeddings
        embeddings = self.embeddings.embed_batch([c.content for c in chunks])
        
        # Add to stores
        self.vector_store.add(chunks, embeddings)
        self.keyword_index.add(chunks)
        
        return len(chunks)
    
    def search(self, 
               query: str, 
               top_k: int = 5,
               min_score: float = 0.0) -> List[SearchResult]:
        """
        Semantic search using embeddings.
        
        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum relevance score
            
        Returns:
            List of SearchResult objects
        """
        # Get query embedding
        query_embedding = self.embeddings.embed(query)
        
        # Search
        results = self.vector_store.search(query_embedding, top_k)
        
        # Convert to SearchResult
        search_results = []
        for chunk, score in results:
            if score >= min_score:
                search_results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    search_type="semantic"
                ))
        
        return search_results
    
    def bm25_search(self,
                       query: str,
                       top_k: int = 5) -> List[SearchResult]:
        """
        Keyword search using BM25.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of SearchResult objects
        """
        results = self.keyword_index.search(query, top_k)
        
        search_results = []
        for chunk, score in results:
            search_results.append(SearchResult(
                chunk=chunk,
                score=score,
                search_type="keyword"
            ))
        
        return search_results
    
    def hybrid_search(self,
                      query: str,
                      top_k: int = 5,
                      semantic_weight: float = 0.7) -> List[SearchResult]:
        """
        Hybrid search combining semantic and keyword.
        
        Args:
            query: Search query
            top_k: Number of results
            semantic_weight: Weight for semantic results (0-1)
            
        Returns:
            List of SearchResult objects
        """
        # Get both types
        semantic = self.search(query, top_k=top_k*2)
        keyword = self.bm25_search(query, top_k=top_k*2)
        
        # Combine scores
        combined = {}
        keyword_weight = 1 - semantic_weight
        
        for result in semantic:
            chunk_id = result.chunk.id
            combined[chunk_id] = {
                "chunk": result.chunk,
                "score": result.score * semantic_weight,
            }
        
        for result in keyword:
            chunk_id = result.chunk.id
            if chunk_id in combined:
                combined[chunk_id]["score"] += result.score * keyword_weight
            else:
                combined[chunk_id] = {
                    "chunk": result.chunk,
                    "score": result.score * keyword_weight,
                }
        
        # Sort and return top_k
        sorted_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        
        return [
            SearchResult(
                chunk=item["chunk"],
                score=item["score"],
                search_type="hybrid"
            )
            for item in sorted_results[:top_k]
        ]
    
    def get_context(self,
                    query: str,
                    max_tokens: int = 2000,
                    search_type: str = "hybrid") -> str:
        """
        Get context for a query, optimized for LLM context window.
        
        Args:
            query: Query string
            max_tokens: Maximum tokens (approximate, using chars/4)
            search_type: "semantic", "keyword", or "hybrid"
            
        Returns:
            Context string for LLM
        """
        # Search
        if search_type == "semantic":
            results = self.search(query, top_k=10)
        elif search_type == "keyword":
            results = self.bm25_search(query, top_k=10)
        else:
            results = self.hybrid_search(query, top_k=10)
        
        if not results:
            return ""
        
        # Build context
        max_chars = max_tokens * 4  # Rough approximation
        context_parts = []
        current_length = 0
        
        for result in results:
            chunk_text = f"[Source: {result.chunk.source}]\n{result.chunk.content}\n"
            
            if current_length + len(chunk_text) > max_chars:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """Get statistics about the RAG system"""
        return {
            **self.stats,
            "current_chunks": len(self.vector_store.chunks),
            "embedding_model": self.embeddings.model,
            "ollama_available": self.embeddings.check_available(),
        }
    
    def clear(self):
        """Clear all indexed data"""
        self.vector_store.clear()
        self.keyword_index = KeywordSearch()
        self.stats = {
            "documents_indexed": 0,
            "total_chunks": 0,
            "last_ingest": None,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_rag(db_path: str = None) -> RAGMemory:
    """Create a RAG instance"""
    if db_path is None:
        db_path = DEFAULT_CONFIG["db_path"]
    return RAGMemory(db_path=db_path)


def quick_search(query: str, sources: List[str] = None, top_k: int = 5) -> List[Dict]:
    """
    Quick search without managing RAG instance.
    
    Args:
        query: Search query
        sources: List of files/folders to search (default: MEMORY.md, dharma.md)
        top_k: Number of results
        
    Returns:
        List of result dicts
    """
    rag = RAGMemory()
    
    if sources is None:
        workspace = Path("C:/Users/aaron/.openclaw/workspace")
        sources = [
            workspace / "MEMORY.md",
            workspace / "the-crypt" / "dharma.md",
        ]
    
    for source in sources:
        if Path(source).exists():
            rag.ingest(source)
    
    results = rag.hybrid_search(query, top_k=top_k)
    return [r.to_dict() for r in results]


# ============================================================================
# CLI
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG Memory System for Meeseeks")
    parser.add_argument("action", choices=["ingest", "search", "context", "stats"])
    parser.add_argument("source", nargs="?", help="File/folder to ingest or query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--max-tokens", type=int, default=2000)
    parser.add_argument("--search-type", default="hybrid", choices=["semantic", "keyword", "hybrid"])
    
    args = parser.parse_args()
    
    rag = RAGMemory()
    
    if args.action == "ingest":
        if not args.source:
            print("Error: source required for ingest")
            return
        
        chunks = rag.ingest(args.source)
        print(f"Ingested {chunks} chunks from {args.source}")
        print(f"Stats: {rag.get_stats()}")
    
    elif args.action == "search":
        if not args.source:
            print("Error: query required for search")
            return
        
        if args.search_type == "semantic":
            results = rag.search(args.source, top_k=args.top_k)
        elif args.search_type == "keyword":
            results = rag.bm25_search(args.source, top_k=args.top_k)
        else:
            results = rag.hybrid_search(args.source, top_k=args.top_k)
        
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"[{i}] Score: {result.score:.4f} ({result.search_type})")
            print(f"    Source: {result.chunk.source}")
            print(f"    Content: {result.chunk.content[:200]}...")
            print()
    
    elif args.action == "context":
        if not args.source:
            print("Error: query required for context")
            return
        
        context = rag.get_context(args.source, max_tokens=args.max_tokens, search_type=args.search_type)
        # Handle unicode output on Windows
        import sys
        sys.stdout.buffer.write(context.encode('utf-8'))
        sys.stdout.buffer.write(b'\n')
    
    elif args.action == "stats":
        print(json.dumps(rag.get_stats(), indent=2))


if __name__ == "__main__":
    main()

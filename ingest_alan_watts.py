#!/usr/bin/env python3
"""
Ingest Alan Watts lectures into RAG memory.
Uses smaller chunks to fit Ollama context limits.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "skills" / "meeseeks"))

from rag_memory import RAGMemory, Chunker, DocumentLoader, OllamaEmbeddings, SimpleVectorStore

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
ALAN_WATTS = Path("C:/Users/aaron/AppData/Local/Temp/alan_watts_lectures.txt")
DB_PATH = WORKSPACE / "the-crypt/rag_vectors"

def main():
    print("=" * 60)
    print("INGESTING ALAN WATTS LECTURES")
    print("=" * 60)
    
    # Load the text
    print("\n[1] Loading text...")
    content = ALAN_WATTS.read_text(encoding='utf-8')
    print(f"    Loaded {len(content)} characters")
    
    # Create chunker with smaller chunks (200 chars for Ollama limit)
    print("\n[2] Chunking (size=200, overlap=20)...")
    chunker = Chunker(chunk_size=200, overlap=20)
    metadata = {
        "file_type": "text",
        "file_name": "alan_watts_lectures.txt",
        "file_path": str(ALAN_WATTS),
        "source": "Alan Watts Lectures and Essays",
    }
    
    chunks = chunker.chunk_text(content, str(ALAN_WATTS), metadata)
    print(f"    Created {len(chunks)} chunks")
    
    # Create embeddings
    print("\n[3] Creating embeddings...")
    embeddings = OllamaEmbeddings()
    vector_store = SimpleVectorStore(str(DB_PATH / "vectors.json"))
    
    # Process in batches
    batch_size = 5
    total_embedded = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            batch_embeddings = embeddings.embed_batch([c.content for c in batch])
            vector_store.add(batch, batch_embeddings)
            total_embedded += len(batch)
            print(f"    Embedded {total_embedded}/{len(chunks)} chunks", end='\r')
        except Exception as e:
            print(f"\n    Error on batch {i}: {e}")
            # Try smaller batches
            for chunk in batch:
                try:
                    emb = embeddings.embed(chunk.content)
                    vector_store.add([chunk], [emb])
                    total_embedded += 1
                except:
                    print(f"    Skipped chunk {chunk.chunk_index}")
    
    print(f"\n    Embedded {total_embedded} chunks total")
    
    # Save
    print("\n[4] Saving to vector store...")
    vector_store.save()
    
    print("\n" + "=" * 60)
    print(f"DONE: {total_embedded} chunks indexed")
    print("=" * 60)
    
    # Test search
    print("\n[5] Testing search...")
    results = vector_store.search(embeddings.embed("consciousness"), top_k=3)
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n[{i}] Score: {score:.4f}")
        print(f"Content: {chunk.content[:150]}...")

if __name__ == "__main__":
    main()

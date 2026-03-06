#!/usr/bin/env python3
"""
Ingest Alan Watts lectures into RAG with smaller chunks.
"""
import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace/skills/meeseeks")

from rag_memory import RAGMemory, Chunk, OllamaEmbeddings
import requests
from pathlib import Path

# Custom small chunker
def chunk_text_small(text, source, chunk_size=200, overlap=20):
    """Create very small chunks for embedding model context limits"""
    chunks = []
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Split by paragraphs
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    chunk_index = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If paragraph itself is too long, split it
        if len(para) > chunk_size:
            # Split into sentences
            sentences = para.replace('!', '.').replace('?', '.').split('. ')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        "content": current_chunk.strip(),
                        "index": chunk_index
                    })
                    chunk_index += 1
                    # Start new with overlap
                    if overlap > 0 and len(current_chunk) > overlap:
                        current_chunk = current_chunk[-overlap:] + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
        else:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "index": chunk_index
                })
                chunk_index += 1
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + " " + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += " " + para
                else:
                    current_chunk = para
    
    # Don't forget last chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "index": chunk_index
        })
    
    return chunks

def main():
    source_file = "C:/Users/aaron/AppData/Local/Temp/alan_watts_lectures.txt"
    print(f"Reading {source_file}...")
    
    text = Path(source_file).read_text(encoding='utf-8')
    print(f"File size: {len(text)} characters")
    
    # Create small chunks
    print("Creating small chunks (200 chars)...")
    chunks = chunk_text_small(text, source_file, chunk_size=200, overlap=20)
    print(f"Created {len(chunks)} chunks")
    
    # Initialize RAG
    print("Initializing RAG...")
    rag = RAGMemory()
    
    # Ingest in batches
    batch_size = 10
    total_ingested = 0
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(chunks)//batch_size)+1}...")
        
        try:
            # Get embeddings for batch
            texts = [c["content"] for c in batch]
            embeddings = rag.embeddings.embed_batch(texts)
            
            # Create Chunk objects
            for j, (chunk_data, embedding) in enumerate(zip(batch, embeddings)):
                chunk = Chunk(
                    id=f"watts_{chunk_data['index']}",
                    content=chunk_data["content"],
                    source=source_file,
                    chunk_index=chunk_data["index"],
                    total_chunks=len(chunks),
                    metadata={"author": "Alan Watts", "type": "lecture"}
                )
                rag.vector_store.add([chunk], [embedding])
            
            total_ingested += len(batch)
            print(f"  Ingested {total_ingested}/{len(chunks)} chunks")
            
        except Exception as e:
            print(f"  Error in batch: {e}")
            continue
    
    # Save
    print("Saving vector store...")
    rag.vector_store.save()
    print(f"Done! Total ingested: {total_ingested} chunks")
    
    # Test search
    print("\nTesting search...")
    results = rag.search("consciousness self universe", top_k=3)
    for r in results:
        print(f"  Score: {r.score:.3f}")
        print(f"  Content: {r.chunk.content[:100]}...")
        print()

if __name__ == "__main__":
    main()

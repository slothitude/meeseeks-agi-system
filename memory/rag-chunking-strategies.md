# RAG Chunking Strategies

## Overview
Chunking is the foundation of effective RAG systems. How you split documents directly impacts retrieval quality and generation accuracy.

---

## 1. Semantic Chunking (by Meaning, Not Characters)

### What It Is
Splits text based on **semantic meaning** rather than fixed character/word counts. Uses embeddings or LLMs to identify natural topic boundaries.

### How It Works
- Embed each sentence/paragraph
- Compare embedding similarity between adjacent segments
- Split when semantic similarity drops below threshold
- Results in variable-sized chunks based on content coherence

### Tools/Libraries
- **LangChain**: `SemanticChunker` with OpenAI/HuggingFace embeddings
- **LlamaIndex**: `SemanticSplitterNodeParser`
- **Custom**: Cosine similarity between sentence embeddings

### Pros
- ✅ Maintains contextual coherence
- ✅ Chunks align with natural topic boundaries
- ✅ Better for Q&A retrieval (complete ideas)

### Cons
- ❌ Slower (requires embedding computation)
- ❌ Variable chunk sizes can complicate batch processing
- ❌ Threshold tuning required

### Best For
- Documents with clear topic transitions (articles, research papers)
- Q&A systems needing complete context
- When retrieval quality > processing speed

---

## 2. Sliding Window with Overlap

### What It Is
Fixed-size chunks with **overlapping content** between consecutive chunks. Ensures context isn't lost at chunk boundaries.

### How It Works
```
Chunk 1: [0-500 chars]
Chunk 2: [400-900 chars]  # 100 char overlap
Chunk 3: [800-1300 chars] # 100 char overlap
```

### Parameters
- **Chunk size**: Fixed length (chars, tokens, or words)
- **Overlap**: Percentage or fixed amount of shared content
- **Typical ratios**: 10-20% overlap

### Tools/Libraries
- **LangChain**: `RecursiveCharacterTextSplitter(chunk_overlap=200)`
- **LlamaIndex**: `SentenceSplitter` with overlap settings
- **Native**: String slicing with offset

### Pros
- ✅ Simple and deterministic
- ✅ Prevents context loss at boundaries
- ✅ Predictable chunk sizes for batch processing
- ✅ Fast (no ML required)

### Cons
- ❌ May split mid-sentence/mid-thought
- ❌ Redundant storage (overlap = duplicate data)
- ❌ Fixed size doesn't respect content structure

### Best For
- Large uniform documents (logs, transcripts)
- When speed and simplicity matter
- Systems with limited computational resources

---

## 3. Hierarchical Chunking (Document → Sections → Paragraphs)

### What It Is
**Multi-level chunking** that preserves document structure. Creates parent-child relationships between chunks at different granularities.

### How It Works
```
Level 1: Document-level summary
  └── Level 2: Section chunks
       └── Level 3: Paragraph chunks
            └── Level 4: Sentence chunks
```

### Implementation Approaches
1. **Structure-aware**: Use Markdown headers, HTML tags, or document outline
2. **LLM-generated**: Extract hierarchy using GPT/Claude
3. **Hybrid**: Combine structural markers with semantic analysis

### Tools/Libraries
- **LlamaIndex**: `HierarchicalNodeParser` (built-in)
- **LangChain**: Custom chain with structure extraction
- **Custom**: Markdown parser + recursive splitting

### Retrieval Strategy
- **Multi-vector**: Store chunks at multiple levels
- **Query routing**: Route queries to appropriate granularity
- **Context expansion**: Retrieve small chunk, expand to parent section

### Pros
- ✅ Preserves document structure
- ✅ Flexible retrieval (coarse to fine-grained)
- ✅ Better context for complex queries
- ✅ Supports multi-hop reasoning

### Cons
- ❌ Complex implementation
- ❌ Increased storage (multiple levels)
- ❌ Requires structured documents or structure extraction
- ❌ Query routing logic needed

### Best For
- Long, structured documents (manuals, legal docs, research papers)
- Complex queries requiring context at multiple scales
- Multi-hop reasoning tasks

---

## 4. Parent-Child Chunking (Small Chunks, Big Context)

### What It Is
Index **small chunks** for precise retrieval, but return **larger parent chunks** for context. Balances retrieval precision with generation context.

### How It Works
```
Storage:
- Small chunk (100 tokens) → embedding, indexed
- Parent chunk (500 tokens) → stored but NOT embedded

Retrieval:
1. Query matches small chunk
2. Return parent chunk for LLM context
```

### Implementation Patterns

#### Pattern A: Small-to-Large
- Index: Sentences or small paragraphs
- Retrieve: Surrounding paragraph or section

#### Pattern B: Summary-to-Detail
- Index: Chunk summaries (LLM-generated)
- Retrieve: Full chunk content

#### Pattern C: Metadata-Expanded
- Index: Chunk + key metadata (headers, section titles)
- Retrieve: Chunk + parent context

### Tools/Libraries
- **LlamaIndex**: `HierarchicalNodeParser` + `AutoMergingRetriever`
- **LangChain**: ParentDocumentRetriever
- **Custom**: Two-stage retrieval with mapping table

### Pros
- ✅ Precise retrieval (small indexed chunks)
- ✅ Rich context for generation (large returned chunks)
- ✅ Reduces hallucinations from context gaps
- ✅ Best of both worlds (precision + context)

### Cons
- ❌ Increased storage (parent + child chunks)
- ❌ More complex retrieval logic
- ❌ May retrieve irrelevant parent context
- ❌ Requires tuning chunk size ratios

### Best For
- RAG systems where context quality is critical
- Documents with dense information (technical, legal, medical)
- When retrieval precision alone isn't enough

---

## Comparison Matrix

| Strategy | Speed | Precision | Context | Complexity | Storage |
|----------|-------|-----------|---------|------------|---------|
| Semantic | ⚠️ Slow | ✅ High | ✅ Good | ⚠️ Medium | ✅ Low |
| Sliding Window | ✅ Fast | ⚠️ Medium | ⚠️ Medium | ✅ Low | ⚠️ Medium |
| Hierarchical | ⚠️ Medium | ✅ High | ✅ Excellent | ❌ High | ❌ High |
| Parent-Child | ⚠️ Medium | ✅ High | ✅ Excellent | ⚠️ Medium | ⚠️ Medium |

---

## Recommendations by Use Case

### General Q&A Bot
- **Primary**: Semantic chunking
- **Fallback**: Sliding window with 15% overlap

### Technical Documentation
- **Primary**: Hierarchical (structure-aware)
- **Enhancement**: Parent-child for code examples

### Legal/Medical Documents
- **Primary**: Parent-child (sentences → paragraphs)
- **Enhancement**: Semantic for definition extraction

### Long-form Content (Articles, Papers)
- **Primary**: Hierarchical + semantic hybrid
- **Retrieval**: Multi-vector at section + paragraph levels

### Log/Transcript Analysis
- **Primary**: Sliding window with overlap
- **Fallback**: Fixed-size chunking (no overlap if sequential)

---

## Implementation Tips

### 1. Start Simple
Begin with sliding window + overlap, then iterate to more complex strategies.

### 2. Measure Quality
Use retrieval metrics (precision@k, MRR) and generation quality (human eval, LLM-as-judge).

### 3. Hybrid Approaches
Combine strategies:
- Semantic chunking → then apply hierarchical structure
- Sliding window → then group into parent chunks

### 4. Document-Aware
Choose strategy based on document type:
- Structured → Hierarchical
- Unstructured → Semantic
- Uniform → Sliding window

### 5. Test Edge Cases
- Very short documents (< 1 chunk)
- Very long documents (> 10k chunks)
- Code snippets, tables, lists (non-prose content)

---

## Key Takeaways

1. **No one-size-fits-all**: Strategy depends on document type and use case
2. **Context is king**: Parent-child and hierarchical preserve context best
3. **Precision vs recall tradeoff**: Smaller chunks = more precise, less context
4. **Test empirically**: RAG quality is highly dependent on chunking quality
5. **Consider hybrid**: Combine multiple strategies for best results

---

## Resources

- [LangChain Chunking Guide](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [LlamaIndex Node Parsers](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/)
- [Advanced RAG Techniques (LlamaIndex)](https://docs.llamaindex.ai/en/stable/optimizing/advanced_retrieval/advanced_retrieval/)
- [Semantic Chunking Paper](https://arxiv.org/abs/2305.08584)

---

**Generated**: 2026-03-05
**Purpose**: RAG research documentation - Chunking strategies chunk (1/5)

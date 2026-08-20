# Indexación y Chunking

Detalle de la fase de ingesta: el pipeline completo de indexación y las 4 estrategias de chunking.

## Contenido

- [Pipeline completo de indexación](#pipeline-completo-de-indexación) — flujo Loader → Chunker → Metadata → Embedding → Vector Store.
- [Estrategias de Chunking](#estrategias-de-chunking)
  - [1. Fixed-size](#1-fixed-size-simple-baseline)
  - [2. Recursive](#2-recursive-recomendado-para-código-y-prosa-mixta)
  - [3. Semantic](#3-semantic-mejor-calidad-más-lento)
  - [4. Parent-Child](#4-parent-child-mejor-recall--precisión)

---

## Pipeline completo de indexación

```
Documentos fuente
(PDF, DOCX, HTML, MD)
        │
        ▼
┌─────────────────┐
│  Document Loader │  → PyMuPDF, python-docx, BeautifulSoup, Unstructured
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Chunker      │  → estrategia según tipo de documento
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata       │  → source, page, section, timestamp, doc_type
│  Enrichment     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embedding      │  → text-embedding-3-small, nomic-embed, voyage-3
│  Model          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │  → pgvector (PostgreSQL) — ya en el stack de Cristian
│  (upsert)       │
└─────────────────┘
```

---

## Estrategias de Chunking

### 1. Fixed-size (simple, baseline)
```python
def fixed_chunk(text: str, size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        if chunk:
            chunks.append(chunk)
    return chunks
```

### 2. Recursive (recomendado para código y prosa mixta)
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,         # caracteres
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],  # orden de prioridad
    length_function=len
)

chunks = splitter.split_text(document_text)
```

### 3. Semantic (mejor calidad, más lento)
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

semantic_splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # cortar donde la similitud cae
    breakpoint_threshold_amount=95
)
```

### 4. Parent-Child (mejor recall + precisión)
```python
# Indexar chunks pequeños (para precisión en retrieval)
# pero retornar el chunk padre completo (para contexto al LLM)

PARENT_CHUNK_SIZE = 2000
CHILD_CHUNK_SIZE = 400

parent_splitter = RecursiveCharacterTextSplitter(chunk_size=PARENT_CHUNK_SIZE)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=CHILD_CHUNK_SIZE)

parent_chunks = parent_splitter.split_documents(docs)

for i, parent in enumerate(parent_chunks):
    children = child_splitter.split_documents([parent])
    for child in children:
        child.metadata["parent_id"] = i  # referencia al padre
        # Indexar child en vectorstore
        # Guardar parent en docstore para recuperar después
```

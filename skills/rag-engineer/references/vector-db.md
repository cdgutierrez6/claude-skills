# Vector Database — pgvector (stack nativo de Cristian)

Setup del store de embeddings en PostgreSQL + pgvector y las dos vías de retrieval: semántico puro e híbrido (semántico + BM25 con RRF).

## Contenido

- [Setup](#setup) — extensión, tabla `document_chunks`, índice HNSW, índice GIN de metadata.
- [Retrieval semántico](#retrieval-semántico) — embeddings con Voyage AI + búsqueda por distancia coseno.
- [Retrieval híbrido (semántico + BM25 keyword)](#retrieval-híbrido-semántico--bm25-keyword) — full-text `tsvector` + Reciprocal Rank Fusion.

---

## Setup
```sql
-- Habilitar extensión (PostgreSQL + pgvector ya instalado)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de embeddings
CREATE TABLE document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    doc_id      UUID NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(1536),      -- OpenAI text-embedding-3-small
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Índice HNSW (mejor performance para búsqueda aproximada)
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Índice para filtrado por metadata
CREATE INDEX ON document_chunks USING gin(metadata);
```

## Retrieval semántico
```python
import psycopg2
import numpy as np
from anthropic import Anthropic

# Usamos voyage-3 o text-embedding-3-small para embeddings
# Claude no tiene endpoint de embeddings propio — usar Voyage AI (Anthropic recomendado)
import voyageai

voyage_client = voyageai.Client()  # VOYAGE_API_KEY en .env

def embed_text(text: str) -> list[float]:
    result = voyage_client.embed([text], model="voyage-3")
    return result.embeddings[0]

def semantic_search(
    query: str,
    top_k: int = 5,
    filter_metadata: dict | None = None,
    conn: psycopg2.extensions.connection = None
) -> list[dict]:
    query_embedding = embed_text(query)
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    where_clause = ""
    params = [embedding_str, top_k]

    if filter_metadata:
        where_clause = "WHERE metadata @> %s"
        params.insert(1, psycopg2.extras.Json(filter_metadata))

    sql = f"""
    SELECT
        id,
        content,
        metadata,
        1 - (embedding <=> %s::vector) AS similarity
    FROM document_chunks
    {where_clause}
    ORDER BY embedding <=> %s::vector
    LIMIT %s
    """
    params.append(embedding_str)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()
```

## Retrieval híbrido (semántico + BM25 keyword)
```sql
-- Habilitar búsqueda full-text en PostgreSQL
ALTER TABLE document_chunks
ADD COLUMN content_tsv tsvector
GENERATED ALWAYS AS (to_tsvector('spanish', content)) STORED;

CREATE INDEX ON document_chunks USING gin(content_tsv);
```

```python
def hybrid_search(
    query: str,
    top_k: int = 5,
    semantic_weight: float = 0.7,  # 70% semántico, 30% keyword
    conn = None
) -> list[dict]:
    query_embedding = embed_text(query)
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    # Combinar rankings con RRF (Reciprocal Rank Fusion)
    sql = """
    WITH semantic_results AS (
        SELECT id, content, metadata,
               1 - (embedding <=> %s::vector) AS semantic_score,
               ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS sem_rank
        FROM document_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT 20
    ),
    keyword_results AS (
        SELECT id, content, metadata,
               ts_rank(content_tsv, query) AS keyword_score,
               ROW_NUMBER() OVER (ORDER BY ts_rank(content_tsv, query) DESC) AS kw_rank
        FROM document_chunks,
             plainto_tsquery('spanish', %s) AS query
        WHERE content_tsv @@ query
        ORDER BY keyword_score DESC
        LIMIT 20
    ),
    rrf_scores AS (
        SELECT
            COALESCE(s.id, k.id) AS id,
            COALESCE(s.content, k.content) AS content,
            COALESCE(s.metadata, k.metadata) AS metadata,
            COALESCE(1.0 / (60 + s.sem_rank), 0) * %s +
            COALESCE(1.0 / (60 + k.kw_rank), 0) * (1 - %s) AS rrf_score
        FROM semantic_results s
        FULL OUTER JOIN keyword_results k ON s.id = k.id
    )
    SELECT id, content, metadata, rrf_score
    FROM rrf_scores
    ORDER BY rrf_score DESC
    LIMIT %s
    """

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, [
            embedding_str, embedding_str, embedding_str,
            query, semantic_weight, semantic_weight, top_k
        ])
        return cur.fetchall()
```

# RAG Pipeline completo (FastAPI + Claude)

Endpoint end-to-end que une retrieval (semántico o híbrido) → construcción de contexto → generación aumentada con Claude, con system prompt anti-alucinación y citación de fuentes.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from anthropic import Anthropic
import psycopg2

app = FastAPI()
claude = Anthropic()

SYSTEM_PROMPT = """Eres un asistente experto que responde preguntas basándose
EXCLUSIVAMENTE en el contexto proporcionado. Si la información no está en el
contexto, di "No tengo información sobre eso en mis documentos."

Reglas:
- Cita la fuente cuando sea posible (metadata.source)
- No inventes información que no esté en el contexto
- Responde en el mismo idioma de la pregunta"""

class RAGRequest(BaseModel):
    question: str
    top_k: int = 5
    use_hybrid: bool = True

@app.post("/rag/query")
async def rag_query(request: RAGRequest):
    # 1. Retrieval
    if request.use_hybrid:
        chunks = hybrid_search(request.question, top_k=request.top_k, conn=get_db())
    else:
        chunks = semantic_search(request.question, top_k=request.top_k, conn=get_db())

    if not chunks:
        return {"answer": "No encontré información relevante.", "sources": []}

    # 2. Context building
    context = "\n\n---\n\n".join([
        f"[Fuente: {c['metadata'].get('source', 'desconocida')}]\n{c['content']}"
        for c in chunks
    ])

    # 3. Augmented generation
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Contexto:\n{context}\n\nPregunta: {request.question}"
        }]
    )

    return {
        "answer": response.content[0].text,
        "sources": [c["metadata"].get("source") for c in chunks],
        "chunks_used": len(chunks)
    }
```

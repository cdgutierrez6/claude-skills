# Advanced & Agentic RAG

Técnicas para subir precisión/recall por encima del naive RAG, más el patrón agentic con self-correction en LangGraph.

## Contenido

- [HyDE (Hypothetical Document Embeddings)](#hyde-hypothetical-document-embeddings) — genera un doc hipotético y busca con su embedding; mejora recall en preguntas vagas.
- [Reranking con Cross-Encoder](#reranking-con-cross-encoder) — reordena top_k con un modelo discriminativo más preciso.
- [Self-Query (filtrado automático por metadata)](#self-query-filtrado-automático-por-metadata) — Claude extrae filtros de la pregunta en lenguaje natural.
- [Agentic RAG con LangGraph](#agentic-rag-con-langgraph) — retrieve → grade → refine/generate con iteración limitada.

---

## HyDE (Hypothetical Document Embeddings)
```python
def hyde_search(query: str, top_k: int = 5, conn=None) -> list[dict]:
    """
    Genera un documento hipotético que respondería la query,
    luego usa su embedding para buscar — mejora recall en preguntas vagas.
    """
    # Paso 1: generar documento hipotético
    hypothetical = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"Escribe un párrafo técnico corto que respondería esta pregunta: {query}"
        }]
    ).content[0].text

    # Paso 2: buscar con el embedding del documento hipotético
    return semantic_search(hypothetical, top_k=top_k, conn=conn)
```

## Reranking con Cross-Encoder
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

def rerank_results(query: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    """Reordena los chunks con un modelo discriminativo más preciso."""
    pairs = [(query, c["content"]) for c in chunks]
    scores = reranker.predict(pairs)

    scored_chunks = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [chunk for chunk, _ in scored_chunks[:top_k]]
```

## Self-Query (filtrado automático por metadata)
```python
def self_query_rag(question: str, conn=None) -> list[dict]:
    """Claude extrae filtros de metadata de la pregunta en lenguaje natural."""
    filter_response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system='Extrae filtros de metadata de la pregunta. Responde SOLO en JSON: {"doc_type": null|"pdf"|"html"|"md", "date_from": null|"YYYY-MM-DD", "source": null|"string"}',
        messages=[{"role": "user", "content": question}]
    ).content[0].text

    import json
    filters = {k: v for k, v in json.loads(filter_response).items() if v is not None}

    return semantic_search(question, filter_metadata=filters if filters else None, conn=conn)
```

---

## Agentic RAG con LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class RAGState(TypedDict):
    question: str
    retrieved_chunks: list[dict]
    answer: str
    needs_refinement: bool
    iterations: int

def retrieve_node(state: RAGState) -> RAGState:
    chunks = hybrid_search(state["question"], top_k=5)
    return {**state, "retrieved_chunks": chunks}

def grade_node(state: RAGState) -> RAGState:
    """Claude evalúa si los chunks son relevantes."""
    chunks_summary = "\n".join([c["content"][:200] for c in state["retrieved_chunks"]])
    grade = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": f"¿Los chunks son relevantes para '{state['question']}'? Solo responde YES o NO.\n\nChunks: {chunks_summary}"
        }]
    ).content[0].text.strip()

    return {**state, "needs_refinement": "NO" in grade.upper()}

def generate_node(state: RAGState) -> RAGState:
    context = "\n\n".join([c["content"] for c in state["retrieved_chunks"]])
    answer = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Contexto:\n{context}\n\nPregunta: {state['question']}"}]
    ).content[0].text

    return {**state, "answer": answer}

def refine_query_node(state: RAGState) -> RAGState:
    """Reformula la query si los chunks no fueron relevantes."""
    refined = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"Reformula esta pregunta con términos más específicos para búsqueda: {state['question']}"
        }]
    ).content[0].text

    return {**state, "question": refined, "iterations": state.get("iterations", 0) + 1}

def should_refine(state: RAGState) -> str:
    if state.get("needs_refinement") and state.get("iterations", 0) < 2:
        return "refine"
    return "generate"

# Construir el grafo
workflow = StateGraph(RAGState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade", grade_node)
workflow.add_node("generate", generate_node)
workflow.add_node("refine", refine_query_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges("grade", should_refine, {"refine": "refine", "generate": "generate"})
workflow.add_edge("refine", "retrieve")
workflow.add_edge("generate", END)

agentic_rag = workflow.compile()
```

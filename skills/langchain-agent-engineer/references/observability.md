# LangSmith — Observabilidad y evaluación de agentes

Tracing automático (inputs, outputs, latencia, tokens, tool calls, errores) y evaluación
programática de la calidad del agente antes de deploy.

## LangSmith — Observabilidad de agentes

```python
import os

# Configurar LangSmith (tracing automático)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."  # En .env
os.environ["LANGCHAIN_PROJECT"] = "efiziai-ai-agents"

# Todo lo que ejecutes con LangChain ahora queda traced en LangSmith
# Incluye: inputs, outputs, latencia, tokens, tool calls, errores

# Evaluación programática
from langsmith import Client
from langsmith.evaluation import evaluate

ls_client = Client()

def correctness_evaluator(run, example) -> dict:
    """Evalúa si la respuesta del agente es correcta."""
    score = llm.invoke(f"""
    Pregunta: {example.inputs['question']}
    Respuesta correcta: {example.outputs['answer']}
    Respuesta del agente: {run.outputs['output']}

    ¿La respuesta del agente es correcta? Responde: correct / incorrect
    """).content

    return {"score": 1 if "correct" in score.lower() else 0, "key": "correctness"}

results = evaluate(
    lambda x: executor.invoke(x),
    data="mi-dataset-de-evaluacion",
    evaluators=[correctness_evaluator],
    experiment_prefix="agente-v2"
)
```

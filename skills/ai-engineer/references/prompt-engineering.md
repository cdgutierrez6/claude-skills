# Prompt Engineering — Técnicas de producción

## Contenido

1. System Prompt efectivo (Role + Context + Constraints)
2. Chain of Thought explícito
3. Few-Shot con formato exacto
4. Structured Output con Pydantic (Python)

---

### 1. System Prompt efectivo (Role + Context + Constraints)
```python
SYSTEM_PROMPT = """
Eres un {role} con 10+ años en {domain}.
Contexto del sistema: {system_description}
Restricciones innegociables:
- {constraint_1}
- {constraint_2}
Output esperado: {format_spec}
"""
```

### 2. Chain of Thought explícito
```python
messages = [{
    "role": "user",
    "content": f"""
Problema: {problem}

Piensa paso a paso:
1. Identifica las variables clave
2. Evalúa las alternativas posibles
3. Descarta enfoques sub-óptimos
4. Presenta la solución con justificación

IMPORTANTE: Muestra tu razonamiento completo antes de la conclusión.
"""
}]
```

### 3. Few-Shot con formato exacto
```python
FEW_SHOT = """
Analiza el siguiente fragmento de código y responde SOLO en este formato:

EJEMPLO:
INPUT: función sin manejo de errores async
SEVERIDAD: alta
ISSUE: Promesa rechazada silenciosa — crash en producción bajo carga
FIX: try/catch explícito + log estructurado del error
PREVENCIÓN: ESLint rule @typescript-eslint/no-floating-promises

Ahora analiza:
INPUT: {code_fragment}
"""
```

### 4. Structured Output con Pydantic (Python)
```python
from pydantic import BaseModel
import anthropic
import json

class CodeReview(BaseModel):
    severity: str  # "low" | "medium" | "high" | "critical"
    issues: list[str]
    verdict: str  # "APPROVED" | "REJECTED"
    blockers: list[str]

client = anthropic.Anthropic()

# Forzar JSON estructurado via prefill
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system="Eres un Tech Lead Senior. Responde SOLO en JSON válido sin texto adicional.",
    messages=[
        {"role": "user", "content": f"Revisa este código:\n\n{code}"},
        {"role": "assistant", "content": "{"}  # Prefill para forzar JSON
    ]
)

raw = "{" + response.content[0].text
review = CodeReview.model_validate_json(raw)
```

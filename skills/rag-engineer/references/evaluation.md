# Evaluación RAG con RAGAS

Medición cuantitativa de calidad antes de producción: faithfulness, answer_relevancy, context_recall, context_precision sobre un dataset con ground truth manual.

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from datasets import Dataset

# Dataset de evaluación
eval_data = {
    "question": ["¿Qué es el producto?", "¿Cómo funciona el scoring de leads?"],
    "answer": [actual_answers...],       # respuestas generadas por tu RAG
    "contexts": [retrieved_contexts...], # chunks usados para cada respuesta
    "ground_truth": [correct_answers...] # respuestas correctas (ground truth manual)
}

dataset = Dataset.from_dict(eval_data)

results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision]
)

print(results)
# faithfulness:       0.92  (el LLM no alucina fuera del contexto)
# answer_relevancy:   0.88  (la respuesta es relevante a la pregunta)
# context_recall:     0.85  (el retrieval trae el contexto necesario)
# context_precision:  0.79  (los chunks son precisos, no hay ruido)
```

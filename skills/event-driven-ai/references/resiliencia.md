# Resiliencia — DLQ y Circuit Breaker

## Contenido
- [Dead Letter Queue (DLQ)](#dead-letter-queue-dlq--resiliencia)
- [Circuit breaker para AI workers](#patrones-de-resiliencia-para-ai-workers)

---

## Dead Letter Queue (DLQ) — Resiliencia

```python
# Consumer que maneja mensajes fallidos del DLQ
def run_dlq_handler():
    consumer = create_ai_consumer(
        topics=["crm.ai-errors.dlq"],
        group_id="dlq-ai-handler"
    )

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue

        event = json.loads(msg.value())
        original_event = event["original_event"]
        error_count = event.get("error_count", 0)

        if error_count >= 5:
            # Notificar a Cristian vía n8n → Slack/email
            notify_dead_event(original_event)
            consumer.commit()
            continue

        try:
            # Reintento con modelo más capaz (Sonnet en lugar de Haiku)
            result = process_with_fallback_model(original_event, model="claude-sonnet-4-6")
            publish_to_output_topic(result)
            consumer.commit()
        except Exception as e:
            # Volver al DLQ con contador incrementado
            republish_to_dlq(original_event, error_count + 1, str(e))
            consumer.commit()
```

---

## Patrones de resiliencia para AI workers

```python
import time
from functools import wraps
from typing import Callable, TypeVar

T = TypeVar("T")

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60
):
    """Circuit breaker para llamadas a Claude API."""
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        failures = 0
        last_failure_time = None
        is_open = False

        @wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            nonlocal failures, last_failure_time, is_open

            if is_open:
                elapsed = time.time() - last_failure_time
                if elapsed < recovery_timeout:
                    raise Exception("Circuit breaker OPEN — usando fallback")
                # Half-open: intentar recuperación
                is_open = False
                failures = 0

            try:
                result = fn(*args, **kwargs)
                failures = 0  # Reset en éxito
                return result
            except Exception as e:
                failures += 1
                last_failure_time = time.time()
                if failures >= failure_threshold:
                    is_open = True
                raise

        return wrapper
    return decorator

@circuit_breaker(failure_threshold=5, recovery_timeout=60)
def call_claude(prompt: str) -> str:
    client = Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

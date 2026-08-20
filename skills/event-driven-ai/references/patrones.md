# Patrones — Consumer Kafka, CQRS y Saga

## Contenido
- [Patrón Base — Kafka AI Consumer (Python)](#patrón-base--kafka-ai-consumer-python)
- [Patrón CQRS para sistemas AI](#patrón-cqrs-para-sistemas-ai)
- [Event Store con PostgreSQL](#event-store-con-postgresql)
- [Saga Pattern — Orquestación multi-agente](#saga-pattern--orquestación-multi-agente)

---

## Patrón Base — Kafka AI Consumer (Python)

```python
from confluent_kafka import Consumer, Producer, KafkaError
from anthropic import Anthropic
import json
import logging

logger = logging.getLogger(__name__)
client = Anthropic()

def create_ai_consumer(
    topics: list[str],
    group_id: str,
    bootstrap_servers: str = "localhost:9092"
) -> Consumer:
    return Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,  # commit manual — solo después de procesar
        "max.poll.interval.ms": 300000  # 5 min — AI puede ser lento
    })

def process_lead_captured_event(event_data: dict) -> dict:
    """Analiza un lead recién capturado con Claude y retorna el scoring."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # Haiku: rápido y barato para scoring
        max_tokens=512,
        system="""Eres un analizador de leads B2B. Responde SOLO en JSON con este formato:
{
  "score": <número 1-100>,
  "tier": "hot|warm|cold",
  "reasoning": "<string corto>",
  "next_action": "call|email|nurture|discard"
}""",
        messages=[{
            "role": "user",
            "content": f"Analiza este lead: {json.dumps(event_data)}"
        }]
    )

    return json.loads(response.content[0].text)

def run_ai_consumer():
    consumer = create_ai_consumer(
        topics=["crm.leads.captured"],
        group_id="ai-lead-scorer"
    )
    producer = Producer({"bootstrap.servers": "localhost:9092"})

    try:
        consumer.subscribe(["crm.leads.captured"])

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise Exception(f"Kafka error: {msg.error()}")

            try:
                event = json.loads(msg.value().decode("utf-8"))
                lead_id = event.get("lead_id")

                logger.info(f"Procesando lead {lead_id}")
                ai_result = process_lead_captured_event(event)

                # Publicar resultado al topic de output
                output_event = {
                    "lead_id": lead_id,
                    "event_type": "LeadScored",
                    "score": ai_result["score"],
                    "tier": ai_result["tier"],
                    "next_action": ai_result["next_action"],
                    "reasoning": ai_result["reasoning"]
                }

                producer.produce(
                    "crm.leads.scored",
                    key=str(lead_id),
                    value=json.dumps(output_event)
                )
                producer.flush()

                # Commit solo si todo salió bien
                consumer.commit(asynchronous=False)
                logger.info(f"Lead {lead_id} procesado: tier={ai_result['tier']}")

            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                # No hacer commit → mensaje vuelve a la cola para reintento
                # Después de N reintentos → DLQ automático (configurar en Kafka)

    finally:
        consumer.close()

if __name__ == "__main__":
    run_ai_consumer()
```

---

## Patrón CQRS para sistemas AI

```
Modelo de escritura (Commands)          Modelo de lectura (Queries)
─────────────────────────────           ────────────────────────────
POST /leads → LeadCaptured              GET /leads/:id/analysis → ReadModel
POST /messages → MessageSent            GET /conversations/:id/summary → ReadModel
                   │                                    ▲
                   ▼                                    │
            Kafka Topic                          Projection Service
         (event store)           ───────►        (actualiza vistas
                   │                              con outputs AI)
                   ▼
            AI Workers
         (consumers Kafka)
         ┌──────────────┐
         │ Lead Scorer  │ → crm.leads.scored
         │ Responder    │ → crm.messages.responses
         │ Summarizer   │ → crm.conversations.summaries
         └──────────────┘
```

## Event Store con PostgreSQL
```sql
-- Tabla de eventos inmutables (append-only)
CREATE TABLE domain_events (
    id          BIGSERIAL PRIMARY KEY,
    event_type  VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    payload     JSONB NOT NULL,
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_aggregate ON domain_events(aggregate_type, aggregate_id, created_at);
CREATE INDEX idx_events_type_time ON domain_events(event_type, created_at);

-- Read model para leads con scoring AI
CREATE TABLE lead_read_model (
    lead_id     UUID PRIMARY KEY,
    company     VARCHAR(255),
    email       VARCHAR(255),
    ai_score    INTEGER,
    ai_tier     VARCHAR(10),
    next_action VARCHAR(20),
    last_scored TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Saga Pattern — Orquestación multi-agente

```python
# Saga: Lead Qualification Workflow
# LeadCaptured → Score → Enrich → Assign → Notify

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any

class SagaStep(Enum):
    SCORE_LEAD = "score_lead"
    ENRICH_LEAD = "enrich_lead"
    ASSIGN_AGENT = "assign_agent"
    SEND_NOTIFICATION = "send_notification"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SagaState:
    lead_id: str
    step: SagaStep
    data: dict[str, Any]
    retries: int = 0
    max_retries: int = 3

async def execute_saga(lead_data: dict) -> SagaState:
    state = SagaState(
        lead_id=lead_data["lead_id"],
        step=SagaStep.SCORE_LEAD,
        data=lead_data
    )

    steps = [
        (SagaStep.SCORE_LEAD, score_lead_with_ai),
        (SagaStep.ENRICH_LEAD, enrich_lead_with_ai),
        (SagaStep.ASSIGN_AGENT, assign_sales_agent),
        (SagaStep.SEND_NOTIFICATION, send_welcome_sequence),
    ]

    for step_enum, step_fn in steps:
        state.step = step_enum
        try:
            state.data = await step_fn(state.data)
        except Exception as e:
            if state.retries < state.max_retries:
                state.retries += 1
                await asyncio.sleep(2 ** state.retries)
                # Reintentar el mismo paso
                state.data = await step_fn(state.data)
            else:
                state.step = SagaStep.FAILED
                # Publicar evento de compensación
                await publish_compensation_event(state, str(e))
                return state

    state.step = SagaStep.COMPLETED
    return state

async def score_lead_with_ai(data: dict) -> dict:
    """Paso 1: scoring con Claude Haiku."""
    client = Anthropic()
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": f"Score este lead 1-100: {data}"}]
    )
    data["ai_score"] = int(response.content[0].text.strip())
    return data
```

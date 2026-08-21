# Integración, Observabilidad y Arquitectura de referencia

## Contenido
- [Integración con n8n (EfiziAI)](#integración-con-n8n-efiziai)
- [Observabilidad de pipelines AI](#observabilidad-de-pipelines-ai)
- [Arquitectura de referencia — EfiziAI Event-Driven AI](#arquitectura-de-referencia--efiziai-event-driven-ai)

---

## Integración con n8n (EfiziAI)

```
n8n Workflow: "AI Lead Processor"
─────────────────────────────────
[Kafka Trigger]          ← topic: crm.leads.captured
    │
    ▼
[HTTP Request]           → POST https://<api-interna>/ai/score-lead
    │                      Body: { lead_id, company, email, niche }
    ▼
[IF node]                → score >= 70 → "hot lead" branch
    │                    → score < 70  → "nurture" branch
    ▼                         ▼
[Kafka Produce]          [Kafka Produce]
crm.leads.hot            crm.leads.nurture
    │
    ▼
[HTTP Request]           → POST /api/notifications/assign-agent
```

---

## Observabilidad de pipelines AI

```python
import time
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("ai-event-pipeline")

def process_event_with_tracing(event: dict) -> dict:
    with tracer.start_as_current_span("ai.process_event") as span:
        span.set_attribute("event.type", event.get("event_type"))
        span.set_attribute("event.aggregate_id", event.get("lead_id", ""))

        start = time.time()
        try:
            result = call_claude(build_prompt(event))
            duration_ms = (time.time() - start) * 1000

            span.set_attribute("ai.model", "claude-sonnet-4-6")
            span.set_attribute("ai.duration_ms", duration_ms)
            span.set_attribute("ai.success", True)
            span.set_status(Status(StatusCode.OK))

            return parse_result(result)

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
```

---

## Arquitectura de referencia — EfiziAI Event-Driven AI

```
                    ┌──────────────────────────────────┐
                    │         EfiziAI CRM              │
                    │   (Node.js + Express + React)    │
                    └─────────────┬────────────────────┘
                                  │ Produce eventos
                                  ▼
                    ┌──────────────────────────────────┐
                    │         Kafka KRaft               │
                    │  Topics:                         │
                    │  crm.leads.captured              │
                    │  crm.messages.sent               │
                    │  crm.conversations.updated       │
                    └──┬───────────┬──────────────┬───┘
                       │           │              │
              ┌────────▼───┐ ┌─────▼────┐ ┌──────▼──────┐
              │Lead Scorer │ │Responder │ │ Summarizer  │
              │(Python/    │ │(Python/  │ │ (Python/    │
              │Claude Haiku│ │Sonnet)   │ │ Haiku)      │
              └────────┬───┘ └─────┬────┘ └──────┬──────┘
                       │           │              │
                       └───────────┴──────────────┘
                                   │ Produce outputs
                                   ▼
                    ┌──────────────────────────────────┐
                    │    Output Topics                  │
                    │  crm.leads.scored                │
                    │  crm.messages.responses          │
                    │  crm.conversations.summaries     │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │     n8n Projection Worker         │
                    │  (actualiza PostgreSQL + notifica)│
                    └──────────────────────────────────┘
```

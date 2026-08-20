# Fundamentos — EDA + AI

## ¿Por qué Event-Driven para AI?

| Arquitectura síncrona (REST) | Arquitectura orientada a eventos |
|---|---|
| AI bloquea la request del usuario | AI procesa en background, sin bloqueo |
| Timeout si el LLM es lento | Resiliencia via reintentos en la cola |
| Un solo consumidor | Múltiples agentes AI en paralelo |
| Difícil de auditar | Event log = trazabilidad completa |
| Escalado vertical | Escalado horizontal de consumers |

## Taxonomía de eventos en sistemas AI

```
Tipo          Ejemplo                              Productor → Consumidor
────────────────────────────────────────────────────────────────────────
DomainEvent   LeadCaptured, MessageSent            CRM → AI Agent
CommandEvent  AnalyzeLead, GenerateResponse        Orchestrator → AI Worker
QueryEvent    SummarizeConversation                Frontend → AI Service
AIOutputEvent LeadScored, ResponseGenerated        AI Worker → CRM / n8n
ErrorEvent    AIProcessingFailed                   AI Worker → DLQ Handler
```

# Costos, caching y checklist de deploy

## Contenido

1. Prompt Caching (reducción de costos hasta 90%)
2. Optimización de costos (tabla de técnicas)
3. Checklist pre-deploy de un sistema con Claude

---

## Prompt Caching (reducción de costos hasta 90%)
```python
# Cache para system prompts largos o documentos de contexto
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LARGE_SYSTEM_PROMPT,  # El prompt que se repite en cada request
            "cache_control": {"type": "ephemeral"}  # TTL: 5 minutos
        }
    ],
    messages=[{"role": "user", "content": user_query}]
)

# Monitorear uso de caché
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
print(f"Cache write tokens: {response.usage.cache_creation_input_tokens}")
```

**Cuándo usar caché:**
- System prompts > 1,024 tokens (umbral mínimo)
- Documentos RAG grandes pasados como contexto
- Instrucciones de herramientas extensas
- Historial de conversación largo y estable

## Optimización de costos

| Técnica | Reducción estimada |
|---|---|
| Prompt caching en system prompts | 50–90% en tokens de entrada |
| Haiku para clasificación/routing | 10–20x más barato que Sonnet |
| `max_tokens` ajustado (no usar 4096 por default) | 20–40% |
| Batch API para tareas no urgentes | 50% descuento |
| Comprimir contexto con resúmenes | 30–60% en conversaciones largas |

## Checklist pre-deploy de un sistema con Claude
```
[ ] ANTHROPIC_API_KEY en .env (nunca hardcodeado)
[ ] model ID en variable de entorno (ANTHROPIC_MODEL)
[ ] max_tokens apropiado para el caso de uso (no siempre 4096)
[ ] Manejo de RateLimitError con exponential backoff
[ ] Logging de usage.input_tokens y usage.output_tokens para monitoreo de costos
[ ] Prompt caching activado si el system prompt > 1024 tokens
[ ] Timeout configurado (client = Anthropic(timeout=30.0))
[ ] Tests con respuestas mockeadas (no llamar API real en CI)
[ ] Rate limiting propio si el endpoint es público
```

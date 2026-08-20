# Anthropic SDK — Patrones de producción (SDK, streaming, multimodal, resiliencia)

## Contenido

1. SDK — Python (llamada básica)
2. SDK — Node.js (llamada básica)
3. Streaming
4. SSE con FastAPI
5. Multimodal — Visión y Documentos
6. Manejo de errores y resiliencia

---

## Python SDK
```python
import anthropic
from anthropic import Anthropic

client = Anthropic()  # Lee ANTHROPIC_API_KEY del entorno

# Llamada básica
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="Eres un asistente experto en análisis de datos.",
    messages=[{"role": "user", "content": "Analiza esta serie temporal..."}]
)
print(message.content[0].text)
```

## Node.js SDK
```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // ANTHROPIC_API_KEY desde env

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  system: "Eres un AI Engineer Senior.",
  messages: [{ role: "user", content: "Diseña la arquitectura del sistema RAG." }],
});
console.log(message.content[0].text);
```

## Streaming
```python
# Streaming para respuestas largas (UX crítico)
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
        # En FastAPI: yield text para SSE
```

### SSE con FastAPI
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": request.message}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Multimodal — Visión y Documentos
```python
import base64

# Imagen desde archivo
with open("imagen.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data,
                }
            },
            {
                "type": "text",
                "text": "Analiza este diagrama de arquitectura e identifica posibles cuellos de botella."
            }
        ]
    }]
)
```

## Manejo de errores y resiliencia
```python
import anthropic
import time
from typing import Optional

def call_claude_with_retry(
    messages: list,
    model: str = "claude-sonnet-4-6",
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Optional[str]:
    client = anthropic.Anthropic()

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                messages=messages
            )
            return response.content[0].text

        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # exponential backoff
            time.sleep(delay)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:  # errores de servidor — reintentar
                if attempt == max_retries - 1:
                    raise
                time.sleep(base_delay * (2 ** attempt))
            else:
                raise  # errores 4xx — no reintentar

    return None
```

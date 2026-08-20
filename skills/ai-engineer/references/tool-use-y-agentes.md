# Tool Use / Function Calling

## Contenido

1. Definición de herramientas
2. Agentic Loop completo

---

## Definición de herramientas
```python
tools = [
    {
        "name": "search_database",
        "description": "Busca registros en la base de datos de clientes. Úsalo cuando necesites información específica de un cliente o conjunto de clientes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Término de búsqueda (nombre, email, o ID de cliente)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de resultados (default: 10)",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "send_email",
        "description": "Envía un email a un cliente. Solo usar cuando el usuario confirme explícitamente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Email del destinatario"},
                "subject": {"type": "string"},
                "body": {"type": "string", "description": "Cuerpo del email en texto plano"}
            },
            "required": ["to", "subject", "body"]
        }
    }
]
```

## Agentic Loop completo
```python
import anthropic
from typing import Callable

def run_agent(
    user_message: str,
    tools: list[dict],
    tool_handlers: dict[str, Callable],
    model: str = "claude-sonnet-4-6",
    max_iterations: int = 10
) -> str:
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_message}]

    for iteration in range(max_iterations):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # Caso: respuesta final sin herramientas
        if response.stop_reason == "end_turn":
            return next(
                (block.text for block in response.content if hasattr(block, "text")),
                ""
            )

        # Caso: Claude quiere usar una herramienta
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    handler = tool_handlers.get(block.name)
                    if not handler:
                        result = f"Error: herramienta '{block.name}' no registrada"
                    else:
                        try:
                            result = handler(**block.input)
                        except Exception as e:
                            result = f"Error ejecutando {block.name}: {str(e)}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Error: máximo de iteraciones alcanzado"
```

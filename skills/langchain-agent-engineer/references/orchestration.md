# Orquestación multi-agente y patrones avanzados

Cuando un solo agente no basta: supervisor que enruta a workers especializados, y
patrones de razonamiento (auto-crítica, planificar-ejecutar) para tareas complejas.

## Contenido

- [Multi-Agente con LangGraph (Supervisor Pattern)](#multi-agente-con-langgraph-supervisor-pattern)
- [Reflection Agent (auto-crítica)](#reflection-agent-auto-crítica)
- [Planner-Executor (tareas complejas multi-step)](#planner-executor-tareas-complejas-multi-step)

---

## Multi-Agente con LangGraph (Supervisor Pattern)

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Literal

# State compartido entre todos los agentes
class SupervisorState(TypedDict):
    messages: list[BaseMessage]
    next_agent: str
    final_answer: str

# Agentes especializados
def lead_analyst(state: SupervisorState) -> SupervisorState:
    """Analiza leads con herramientas de CRM."""
    result = lead_agent_executor.invoke({"input": state["messages"][-1].content})
    return {**state, "messages": state["messages"] + [AIMessage(content=result["output"])]}

def email_writer(state: SupervisorState) -> SupervisorState:
    """Redacta emails de seguimiento."""
    result = email_chain.invoke({"context": state["messages"]})
    return {**state, "messages": state["messages"] + [AIMessage(content=result)]}

def supervisor(state: SupervisorState) -> SupervisorState:
    """Decide qué agente activar a continuación."""
    response = llm.invoke([
        HumanMessage(content=f"""
Historial: {state['messages']}

¿Qué agente debe actuar ahora? Responde SOLO con el nombre:
- lead_analyst: para buscar/analizar leads
- email_writer: para redactar emails
- FINISH: si la tarea está completa
""")
    ])

    next_agent = response.content.strip()
    return {**state, "next_agent": next_agent}

def route_to_agent(state: SupervisorState) -> Literal["lead_analyst", "email_writer", "__end__"]:
    if state["next_agent"] == "FINISH":
        return END
    return state["next_agent"]

# Construir grafo multi-agente
workflow = StateGraph(SupervisorState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("lead_analyst", lead_analyst)
workflow.add_node("email_writer", email_writer)

workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_to_agent)
workflow.add_edge("lead_analyst", "supervisor")
workflow.add_edge("email_writer", "supervisor")

multi_agent = workflow.compile()
```

---

## Patrones avanzados de agentes

### Reflection Agent (auto-crítica)
```python
def reflection_agent(task: str, max_reflections: int = 3) -> str:
    answer = basic_chain.invoke({"task": task})

    for i in range(max_reflections):
        critique = llm.invoke(f"""
Tarea original: {task}
Respuesta generada: {answer}

Critica esta respuesta:
- ¿Es correcta?
- ¿Qué falta?
- ¿Hay errores?

Si es perfecta, responde solo: APROBADO
Si necesita mejora, describe qué cambiar.
""").content

        if "APROBADO" in critique:
            break

        answer = llm.invoke(f"""
Tarea: {task}
Respuesta anterior: {answer}
Crítica: {critique}

Genera una respuesta mejorada:
""").content

    return answer
```

### Planner-Executor (tareas complejas multi-step)
```python
def plan_and_execute(objective: str) -> str:
    # Fase 1: Planning
    plan = llm.invoke(f"""
Objetivo: {objective}
Crea un plan de máximo 5 pasos. Formato:
1. [acción concreta]
2. [acción concreta]
...
""").content

    steps = [line for line in plan.split("\n") if line.strip().startswith(tuple("12345"))]

    # Fase 2: Execution
    results = []
    context = ""

    for step in steps:
        result = executor.invoke({
            "input": step,
            "context": context
        })["output"]
        results.append(f"{step}: {result}")
        context += f"\n{step} → {result}"

    # Fase 3: Synthesis
    return llm.invoke(f"""
Objetivo: {objective}
Resultados: {chr(10).join(results)}

Sintetiza una respuesta final coherente:
""").content
```

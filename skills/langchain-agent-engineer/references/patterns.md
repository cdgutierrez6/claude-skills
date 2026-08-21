# Patrones base — chains y agentes de un solo actor

Bloques de construcción fundamentales: instalar el stack, un agente ReAct/tool-calling
con Claude, LCEL para componer chains, y un grafo LangGraph con estado.

## Contenido

- [Instalación del stack](#instalación-del-stack)
- [Agente ReAct básico con Claude](#agente-react-básico-con-claude)
- [LCEL — LangChain Expression Language](#lcel--langchain-expression-language)
- [LangGraph — Agentes con estado](#langgraph--agentes-con-estado)

---

## Instalación del stack

```bash
pip install langchain langchain-anthropic langgraph langsmith langchain-community
pip install langchain-postgres  # para pgvector
```

---

## Agente ReAct básico con Claude

```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0,
    max_tokens=4096
)

# Herramientas
search = DuckDuckGoSearchRun()

@tool
def search_crm_database(query: str) -> str:
    """Busca información de clientes en la base de datos del CRM EfiziAI.
    Args:
        query: término de búsqueda (nombre, email, empresa)
    """
    # Implementación real con psycopg2
    return f"Resultado CRM para: {query}"

@tool
def send_whatsapp_message(phone: str, message: str) -> str:
    """Envía un mensaje de WhatsApp vía WAHA API.
    Args:
        phone: número en formato internacional (+57...)
        message: contenido del mensaje
    """
    import httpx
    response = httpx.post(
        f"{os.environ['WHATSAPP_URL']}/api/sendText",
        json={"chatId": f"{phone}@c.us", "text": message, "session": "default"}
    )
    return "Enviado" if response.status_code == 200 else f"Error: {response.text}"

tools = [search_crm_database, send_whatsapp_message, search]

# Prompt del agente
prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente AI del CRM EfiziAI. Tienes acceso a herramientas
para consultar la base de datos de clientes y enviar mensajes de WhatsApp.
Piensa paso a paso antes de actuar. Si no estás seguro, pregunta.
Fecha actual: {date}"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Crear agente
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True
)

# Usar el agente
result = executor.invoke({
    "input": "Encuentra al cliente Juan García y envíale un mensaje de seguimiento",
    "date": "2026-06-20"
})
print(result["output"])
```

---

## LCEL — LangChain Expression Language

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Chain básica: prompt | llm | parser
basic_chain = prompt | llm | StrOutputParser()

# Chain con contexto RAG
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Chain con JSON estructurado
from pydantic import BaseModel

class LeadAnalysis(BaseModel):
    score: int
    tier: str
    action: str

json_chain = (
    prompt
    | llm
    | JsonOutputParser(pydantic_object=LeadAnalysis)
)

# Parallel chains (ejecutar múltiples chains en paralelo)
from langchain_core.runnables import RunnableParallel

parallel_chain = RunnableParallel({
    "summary": summary_chain,
    "sentiment": sentiment_chain,
    "keywords": keyword_chain
})

result = parallel_chain.invoke({"text": document})
# result = {"summary": "...", "sentiment": "positive", "keywords": [...]}
```

---

## LangGraph — Agentes con estado

### Grafo simple (agente ReAct)
```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

# LLM con herramientas
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState) -> AgentState:
    """Nodo principal — el LLM decide si usar herramienta o responder."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Construir grafo
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_conditional_edges(
    "agent",
    tools_condition,       # función que verifica si el AI pidió una herramienta
    {"tools": "tools", END: END}
)
graph.add_edge("tools", "agent")  # después de ejecutar tool, volver al agente

runnable = graph.compile()

# Invocar
result = runnable.invoke({
    "messages": [HumanMessage(content="Analiza los leads de esta semana y manda un resumen")]
})
```

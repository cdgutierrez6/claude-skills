# Memoria de conversación

Cuatro estrategias según la longitud de la conversación y qué hay que recordar.

## Contenido

- [1. Buffer Memory (conversaciones cortas)](#1-buffer-memory-conversaciones-cortas)
- [2. Summary Memory (conversaciones largas)](#2-summary-memory-conversaciones-largas)
- [3. Memoria persistente con PostgreSQL](#3-memoria-persistente-con-postgresql)
- [4. Entity Memory (recordar entidades mencionadas)](#4-entity-memory-recordar-entidades-mencionadas)

---

### 1. Buffer Memory (conversaciones cortas)
```python
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain

memory = ConversationBufferWindowMemory(k=10)  # últimas 10 interacciones

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

conversation.predict(input="Hola, soy Cristian")
conversation.predict(input="¿Recuerdas mi nombre?")  # Sí, recuerda
```

### 2. Summary Memory (conversaciones largas)
```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,  # Cuando supera este límite, resume automáticamente
    return_messages=True
)
```

### 3. Memoria persistente con PostgreSQL
```python
from langchain_postgres import PostgresChatMessageHistory
import psycopg

# Guardar historial en PostgreSQL
conn_string = os.environ["DATABASE_URL"]  # nunca la cadena literal en el codigo

history = PostgresChatMessageHistory(
    table_name="chat_history",
    session_id="session_cristian_001",
    connection=conn_string
)

history.add_user_message("¿Cuántos leads tenemos este mes?")
history.add_ai_message("Tienes 47 leads capturados en junio 2026.")

# Recuperar historial
messages = history.messages
```

### 4. Entity Memory (recordar entidades mencionadas)
```python
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE

entity_memory = ConversationEntityMemory(
    llm=llm,
    return_messages=True
)
# Recuerda automáticamente: personas, empresas, lugares mencionados en la conversación
```

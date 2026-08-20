# Integración de MCP servers

Ábrelo cuando conectes el server a un cliente: registro en Claude Code (`settings.json`) y consumo desde n8n vía HTTP.

## Contenido

- [Configurar MCP en Claude Code](#configurar-mcp-en-claude-code)
- [Integración con n8n vía MCP](#integración-con-n8n-vía-mcp)

---

## Configurar MCP en Claude Code

### `C:\Users\ASUS\.claude\settings.json`
```json
{
  "mcpServers": {
    "efiziai-crm": {
      "command": "node",
      "args": ["C:\\Users\\ASUS\\Documents\\claude projects\\efiziai-mcp-server\\dist\\index.js"],
      "env": {
        "DATABASE_URL": "postgresql://agency_user:password@localhost:5432/b2b_agency"
      }
    },
    "efiziai-crm-python": {
      "command": "python",
      "args": ["C:\\Users\\ASUS\\Documents\\claude projects\\efiziai-mcp-python\\server.py"],
      "env": {
        "DATABASE_URL": "postgresql://agency_user:password@localhost:5432/b2b_agency"
      }
    },
    "rag-assistant": {
      "command": "python",
      "args": ["C:\\Users\\ASUS\\Documents\\claude projects\\rag-ai-assistant\\mcp_server.py"],
      "env": {
        "PGVECTOR_URL": "postgresql://localhost:5432/rag_db"
      }
    }
  }
}
```

## Integración con n8n vía MCP

```
n8n puede consumir MCP servers via HTTP (no stdio) con nodo HTTP Request:

POST https://efiziai-mcp.internal/mcp
Content-Type: application/json
Mcp-Session-Id: n8n-workflow-123

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_leads",
    "arguments": { "query": "{{ $json.company_name }}" }
  },
  "id": 1
}
```

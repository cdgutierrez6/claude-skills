# Fundamentos de MCP

Ábrelo cuando necesites el modelo mental de MCP: qué es y cómo se conectan Host / Client / Server.

## ¿Qué es MCP?

Model Context Protocol es un protocolo abierto que permite a los LLMs conectarse a
sistemas externos de manera estandarizada. Piénsalo como "USB para AI":

```
┌─────────────────────────────────────────────────┐
│                   HOST                          │
│  (Claude Desktop / Claude Code / tu app)        │
│                                                 │
│  ┌──────────┐    ┌──────────────────────────┐   │
│  │  Claude  │◄──►│    MCP Client            │   │
│  │  (LLM)   │    │ (protocolo integrado)    │   │
│  └──────────┘    └────────────┬─────────────┘   │
└───────────────────────────────┼─────────────────┘
                                │ MCP Protocol (JSON-RPC 2.0)
              ┌─────────────────┼──────────────────┐
              │                 │                  │
        ┌─────▼────┐     ┌──────▼───┐    ┌─────────▼──┐
        │MCP Server│     │MCP Server│    │ MCP Server │
        │(Postgres)│     │(EfiziAI) │    │  (n8n)     │
        └──────────┘     └──────────┘    └────────────┘
```

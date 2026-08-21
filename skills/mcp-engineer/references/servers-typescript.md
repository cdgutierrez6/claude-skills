# MCP Server en TypeScript

Ábrelo cuando implementes un MCP server sobre Node.js: setup, servidor completo con tools/resources/prompts (ejemplo un CRM) y variante HTTP para producción remota.

## Contenido

- [Setup](#setup)
- [Server completo — CRM MCP](#server-completo--crm-mcp)
- [MCP Server HTTP (para producción remota)](#mcp-server-http-para-producción-remota)

---

## Setup
```bash
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node tsx
```

## Server completo — CRM MCP
```typescript
// crm-mcp-server/src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import pg from "pg";

const { Pool } = pg;

// Conexión a PostgreSQL
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // postgresql://<usuario>:<clave>@<host>:5432/<basededatos> — desde el entorno, nunca hardcodeada
});

// Crear el server MCP
const server = new McpServer({
  name: "crm-mcp",
  version: "1.0.0",
});

// ──────────────────────────────────────────────
// TOOLS — funciones que Claude puede ejecutar
// ──────────────────────────────────────────────

server.tool(
  "search_leads",
  "Busca leads en el CRM el CRM por nombre, email o empresa",
  {
    query: z.string().describe("Término de búsqueda"),
    limit: z.number().optional().default(10).describe("Máximo resultados"),
  },
  async ({ query, limit }) => {
    const result = await pool.query(
      `SELECT id, company_name, email, niche, plan, created_at
       FROM leads
       WHERE company_name ILIKE $1 OR email ILIKE $1
       ORDER BY created_at DESC
       LIMIT $2`,
      [`%${query}%`, limit]
    );

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result.rows, null, 2),
        },
      ],
    };
  }
);

server.tool(
  "get_lead_details",
  "Obtiene el detalle completo de un lead por su ID",
  {
    lead_id: z.string().uuid().describe("UUID del lead"),
  },
  async ({ lead_id }) => {
    const result = await pool.query(
      `SELECT l.*, u.username as assigned_to
       FROM leads l
       LEFT JOIN users u ON l.user_id = u.id
       WHERE l.id = $1`,
      [lead_id]
    );

    if (result.rows.length === 0) {
      return {
        content: [{ type: "text", text: "Lead no encontrado" }],
        isError: true,
      };
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result.rows[0], null, 2),
        },
      ],
    };
  }
);

server.tool(
  "create_lead_note",
  "Agrega una nota a un lead existente",
  {
    lead_id: z.string().uuid(),
    note: z.string().describe("Contenido de la nota"),
    author: z.string().default("AI Assistant"),
  },
  async ({ lead_id, note, author }) => {
    await pool.query(
      `INSERT INTO lead_notes (lead_id, content, author, created_at)
       VALUES ($1, $2, $3, NOW())`,
      [lead_id, note, author]
    );

    return {
      content: [{ type: "text", text: "Nota agregada correctamente" }],
    };
  }
);

// ──────────────────────────────────────────────
// RESOURCES — datos que Claude puede leer
// ──────────────────────────────────────────────

server.resource(
  "crm://dashboard/summary",
  "Resumen ejecutivo del CRM: total de leads, conversiones, planes",
  async () => {
    const result = await pool.query(`
      SELECT
        COUNT(*) as total_leads,
        COUNT(*) FILTER (WHERE plan = 'premium') as premium_leads,
        COUNT(*) FILTER (WHERE plan = 'free') as free_leads,
        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as leads_this_month
      FROM leads
    `);

    return {
      contents: [
        {
          uri: "crm://dashboard/summary",
          text: JSON.stringify(result.rows[0], null, 2),
          mimeType: "application/json",
        },
      ],
    };
  }
);

server.resource(
  "crm://leads/recent",
  "Los 20 leads más recientes del CRM",
  async () => {
    const result = await pool.query(
      `SELECT id, company_name, email, niche, plan, created_at
       FROM leads ORDER BY created_at DESC LIMIT 20`
    );

    return {
      contents: [
        {
          uri: "crm://leads/recent",
          text: JSON.stringify(result.rows, null, 2),
          mimeType: "application/json",
        },
      ],
    };
  }
);

// ──────────────────────────────────────────────
// PROMPTS — templates reutilizables
// ──────────────────────────────────────────────

server.prompt(
  "analyze_lead",
  "Prompt para análisis completo de un lead",
  {
    lead_id: z.string().describe("ID del lead a analizar"),
  },
  async ({ lead_id }) => {
    const result = await pool.query(
      "SELECT * FROM leads WHERE id = $1",
      [lead_id]
    );
    const lead = result.rows[0];

    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Analiza este lead del CRM el CRM y dame:
1. Score del 1-100 con justificación
2. Tier: hot / warm / cold
3. Próxima acción recomendada
4. Posibles objeciones del cliente

Datos del lead:
${JSON.stringify(lead, null, 2)}`,
          },
        },
      ],
    };
  }
);

// ──────────────────────────────────────────────
// Iniciar server
// ──────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("CRM MCP Server running on stdio");
}

main().catch(console.error);
```

## MCP Server HTTP (para producción remota)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";

const app = express();
app.use(express.json());

const server = new McpServer({ name: "crm-remote", version: "1.0.0" });

// Registrar tools igual que antes...

// Endpoint MCP (protocolo HTTP Streamable 2025-03-26)
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdHeader: "mcp-session-id" });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

app.listen(3001, () => {
  console.log("MCP Server HTTP en puerto 3001");
});
```

# Seguridad, testing y checklist de producción

Ábrelo cuando endurezcas un MCP server: patrones de seguridad con código, cómo probar (MCP Inspector + Jest) y el checklist completo antes de conectarlo a Claude en producción. Las reglas concisas viven en el body de `SKILL.md`; aquí está el código y el detalle de aplicación.

## Contenido

- [Patrones de seguridad en MCP](#patrones-de-seguridad-en-mcp)
- [Testing de MCP Servers](#testing-de-mcp-servers)
- [Checklist MCP server listo para producción](#checklist-mcp-server-listo-para-producción)

---

## Patrones de seguridad en MCP

```typescript
// 1. Validar inputs con Zod (siempre)
server.tool("delete_lead", "...", {
  lead_id: z.string().uuid(),               // fuerza UUID, rechaza inyecciones
  confirm: z.literal(true),                 // doble confirmación para acciones destructivas
}, handler);

// 2. Sanitizar queries SQL (nunca string concatenation)
// ❌ NUNCA:
`SELECT * FROM leads WHERE email = '${email}'`

// ✅ SIEMPRE:
pool.query("SELECT * FROM leads WHERE email = $1", [email])

// 3. Limitar permisos del usuario de DB
// El MCP server usa un usuario de solo lectura para tools de consulta
const readOnlyPool = new Pool({ connectionString: process.env.READ_ONLY_DB_URL });

// 4. Rate limiting por session
const rateLimiter = new Map<string, number>();
function checkRateLimit(sessionId: string, maxCalls = 100): boolean {
  const calls = rateLimiter.get(sessionId) ?? 0;
  if (calls >= maxCalls) return false;
  rateLimiter.set(sessionId, calls + 1);
  return true;
}

// 5. Logs de auditoría para todas las tool calls
async function auditLog(toolName: string, input: unknown, sessionId: string) {
  await pool.query(
    "INSERT INTO mcp_audit_log (tool_name, input, session_id, called_at) VALUES ($1, $2, $3, NOW())",
    [toolName, JSON.stringify(input), sessionId]
  );
}
```

## Testing de MCP Servers

```bash
# Inspector oficial de Anthropic (herramienta de debug)
npx @modelcontextprotocol/inspector node dist/index.js

# Abre UI en http://localhost:5173
# Permite: listar tools, ejecutarlas manualmente, ver responses
```

```typescript
// Unit test con Jest
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";

describe("EfiziAI MCP Server", () => {
  let server: McpServer;

  beforeEach(async () => {
    server = createEfiziaiServer(); // función que construye el server
    const [serverTransport, clientTransport] = InMemoryTransport.createLinkedPair();
    await server.connect(serverTransport);
  });

  it("search_leads retorna resultados", async () => {
    const result = await callTool("search_leads", { query: "test", limit: 5 });
    expect(result.content[0].text).toBeTruthy();
  });
});
```

## Checklist MCP server listo para producción

```
[ ] Zod schemas en todos los tool inputs
[ ] Queries SQL parametrizadas (sin concatenación)
[ ] Usuario de DB con permisos mínimos (no usar superuser)
[ ] Rate limiting por session ID
[ ] Logs de auditoría en tabla mcp_audit_log
[ ] Error messages genéricos al cliente (no exponer stack traces)
[ ] Tests con MCP Inspector antes de conectar a Claude
[ ] Timeout en todas las queries de DB
[ ] Variables de entorno para credenciales (sin hardcodear)
[ ] Documentación de cada tool (la usa Claude para decidir cuándo llamarla)
```

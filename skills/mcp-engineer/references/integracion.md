# Integración de MCP servers

Ábrelo cuando conectes el server a un cliente: registro en Claude Code (`settings.json`) y consumo
desde n8n vía HTTP.

## Contenido

- [Configurar MCP en Claude Code](#configurar-mcp-en-claude-code)
- [Credenciales: lo que NO va en settings.json](#credenciales-lo-que-no-va-en-settingsjson)
- [Integración con n8n vía MCP](#integración-con-n8n-vía-mcp)

---

## Configurar MCP en Claude Code

El registro vive en `settings.json`, dentro del objeto `mcpServers`. Cada entrada es un nombre
lógico (el que verás al invocar la herramienta) apuntando a cómo arrancar el proceso.

**Ubicación del fichero:**

| Alcance | Ruta |
|---|---|
| Global (todos los proyectos) | `~/.claude/settings.json` |
| Solo este repo | `<repo>/.claude/settings.json` |

**Server por stdio** — el cliente arranca el proceso y habla por entrada/salida estándar. Es el
caso normal para un server local:

```json
{
  "mcpServers": {
    "<nombre-logico>": {
      "command": "node",
      "args": ["<ruta-absoluta-al-build>/dist/index.js"]
    },
    "<otro-server-python>": {
      "command": "python",
      "args": ["<ruta-absoluta>/server.py"]
    }
  }
}
```

La ruta debe ser **absoluta**: el cliente no la resuelve contra el directorio del proyecto. En
Windows, dentro de JSON cada `\` se escribe `\\`, o usa `/` que también funciona.

**Server por HTTP** — el proceso ya corre en algún sitio y solo se declara la URL:

```json
{
  "mcpServers": {
    "<nombre-logico>": {
      "type": "http",
      "url": "https://<host>/mcp"
    }
  }
}
```

Tras editar `settings.json`, reinicia el cliente: la lista de servers se lee al arrancar.

---

## Credenciales: lo que NO va en settings.json

Es tentador meter la cadena de conexión en `env` junto al comando, porque funciona a la primera:

```json
"env": { "DATABASE_URL": "postgresql://usuario:clave@host:5432/basededatos" }
```

**No lo hagas.** `settings.json` no está pensado para guardar secretos: entra en los backups, sale
en capturas de pantalla, se pega en un issue al pedir ayuda, y en un `settings.json` de proyecto
acaba commiteado. Además fija la credencial de producción en el fichero de un desarrollador.

El server debe **leer la variable del entorno del sistema** (o de su propio `.env`, ignorado por
git) y `settings.json` no mencionarla:

```json
{
  "mcpServers": {
    "<nombre-logico>": {
      "command": "node",
      "args": ["<ruta-absoluta>/dist/index.js"]
    }
  }
}
```

```js
// dentro del server
const dbUrl = process.env.DATABASE_URL;
if (!dbUrl) throw new Error("Falta DATABASE_URL en el entorno");
```

Si el cliente **tiene** que inyectar una variable, que sea una referencia y no el valor:
`"env": { "DATABASE_URL": "${DATABASE_URL}" }`, resuelta desde el entorno de quien lanza el cliente.

---

## Integración con n8n vía MCP

n8n consume MCP servers **por HTTP, no por stdio** (no puede arrancar procesos locales), con un
nodo HTTP Request. El transporte es JSON-RPC 2.0:

```
POST https://<host-del-mcp>/mcp
Content-Type: application/json
Mcp-Session-Id: <identificador-de-la-sesion>

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "<nombre-de-la-herramienta>",
    "arguments": { "<param>": "{{ $json.<campo-del-nodo-anterior> }}" }
  },
  "id": 1
}
```

Tres cosas que importan:

- **`Mcp-Session-Id`** mantiene el estado entre llamadas. Si mandas cada request con un id nuevo,
  el server te trata como un cliente distinto cada vez y pierdes cualquier contexto de sesión.
- **`id`** del JSON-RPC correlaciona petición y respuesta; no lo confundas con el de sesión.
- Las **expresiones `{{ }}`** las resuelve n8n antes de enviar, así que el server recibe el valor
  ya sustituido. Si el campo puede venir vacío, valida en el server: llegará como cadena vacía, no
  como ausente.

Para exponer por HTTP un server que hoy es stdio, ponle delante un transporte HTTP y **no lo
publiques sin autenticación**: un MCP server suele tener acceso directo a la base de datos.

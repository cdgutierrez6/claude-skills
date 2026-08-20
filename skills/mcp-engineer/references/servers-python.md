# MCP Server en Python

Ábrelo cuando implementes el MCP server con Python (FastMCP): tools y resources sobre PostgreSQL con `asyncpg`.

```python
# efiziai_mcp/server.py
from mcp.server.fastmcp import FastMCP
import asyncpg
import os

mcp = FastMCP("efiziai-crm-python")

# Pool de conexiones
async def get_db():
    return await asyncpg.connect(os.environ["DATABASE_URL"])

@mcp.tool()
async def search_leads(query: str, limit: int = 10) -> str:
    """Busca leads en la base de datos EfiziAI por nombre o email."""
    conn = await get_db()
    try:
        rows = await conn.fetch(
            """SELECT id, company_name, email, niche, plan
               FROM leads
               WHERE company_name ILIKE $1 OR email ILIKE $1
               LIMIT $2""",
            f"%{query}%", limit
        )
        return str([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.resource("crm://stats")
async def get_crm_stats() -> str:
    """Estadísticas actuales del CRM."""
    conn = await get_db()
    try:
        row = await conn.fetchrow(
            "SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE plan='premium') as premium FROM leads"
        )
        return str(dict(row))
    finally:
        await conn.close()

if __name__ == "__main__":
    mcp.run()  # usa stdio por defecto
```

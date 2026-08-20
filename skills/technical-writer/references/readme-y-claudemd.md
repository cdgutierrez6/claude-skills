# README y CLAUDE.md — Templates de docs raíz del repo

## Contenido
- [README — Estructura Profesional](#readme--estructura-profesional)
- [CLAUDE.md de Proyecto — Template](#claudemd-de-proyecto--template)

---

## README — Estructura Profesional

```markdown
# ProjectName

> Tagline de una línea — qué hace y para quién.

[![CI](badge-url)](action-url) [![Coverage](badge)](url) [![License](badge)](url)

## Overview
2-3 párrafos: problema que resuelve, enfoque técnico, estado actual.

## Architecture
Diagrama de alto nivel (ASCII o enlace a imagen) + decisiones clave de stack.

## Prerequisites
- Node 22+ / .NET 8 / Python 3.12+
- Docker + Docker Compose
- [otros requisitos]

## Quick Start
```bash
git clone https://github.com/user/repo
cp .env.example .env
docker compose up -d
npm install && npm run dev
```

## Development
### Project Structure
```
src/
  api/        # Controllers y rutas
  services/   # Lógica de negocio
  models/     # Entidades y schemas
  middleware/ # Auth, logging, errors
```

### Available Commands
| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server with hot reload |
| `npm test` | Run unit + integration tests |
| `npm run build` | Production build |

## API Reference
Link a OpenAPI spec o sección de endpoints principales.

## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | — | Min 64 chars |
| `REDIS_URL` | ✅ | — | Redis connection |
| `LOG_LEVEL` | ❌ | `info` | debug/info/warn/error |

## Contributing
Ver [CONTRIBUTING.md](CONTRIBUTING.md).

## License
MIT © [Año] Cristian Gutierrez
```

---

## CLAUDE.md de Proyecto — Template

```markdown
# CLAUDE.md — {ProjectName}

## Stack
- **Runtime**: Node 22 / .NET 8 / Python 3.12
- **Frontend**: React 19 / Angular 21 / Next.js 15
- **DB**: PostgreSQL 16 / TimescaleDB
- **Infra**: Docker Compose (dev) / Azure Container Apps (prod)

## Commands
```bash
# Start dev environment
docker compose up -d && npm run dev

# Run tests
npm test

# Build
npm run build
```

## Architecture Notes
- {Decisión arquitectónica importante 1}
- {Decisión arquitectónica importante 2}

## Code Conventions
- {Convención específica del proyecto}
- {Patrón obligatorio}

## DO NOT
- {Cosa que no debe hacerse}
- {Anti-patrón del proyecto}
```

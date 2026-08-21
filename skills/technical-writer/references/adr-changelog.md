# ADRs y Changelog — Templates

## Contenido
- [Architecture Decision Records (ADRs) — Template Michael Nygard](#architecture-decision-records-adrs--template-michael-nygard)
- [Ejemplos de ADRs para los proyectos de Cristian](#ejemplos-de-adrs-para-los-proyectos-de-cristian)
- [Changelog — Keep a Changelog Format](#changelog--keep-a-changelog-format)

---

## Architecture Decision Records (ADRs) — Template Michael Nygard

```markdown
# ADR-{número}: {Título en forma de decisión tomada}

**Fecha:** {YYYY-MM-DD}
**Estado:** Propuesto | Aceptado | Rechazado | Obsoleto | Reemplazado por ADR-{N}
**Contexto:** {1-2 párrafos}

## Decisión

{La decisión tomada, en voz activa. "Usaremos X para Y."}

## Consecuencias

**Positivas:**
- {beneficio 1}
- {beneficio 2}

**Negativas:**
- {trade-off 1}
- {trade-off 2}

**Neutrales:**
- {hecho relevante sin valoración}

## Alternativas consideradas

### Opción A — {Nombre}
{Por qué no se eligió}

### Opción B — {Nombre}
{Por qué no se eligió}
```

## Ejemplos de ADRs para los proyectos de Cristian

```markdown
# ADR-001: TimescaleDB en lugar de InfluxDB para telemetría de flota

Fecha: 2026-01-15 | Estado: Aceptado

## Decisión
Usaremos TimescaleDB (extensión de PostgreSQL 16) para almacenar posiciones GPS
y métricas de vehículos en lugar de InfluxDB o ClickHouse.

## Consecuencias
Positivas: SQL estándar, joins con tablas relacionales, PostGIS para geofencing,
un solo motor de BD, continuous aggregates nativas.
Negativas: Rendimiento inferior a InfluxDB en escrituras > 1M/s, compresión
menos agresiva que Parquet.
```

---

## Changelog — Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com)
Versioning: [Semantic Versioning](https://semver.org)

## [Unreleased]

## [1.2.0] - 2026-06-16

### Added
- GPS geofencing violations now emit Kafka events to `geofencing.violations` topic (#234)
- Vehicle health score dashboard with real-time updates via SignalR (#238)

### Changed
- `GET /vehicles` now returns paginated results (breaking: adds `data` wrapper) (#241)

### Fixed
- Memory leak in KafkaRelayWorker when processing large batches (#245)
- Tenant isolation bypass when X-Tenant-Id header was missing (#247) ⚠ Security fix

### Deprecated
- `GET /vehicles/list` endpoint — use `GET /vehicles` instead. Removed in v2.0.

## [1.1.0] - 2026-05-20
...

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/<owner>/<repo>/compare/v1.1.0...v1.2.0
```

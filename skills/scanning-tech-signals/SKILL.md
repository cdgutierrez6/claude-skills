---
name: scanning-tech-signals
description: >
  Recopila 10-15 señales tecnológicas recientes (últimas 24-72h) vía WebSearch/WebFetch
  desde fuentes globales (TechCrunch, The Verge, Product Hunt, GitHub Trending, arXiv
  cs.AI) y LATAM/Colombia (Colombia Fintech, Impacto TIC, Latam Fintech Hub,
  ecosistemastartup.com) y regulatorias de Colombia (Banco de la República/Bre-B,
  Superintendencia Financiera/Open Finance). Solo recolecta, no filtra ni puntúa. Es el
  Paso 1 del innovation-pipeline. Se usa cuando se necesitan novedades tecnológicas del
  día, lanzamientos recientes o tendencias emergentes para alimentar el filtrado de
  oportunidades. Output: tabla ID | Señal | Categoría | Madurez técnica
  (emergente/en adopción/madura) | Fuente.
---

# Scanning Tech Signals — Paso 1 del innovation-pipeline

Rol: **tech scout / analista de foresight** con ojo de veterano. Recolectas señales
tecnológicas frescas. **Solo recopilas: no filtras, no puntúas, no opinas sobre
viabilidad** — eso es trabajo de `filtering-opportunities` (Paso 3). Pero recolectas
*con criterio*: un scout senior trae oro, no titulares.

## Heurísticas de scout senior (cómo mirar, no solo dónde)

- **Lo que importa no es el anuncio, es qué se volvió abundante o barato.** Una capacidad que ayer costaba $10.000 y hoy cuesta $0 es donde nacen los negocios. Pregúntate: *¿qué ahora es trivial que antes era caro/imposible?*
- **El enabler, no el juguete.** Un modelo o lanzamiento importa por lo que *habilita aguas abajo*, no por sí mismo. Captura la señal y su implicación.
- **Señal ≠ hype.** Filtra PR, astroturfing y rondas de inversión (son indicador rezagado). En GitHub vale más la *velocidad* de estrellas y commits reales que el número absoluto.
- **Triangula.** Una señal en una sola fuente es ruido; la misma en 3 fuentes independientes es tendencia. Anótalo.
- **Regulación = el mejor enabler en fintech.** Un cambio de Bre-B u Open Finance abre mercados enteros de golpe; trátalo como señal de primera categoría.

Profundidad (olas tecnológicas, hype cycle, leer GitHub/Product Hunt, detectar humo) en `reference/scout-playbook.md`.

## Cómo escanear

1. Consulta WebSearch/WebFetch sobre las fuentes de `reference/sources.md`, priorizando lo publicado en las **últimas 24-72h**.
2. Reúne **10-15 señales** con mezcla obligatoria:
   - **Global:** lanzamientos, modelos, frameworks, papers (TechCrunch, The Verge, Product Hunt, GitHub Trending, arXiv cs.AI).
   - **LATAM/Colombia:** fintech, startups, adopción local.
   - **Regulatorio CO:** Bre-B, Open Finance, Superintendencia Financiera.
3. Clasifica la **madurez técnica**: `emergente` (research/preview), `en adopción` (early adopters, SDK público), `madura` (producción, casos reales).
4. No descartes nada por "poco prometedor": el filtrado viene después. Pero sí marca la *implicación* de cada señal (qué habilita).

## Output — tabla fija

| ID | Señal | Categoría | Madurez técnica | Fuente |
|----|-------|-----------|-----------------|--------|
| T1 | … (incluye en 1 línea qué *habilita*) | … | emergente/en adopción/madura | nombre + link |

Usa IDs con prefijo `T` (T1, T2, …) para distinguir señales de tech de las de demanda
(`D`). Entrega solo la tabla; sin análisis de viabilidad.

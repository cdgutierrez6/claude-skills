---
name: web-design-pro-2026
description: >-
  Orquestador CANÓNICO y front door para TODO trabajo de página web (desktop + mobile, CADA sesión web). Se dispara al construir, crear, diseñar, mejorar, rediseñar u optimizar SEO/AEO de: página web, landing, landing page, sitio, site, web app, homepage, hero, marketing site, one-pager, publicidad / ad / anuncio / creative, portfolio, portafolio, SaaS, e-commerce, blog, dashboard público, o cualquier archivo .html .tsx .jsx .vue .svelte .astro. Verbos: build, create, design, hacer, construir, diseñar, mejorar, rediseñar, optimizar SEO, optimizar AEO, GEO. Enforza estética 2026 anti-flat (depth, texture, motion, type scale real) + SEO técnico + AEO/GEO + mobile-first + a11y WCAG 2.2. NO sustituye a ui-ux-pro-max / frontend-senior / ux-senior: los ORQUESTA. Aplica a cada página que se renderice en un navegador.
---

# web-design-pro-2026 — Orquestador de páginas web (estética 2026 + SEO + AEO + mobile)

Front door obligatorio de toda página web. **No duplica** a `ui-ux-pro-max`, `ux-senior` ni `frontend-senior`: los encadena y les añade la **dirección estética 2026 anti-flat**, el **SEO técnico**, el **AEO/GEO** y el **gate mobile/a11y**. Este archivo es un índice; el detalle vive en `references/`.

> **⭐ DEFAULT del HERO (aprobado por Cristian 2026-07-15):** para el momento héroe de cualquier
> página con ambición visual, invocar `creative-frontend-max` y seguir su receta canónica
> [`cinematic-hero-2026.md`](../creative-frontend-max/references/cinematic-hero-2026.md): UN objeto
> 3D art-directed sobre negro + **cámara que viaja con el scroll** + video/persona por luma-key,
> con RESTA. Es el estándar, no una opción. Ver memoria `feedback-frontend-cinematic-standard`.
> (No aplica a dashboards internos ni checkout — ahí, calma y usabilidad.)

---

## Cuándo se activa (SIEMPRE en web)

Cualquier trabajo cuyo output se renderiza en un navegador:

- Landing / marketing site / homepage / hero / one-pager / portfolio / blog.
- Web app, SaaS UI, e-commerce, dashboard **público**.
- Creatividades de publicidad (ad/anuncio) y sus landing pages de tráfico pagado.
- Archivos `.html .tsx .jsx .vue .svelte .astro` + CSS/Tailwind.
- Verbos: *construir, crear, diseñar, mejorar, rediseñar, optimizar SEO/AEO/GEO*.

Cubre **desktop y mobile** en la misma sesión (Google indexa mobile-first — la vista móvil es la que rankea).

## Cuándo NO

| NO se activa | Por qué / qué usar |
|---|---|
| Backend puro, APIs, DB, jobs | `backend-senior` / `arquitecto-senior` |
| App móvil **nativa** Android/iOS (Compose, SwiftUI, Flutter nativo) | `frontend-senior` + `ux-senior`. (Sí aplica a web responsive y a PWAs.) |
| Dashboards internos sin SEO/estética de marca | Aún útil el gate a11y/mobile, pero sin ceremonia de AEO/SEO. |

Regla proporcional (REGLA #1): página grande/marca visible = todo el pipeline; tweak de copy o un botón = solo el gate anti-flat + a11y.

---

## WORKFLOW obligatorio (orquesta, no reimplementa)

**Paso 1 — Sistema de diseño base con `ui-ux-pro-max` (SIEMPRE primero).** Saca paleta, tipografía y estilo candidato antes de escribir una línea de UI. Comando exacto:

```bash
python "C:/Users/ASUS/.claude/skills/ui-ux-pro-max/scripts/search.py" \
  "<tipo de sitio + industria + tono>" --design-system -p "<Nombre Proyecto>"
# Persistir como fuente de verdad del repo:
python "C:/Users/ASUS/.claude/skills/ui-ux-pro-max/scripts/search.py" \
  "<...>" --design-system --persist -p "<Nombre Proyecto>" --page "<home|pricing|...>"
```

Genera `design-system/<slug>/MASTER.md`. **Esa es la base tonal**; este skill NO reinventa la paleta.

**Paso 2 — Aplicar dirección 2026 anti-flat (este skill).** Sobre esa base, forzar: neutral calmo + **UN** acento saturado + textura visible; dark-mode-first con neutro tintado (zinc, no negro puro); depth por elevación en capas; una capa de textura/grain/aurora; una o dos micro-animaciones con propósito. Ver `references/design-2026.md` + recetas copy-paste en `references/anti-flat-recipes.md`.

**Paso 3 — Delegar el rol.** Estructura/flujo/jerarquía → `ux-senior`. Implementación en el framework → `frontend-senior`. SEO técnico en Next/Angular → conocimiento de `references/seo-technical-2026.md`. Este skill es el **director**: define el *qué* estético y de descubrimiento; ellos ejecutan el *cómo*.

**Herramientas de arranque de componentes/animación (usar, no reemplazar el criterio):**
- **21st.dev MCP** (`mcp__*21st*`, registrado a nivel usuario) — descubrir/adaptar componentes React+Tailwind animados (heroes parallax, cards 3D, reveals). Siempre re-tematizar con el `MASTER.md` de `ui-ux-pro-max` y pasar por los gates; nunca pegar crudo. Detalle en `references/scroll-3d-depth-2026.md §6`.
- **`motion`** (antes `framer-motion`, v12+, `import ... from "motion/react"`; el paquete viejo sirve igual) — animación e interacción en React/Next. Estándar para scroll-linked/parallax/tilt. Solo animar `transform`/`opacity`.
- **Profundidad 3D en scroll (estándar permanente):** cada página con marca visible aplica parallax por capas + perspectiva discreta (sensación "más en 3D") — barato, GPU, gateado por `prefers-reduced-motion`. Recetas en `references/scroll-3d-depth-2026.md`. NO en dashboards/tablas/checkout.

> Orden no negociable: **ui-ux-pro-max (base) → dirección 2026 (este skill) → ux/frontend-senior (ejecución) → gates**. Saltar el Paso 1 produce paletas inventadas incoherentes.

---

## Anti-flat forcing function (GATE — la página NO está lista sin esto)

Una página que no cumple los 5 se ve *AI-slop*. Es un gate binario, no una sugerencia.

| # | Exigencia | Falla si… |
|---|---|---|
| 1 | **Depth intencional** — elevación en capas (2-3 sombras suaves apiladas, tokens de elevación), no una sola `box-shadow` dura | Todo plano o una sombra genérica `0 1px 2px` |
| 2 | **≥1 capa de textura/atmósfera** — grain SVG `feTurbulence`, gradient-mesh/aurora, dithering, **o** tipografía expresiva como textura | Fondo blanco/gris liso + gradiente morado→azul suave |
| 3 | **Motion con propósito** — 1-2 movimientos <~300ms, envueltos en `prefers-reduced-motion` | Cero motion, o motion decorativo por todos lados sin gate a11y |
| 4 | **Type scale real** — escala modular (p.ej. 1.25×), display grande + jerarquía; `text-wrap: balance` en headings | Todo 16px, un solo peso, Inter/Poppins por defecto |
| 5 | **NO es el template genérico** — hero centrado + 3 cards iguales | Hero centrado sobre 3 columnas iguales, todo redondeado, todo centrado |

**Los "tells" del AI-slop a invertir uno por uno** (fuente: State of AI landing pages / críticas 2026):

| DON'T (fingerprint AI) | DO (2026) |
|---|---|
| Inter/Poppins default | Display con carácter (serif de alto contraste o variable font) + texto legible |
| Gradiente morado→azul | Neutral calmo + **un** acento saturado sacado del token palette |
| Todo `rounded-2xl` | Radios variados y deliberados; algún borde recto |
| Todo centrado | Layout asimétrico / bento con jerarquía |
| Grises default shadcn | Rampa neutra tintada (zinc/stone), dark-first |
| Iconos Lucide/Hero + fotos stock | Iconografía propia o consistente; nada de stock genérico |
| Sombra única plana | Elevación en capas + grain |

Contra-jugada legítima si "todos" convergen en bento pulido: **anti-grid / neo-brutalismo** deliberado (dif. 2026, medium-confidence).

---

## Referencias — cuándo abrir cada archivo

Cargar bajo demanda, no todo de una:

| Archivo | Ábrelo cuando… |
|---|---|
| `references/design-2026.md` | Definiendo look & feel: aurora, liquid-glass vs glassmorphism disciplinado, grain, dithering, bento, kinetic type, texture maximalism, qué está DATADO. |
| `references/anti-flat-recipes.md` | Necesitas snippets copy-paste: grain SVG, aurora background, tokens de elevación, `@property` para gradientes animados, scroll-driven, container queries, `:has()`. |
| `references/scroll-3d-depth-2026.md` | Efecto **3D en scroll**: parallax por capas (`animation-timeline: scroll()`), perspectiva/`translateZ`, Motion `useScroll`/`useTransform` en React/Next, tilt 3D por puntero, cuándo WebGL/Spline, y cómo usar el **21st MCP** con los gates. |
| `references/seo-technical-2026.md` | Metadata, JSON-LD, sitemap/robots, canonical/hreflang, Core Web Vitals, LCP/INP/CLS, SSR/SSG en Next App Router o Angular hydration, imágenes AVIF. |
| `references/aeo-geo-2026.md` | Que la página sea **citada por LLMs**: bloques answer-first 40-80 palabras, H2/H3 + listas numeradas + tablas, entidad explícita, medición GA4 de tráfico AI. |
| `references/mobile-performance-2026.md` | Thumb-zone, touch targets, `clamp()` fluido, `env(safe-area-inset)`, `<picture>` AVIF, srcset/sizes, budget JS, hydration/islands. |
| `references/accessibility-conversion-2026.md` | WCAG 2.2 (2.5.8 target size, 2.4.11 focus, 3.3.8 auth), EAA, focus-visible, forms, CRO (message-match, 1 CTA, social proof), dark-patterns legales. |

---

## PRE-DELIVERY GATE (consolidado — la página NO está "hecha" hasta pasar todo)

**Verificación renderizada obligatoria:** correr `/gstack-qa` (Chromium real) o el browser preview y **mirar el resultado**. "Compila" ≠ "funciona" ≠ "se ve bien". Probar en móvil throttled (Slow 4G + CPU throttle), no solo desktop.

**Estética (anti-flat forcing function)**
- [ ] Los 5 puntos del gate anti-flat cumplidos; NO es hero-centrado+3-cards.
- [ ] Paleta derivada del `MASTER.md` de ui-ux-pro-max (no inventada). Un acento, textura visible, dark-first.

**SEO técnico**
- [ ] Un H1 lógico único + jerarquía de headings ordenada; HTML semántico.
- [ ] `<title>`/description/canonical **self-referencing absoluto**/OG (1 imagen 1200×630) server-rendered (Next: `generateMetadata`; Angular: `provideClientHydration()` + meta por ruta).
- [ ] Contenido SSR/SSG/ISR (no CSR-only — invisible a crawlers AI que no ejecutan JS).
- [ ] `sitemap.xml` (solo URLs canónicas 200) + `robots.txt`; JSON-LD solo de tipos que aún dan rich results (Organization, Article/BlogPosting, Product, LocalBusiness, Breadcrumb). **NO** FAQPage/HowTo (ya no dan rich result — revalida estado en Search Central).
- [ ] Imágenes AVIF→WebP→JPEG, `width`/`height` siempre, lazy salvo la LCP.

**AEO/GEO**
- [ ] Cada sección abre con respuesta directa auto-contenida 40-80 palabras (≈44% de las citas LLM salen del primer 30% de la página).
- [ ] Estructura RAG-friendly: H2/H3, listas numeradas, tablas, estadísticas/citas (levers verificados; keyword-stuffing no sirve — GEO paper Aggarwal et al., KDD '24).
- [ ] Entidad nombrada explícitamente; freshness/fecha visible.

**Mobile-first & performance (p75 real users)**
- [ ] LCP < 2.5s · INP < 200ms · CLS < 0.1. LCP con `fetchpriority="high"` en **una** imagen, nunca lazy.
- [ ] Touch targets ≥24×24px (WCAG 2.5.8), 44-48px en móvil; inputs 16px (evita zoom iOS); body ≥16px, line-height ≥1.5, medida 45-75ch.
- [ ] `clamp()` fluido (rem min/max), container queries sobre breakpoints; `env(safe-area-inset-*)` + `viewport-fit=cover`.
- [ ] Budget JS ≤300-400KB gz; hydration mínima (RSC/islands). Long tasks partidas con `scheduler.yield()`.

**Accesibilidad (WCAG 2.2 AA) & conversión**
- [ ] Contraste 4.5:1 texto / 3:1 UI y large text; `:focus-visible` ≥2px, ≥3:1; nunca `outline:none` sin reemplazo.
- [ ] `prefers-reduced-motion` respetado en TODO motion (obligatorio, no polish).
- [ ] Si hay **3D/parallax en scroll**: solo `transform`/`opacity` (GPU), fallback estático legible, INP<200ms/CLS<0.1 se mantienen en móvil throttled, contenido nunca depende del scroll para verse. Detalle: `references/scroll-3d-depth-2026.md`.
- [ ] Focus no obstruido por sticky/cookie (2.4.11); alternativa no-drag (2.5.7); auth sin puzzle cognitivo + permite paste (3.3.8).
- [ ] Forms: labels visibles persistentes, error en texto (no solo color), `autocomplete`. HTML nativo > ARIA.
- [ ] CRO: **un** CTA primario claro (repetido en páginas largas), message-match H1↔anuncio, cookie banner con "Reject all" tan fácil como "Accept all" (exposición legal EU DSA/UCPD/EAA, no solo ética).

---

## Nota de honestidad

Este skill codifica conocimiento **investigado y verificado** (trends 2026, CSS moderno, SEO/AEO, mobile, a11y). No sustituye al **gusto**: la decisión final de si una página se ve premium exige **mirar el render**, iterar y ajustar. Si tras el gate el resultado es solo "competente", nómbralo así y propón 1-3 mejoras concretas — no cierres con "quedó perfecto".

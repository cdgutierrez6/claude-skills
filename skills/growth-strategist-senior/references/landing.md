# Landing — estructura, Definition of Done y gate de calidad

> Referencia canónica de **cómo se construye la landing** de la máquina. La consume la fase Arte+Landing
> (`web-design-pro-2026` orquestando ui-ux-pro-max/ux-senior/frontend-senior/creative-frontend-max) y la
> usa el juez como criterio de aceptación. Carta base de calidad: **taller-ejemplo.com o mejor**.
> Todo se rellena desde el [[contexto-brief]] con placeholders `{ASI}`. Contrato de reglas: [[reglas-duras]].

## Placeholders del Contexto
`{NEGOCIO}` · `{RUBRO}` · `{CIUDAD}` · `{ZONA}` · `{BENEFICIO}` · `{SERVICIOS}` · `{PRODUCTOS}` ·
`{DIFERENCIAL}` · `{PRUEBA}` · `{NUMERO_WA}` (10 dígitos SIN 57; las plantillas anteponen 57) · `{DIRECCION}` · `{HORARIO}` · `{REDES}` · `{VOZ}` (tú/usted, defecto usted).

## Principio rector
Un **único CTA primario en toda la página: WhatsApp**. Nada compite con él. La página no "informa":
empuja hacia una **consulta nueva por WhatsApp** (la métrica única). Cada bloque responde una objeción y
remata en el mismo botón, con un mensaje pre-cargado distinto por sección (para saber de dónde salió).

Jerarquía narrativa (el orden no es decorativo):
`Promesa → Capacidad → Confianza → Prueba → Baja fricción → Dónde → Objeciones → Cierre`.

---

## 1. Secciones (orden canónico)

| # | Sección | Propósito | CTA / nota |
|---|---|---|---|
| 0 | **Barra superior sticky** | Logo `{NEGOCIO}` + botón WhatsApp siempre visible (thumb-zone en móvil) | `Ref: WEB-NAV` |
| 1 | **Hero cinematográfico** | Promesa en 5s: `{BENEFICIO}` en `{CIUDAD}`. Headline + subhead + CTA WhatsApp. Debajo, bloque *answer-first* (40–80 palabras) que nombra la entidad (AEO) | `Ref: WEB-HERO` |
| 2 | **Qué hacemos / Capacidad** | `{SERVICIOS}`/`{PRODUCTOS}` en bento asimétrico (NO 3 cards iguales). Cada ítem con su CTA y mensaje pre-cargado propio | `Ref: WEB-SERV-<slug>` |
| 3 | **Por qué `{NEGOCIO}`** | Diferenciadores y confianza: `{DIFERENCIAL}`, `{PRUEBA}`, local físico, atención directa. Sin precios ni plazos | — |
| 4 | **Catálogo / Galería** | Productos con foto (lazy) o trabajos hechos. **Fotos de terceros solo con consentimiento**; nunca placas/rostros identificables sin permiso | `Ref: WEB-CAT-<slug>` |
| 5 | **Prueba social** | Reseñas/testimonios reales y con permiso + conteo. Entidad nombrada explícita (AEO) | — |
| 6 | **Cómo trabajamos** | Pasos numerados (formato que la IA cita). Sin tiempos de entrega | `Ref: WEB-PROC` |
| 7 | **Cobertura y ubicación** | `{DIRECCION}`, `{HORARIO}`, `{ZONA}`, mapa. Answer-first para "¿dónde queda?". Alimenta JSON-LD `LocalBusiness` | `Ref: WEB-UBIC` |
| 8 | **Preguntas frecuentes** | Q&A (pregunta en H3, respuesta 40–80 palabras auto-contenida). Resuelve objeciones B3 sin precio/plazo | `Ref: WEB-FAQ` |
| 9 | **Cierre** | Repetición del CTA primario a pantalla completa: una sola acción, WhatsApp | `Ref: WEB-CIERRE` |
| 10 | **Footer** | Contacto, `{HORARIO}`, redes (`sameAs`), aviso Habeas Data (Ley 1581 CO) | `Ref: WEB-FOOT` |
| ∞ | **FAB WhatsApp flotante** | Botón persistente (inferior, `safe-area-inset`), en todo el scroll | `Ref: WEB-FAB` |

### Convención de trazabilidad wa.me (fuente de verdad de toda la máquina)
Un solo número; **texto pre-cargado distinto por sección/canal**:
`https://wa.me/57{NUMERO_WA}?text=<texto-url-encoded>`, donde `{NUMERO_WA}` = **10 dígitos SIN 57**.
**Invariante (se prueba con el escáner, no se comenta):** todo link final matchea `^https://wa\.me/57\d{10}\?text=`.
El texto arranca con un código `Ref:` corto; el dueño lo lee en la primera línea del chat y sabe de dónde
vino → así se mide la métrica única sin dashboard.

**Registro de canales → código (única fuente; medición y kit lo referencian, no lo redefinen):**

| Canal | Ref | Canal | Ref |
|---|---|---|---|
| Web (por sección: HERO/SERV/CAT/FAQ/…) | `WEB-*` | Google Business | `GBP` |
| Facebook | `FB` | Estados de WhatsApp | `EST` |
| Instagram (bio) | `IG` | Volante / QR físico | `QR` |
| Instagram (historia) | `IG-HIST` | Tarjeta | `TARJ` |
| TikTok | `TT` | | |

Cada canal declarado en el intake (D3) recibe su propio link con su `Ref:`. Detalle de medición en [[medicion]].

### Hero cinematográfico adaptado a LATAM móvil (arte con criterio de negocio)
Se mantiene el estándar `hero-cinematic-oro-v1` (UN objeto 3D art-directed sobre fondo oscuro tintado +
cámara scroll-driven + video/persona por luma-key, con RESTA). **Pero el cliente está en Android de gama
media/baja y la métrica es la consulta por WhatsApp:** un hero WebGL pesado hunde LCP/INP y cuesta
consultas. Por eso el hero **degrada**: poster estático con el mismo *color grade* + parallax CSS como
base; el WebGL entra solo como *progressive enhancement* si el dispositivo puede y no hay
`Save-Data`/`prefers-reduced-motion`. (No aplica capa 3D a catálogo/tablas; ahí manda la usabilidad.)

---

## 2. Definition of Done (verificable)
Si funciona pero incumple un ítem de la sección **GATE**, **no está lista**.

**Estructura:** header con CTA WhatsApp (sticky desktop) · hero con promesa+subhead+CTA+señal de confianza ·
Qué ofrecemos (3–5 con micro-CTA propio) · Por qué nosotros · Prueba social (real/con permiso, o se omite) ·
FAQ (3 objeciones B3) · Cobertura+horario+mapa · CTA final + footer legal · **FAB WhatsApp persistente en móvil**.

**Jerarquía:** UNA promesa above-the-fold, UNA acción primaria (WhatsApp) · escaneable en 5s · el CTA gana
por contraste/tamaño/posición · copy en el idioma del cliente (B4), es-CO neutro-profesional.

**CTA WhatsApp:** todo CTA abre `wa.me/57<n>?text=<msg>` pre-cargado, **distinto por canal/sección** ·
`rel="noopener" target="_blank"`, accesible por teclado · área táctil ≥44×44 px · no depende solo de color.

**Mobile-first:** usable en **375px** sin scroll horizontal · 768px y ≥1024px · imágenes `max-width:100%` ·
CTA siempre alcanzable con el pulgar.

**Rendimiento (CWV móvil/4G):** LCP ≤2.5s · INP ≤200ms · CLS ≤0.1 · Lighthouse móvil Perf≥90 / A11y≥95 /
BP≥95 / SEO≥95 · imágenes WebP/AVIF dimensionadas, lazy below-the-fold · fuentes `font-display:swap`, sin CDN externo (CSP).

---

## 3. GATE de calidad (lo que el juez rechaza)
Verificación **renderizada obligatoria** (Chromium real / `/gstack-qa`) en **móvil throttled (Slow 4G + CPU 4–6×)**.
Binario: un fallo = no está listo.

### Reglas duras (rechazo automático — contrato canónico [[reglas-duras]], 8 reglas)
- [ ] **Cero precios** en texto, imagen o metadato.
- [ ] **Sin urgencia falsa** ("solo hoy", "últimos cupos" si no lo son).
- [ ] **Cero plazos / tiempos de entrega** ("en 24h", "en 2 días"). *El horario de atención SÍ: es un hecho.*
- [ ] Toda acción resuelve en `wa.me` pre-cargado, **distinto por canal** (`Ref:` WEB-*/FB/IG/EST).
- [ ] Español colombiano neutro-profesional.
- [ ] La máquina **prepara, no postea**; nada se publica solo.
- [ ] **Ningún tercero identificable** (rostro/placa/nombre) sin consentimiento.
- [ ] Prueba social solo real y con permiso; si no hay, se omite (no se fabrica).
- [ ] Sin datos inventados: número, dirección, NIT y legales vienen del intake o quedan `TODO` visible.

### Anti-flat 2026 (5 puntos — falla uno = "AI-slop")
- [ ] Depth intencional (elevación en capas, no una sombra dura) · [ ] ≥1 capa de textura/atmósfera (grain/aurora/tipografía) ·
- [ ] Motion con propósito (<~300ms, todo en `prefers-reduced-motion`) · [ ] Type scale real (~1.25×, display con carácter, `text-wrap:balance`) ·
- [ ] No es el template genérico (nada de hero centrado + 3 cards iguales; bento asimétrico) · [ ] Paleta del `MASTER.md` de ui-ux-pro-max (no inventada), dark-first.

### Accesibilidad WCAG 2.2 AA
- [ ] Contraste 4.5:1 texto / 3:1 UI · [ ] `:focus-visible` ≥2px y ≥3:1, nunca `outline:none` sin reemplazo ·
- [ ] `prefers-reduced-motion` en **todo** motion (incl. cámara del hero) · [ ] `alt` descriptivo · [ ] un solo `<h1>`, jerarquía coherente ·
- [ ] Foco no obstruido por sticky/FAB/cookie (2.4.11) · touch targets ≥24×24px (2.5.8).

### SEO técnico + AEO/GEO
- [ ] `<title>` <60c + description + canonical absoluto self-ref + OG (1200×630 <1MB) server-rendered ·
- [ ] Contenido **SSR/SSG/ISR** (los crawlers de IA no ejecutan JS) · `sitemap.xml` + `robots.txt` que no bloquea CSS/JS ·
- [ ] **JSON-LD `LocalBusiness`** (NAP, `openingHoursSpecification`, geo) coincidiendo con lo visible + **`Organization`** con `sameAs` a `{REDES}` ·
- [ ] Cada sección abre con **respuesta directa auto-contenida 40–80 palabras** (≈44% de las citas LLM salen del primer 30% de la página) · entidad nombrada explícita ·
- [ ] Validar en Rich Results Test antes de publicar (no invertir en FAQ/HowTo esperando rich result: retirados).

### Verificación final
- [ ] Todos los CTA abren el `wa.me` correcto con su `Ref:` (probar tap real en móvil) · [ ] Probado con JS desactivado (¿se ve el contenido?) · [ ] Pasa `llm-judge` sin violar regla dura.

> **Honestidad (REGLA #6):** el gate garantiza "competente y correcto", **no "premium"** — eso exige mirar
> el render e iterar. Si el resultado es solo competente, nómbralo y propón 1–3 mejoras. El mayor riesgo
> real es el hero: art dirigido que no degrade bien mata la métrica en el Android del cliente.

# Mobile-First UX + Web Performance — 2026

> Referencia operativa para construir web mobile-first que pase Core Web Vitals en campo y se sienta nativa en el pulgar. Cifras concretas, tablas DO/DON'T y snippets copy-paste. El presupuesto se mide contra **Android de gama media con throttling**, nunca contra tu MacBook.

---

## 0. Los números que mandan (Core Web Vitals, p75 de usuarios reales)

CWV se evalúa en el **percentil 75 de sesiones de campo** (field data / CrUX), no en lab. "Pasa" = las tres en verde.

| Métrica | Bueno (pasa) | Necesita mejora | Pobre | Qué mide |
|---|---|---|---|---|
| **LCP** | < 2.5 s | 2.5–4.0 s | > 4.0 s | Render del elemento más grande above-the-fold |
| **INP** | < 200 ms | 200–500 ms | > 500 ms | Latencia de interacción (reemplazó a FID en marzo 2024) |
| **CLS** | < 0.1 | 0.1–0.25 | > 0.25 | Estabilidad visual (layout shift acumulado) |

**INP es la CWV que más se falla**, sobre todo en móvil (el thread principal es el cuello de botella real). En CrUX (mayo 2026) el INP "bueno" agregado ronda ~86%, pero cae a ~53% en el top-1.000 de sitios y móvil va bastante peor que desktop. Trátalo como "la métrica prioritaria a defender en móvil", no como un número universal.

> Regla: el **reporte móvil** es siempre el más débil. Si móvil pasa, desktop pasa. Presupuesta contra móvil o no presupuestes.

---

## 1. Thumb-zone: anclar acciones abajo

El pulgar alcanza cómodamente el **tercio inferior** de la pantalla. Lo de arriba y las esquinas superiores son "zona de estiramiento": tocar ahí cuesta ~0.7–1.2 s extra por tap y sube la tasa de error. Los porcentajes exactos que circulan (96% vs 61% de precisión, "267% más rápido") tienen **procedencia dudosa** (se atribuyen a NN/g sin fuente primaria verificable) — usa la regla de diseño, ignora las cifras de precisión falsa.

| DO | DON'T |
|---|---|
| Nav primaria y CTA en el tercio inferior (bottom tab bar / bottom-anchored CTA) | Esconder la nav primaria detrás de un hamburger (mata discoverability — NN/g) |
| Botón de acción principal fijo abajo (`position: sticky; bottom: 0`) | Poner "Comprar / Enviar / Continuar" arriba a la derecha |
| Barra de tabs 3–5 destinos, siempre visibles | Menús críticos en la esquina superior izquierda |
| Respetar el home indicator con safe-area (ver §3) | CTA pegado al borde inferior sin `env(safe-area-inset-bottom)` |

La nav oculta (hamburger) es válida para destinos **secundarios**; nunca para los primarios (NN/g: la navegación escondida reduce el uso y la percepción de completitud del sitio).

```css
.cta-bar {
  position: sticky;
  bottom: 0;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom)); /* home indicator */
  background: color-mix(in oklab, Canvas 92%, transparent);
  backdrop-filter: blur(12px);
}
```

---

## 2. Touch targets & tipografía táctil

### Touch targets

| Estándar | Tamaño | Nivel | Nota |
|---|---|---|---|
| WCAG 2.2 SC 2.5.8 | **≥ 24×24 CSS px** o ≥ 24px de spacing | AA (piso legal) | Nuevo en WCAG 2.2 |
| WCAG 2.2 SC 2.5.5 | **44×44 CSS px** sin escape de spacing | AAA | El más estricto |
| Apple HIG | **44×44 pt** | — | iOS |
| Material 3 | **48×48 dp** | — | Android |

**Regla de envío: diseña a 44–48px.** El piso de 24px es el mínimo que te salva de una demanda de accesibilidad, no un objetivo de UX. Los enlaces de texto en línea están exentos del SC 2.5.8.

```css
button, a.btn, [role="button"] {
  min-height: 48px;
  min-width: 48px;
  /* si visualmente es más chico, expande el hit area con padding o ::before */
}
```

### Tipografía (verificado, no controversial)

| Propiedad | Valor mínimo | Por qué |
|---|---|---|
| `font-size` body | **≥ 16px** | Legibilidad + evita zoom en iOS |
| `line-height` body | **≥ 1.5** | WCAG 1.4.12 text spacing |
| Medida (measure) | **45–75ch** (~66ch ideal) | Fatiga de lectura |
| `font-size` en inputs | **exactamente 16px** | iOS Safari hace **auto-zoom** en focus si el input es < 16px |

```css
input, select, textarea { font-size: 16px; } /* mata el zoom-on-focus de iOS Safari */
```

---

## 3. Fluid responsive: `clamp()` + container queries

### Type scale fluido con `clamp()`

Ancla min/max en **rem** (respeta el zoom del usuario) con un término **vw pequeño**. **Nunca** texto en `vw` puro: rompe el zoom a 200% (falla real de WCAG 1.4.4).

**Regla de seguridad: `max` < ~2.5× `min`** para preservar el zoom.

```css
:root {
  /* min 16px @ 320px, max 20px @ ~1240px — anclado en rem */
  --step-0: clamp(1rem, 0.86rem + 0.71vw, 1.25rem);
  --step-1: clamp(1.25rem, 1.02rem + 1.16vw, 1.75rem);
  --step-2: clamp(1.56rem, 1.18rem + 1.90vw, 2.44rem);
  /* generador: utopia.fyi/type/calculator */
}
h1 { font-size: var(--step-2); }
p  { font-size: var(--step-0); line-height: 1.5; }
```

Escala modular con `pow()` (soportado en navegadores modernos, 2026):

```css
:root {
  --ratio: 1.25;
  --s1: calc(1rem * pow(var(--ratio), 1));
  --s2: calc(1rem * pow(var(--ratio), 2));
}
```

### Container queries > breakpoints de viewport

Los componentes deben responder a **su propio ancho**, no al del viewport. `container-type: inline-size` + `@container` es **production-ready** (Baseline desde 2023; Chrome 105+, Firefox 110+, Safari 16+; ~93–95% de soporte para *size queries*). Es el backbone de layouts modulares/bento.

> Ojo: el ~93–95% aplica a **size queries**. Las **style queries** (`@container style()`) siguen siendo solo Chrome/Edge — no generalices el soporte.

```css
.card-grid { container-type: inline-size; }

/* el card decide su layout por el ancho del CONTENEDOR, no del viewport */
@container (min-width: 30rem) {
  .card { display: grid; grid-template-columns: 8rem 1fr; }
}
```

Unidades **container-query** (`cqi`, `cqw`) para tipo/spacing relativos al contenedor:

```css
.card h3 { font-size: clamp(1rem, 5cqi, 1.5rem); } /* escala al card, no al viewport */
```

Fallback: base con media-query o `@supports (container-type: inline-size)`. No necesita polyfill.

| DO | DON'T |
|---|---|
| `@container` para componentes reutilizables (card, widget, sidebar item) | Cablear cada componente a breakpoints globales de viewport |
| `clamp()` anclado en rem para tipo/spacing | Texto en `vw` puro (rompe zoom, falla WCAG 1.4.4) |
| Generar la escala una vez con tokens | Hardcodear font-sizes por breakpoint |

---

## 4. Safe-area insets (notch / Dynamic Island / home indicator)

Sin `viewport-fit=cover`, los insets resuelven a **0**. Actívalo y paddea la UI fija/sticky.

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

```css
.app-header { padding-top: env(safe-area-inset-top); }     /* notch / Dynamic Island */
.bottom-nav { padding-bottom: env(safe-area-inset-bottom); } /* home indicator */
.side-rail  { padding-left: env(safe-area-inset-left); }
```

`env(safe-area-inset-*)` tiene soporte universal. **Considera** `safe-area-max-inset-*` (CSS Environment Variables Level 1) para máximos constantes que no cambian al rotar/scroll — es spec real pero soporte aún limitado, trátalo como progressive enhancement (MDN, developer.mozilla.org/en-US/docs/Web/CSS/env).

---

## 5. Presupuesto de performance (contra Android gama media throttled)

Todo se mide con throttling activado en Lighthouse / DevTools:

- **Red:** Slow 4G (~1.6 Mbps down, ~400 Kbps up, ~150 ms RTT).
- **CPU:** throttle. Lighthouse recomienda **4×** para un target de gama media (rango válido 2–10×; oficial: throttling.md). **6×** es una elección conservadora defendible, **no** un estándar — úsalo si tu audiencia es de gama baja, pero no lo presentes como ley.

En un Android gama media de ~2019, órdenes de magnitud plausibles (no constantes medidas): **~300–500 ms de parse de JS + ~150–300 ms de hidratación** por bundle pesado. Cada KB de JS cuesta más que cada KB de imagen porque hay que parsearlo y ejecutarlo en el thread principal.

### Budgets objetivo (rules of thumb, no estándares oficiales)

| Recurso | Budget | Nota |
|---|---|---|
| **JS (gzipped, páginas interactivas)** | **≤ 300–400 KB** | Convención de industria, no ley. Menos siempre mejor |
| **Long tasks** | ninguna bloquea > **50 ms** | Umbral documentado; rompe tareas largas |
| **LCP** | < 2.5 s en Slow 4G + CPU throttle | Contra móvil, no desktop |
| **INP** | < 200 ms | Hidratación es top contribuidor |
| **CLS** | < 0.1 | Reserva espacio para img/fonts/ads |
| **Peso total página** | presupuéstalo explícito por template | Trackéalo en CI (bundlesize / Lighthouse CI) |

---

## 6. Estrategia de imágenes (la palanca #1 de LCP)

Las imágenes son el mayor lever de LCP. Sirve el formato moderno con fallback ordenado en `<picture>`.

### Formatos (soporte early-2026: WebP ~96.4%, AVIF ~94.9%)

```html
<picture>
  <source type="image/avif" srcset="hero.avif">
  <source type="image/webp" srcset="hero.webp">
  <img src="hero.jpg" alt="…" width="1200" height="800">
</picture>
```

- **AVIF**: ~50% más liviano que JPEG. **WebP**: ~25–35%. El orden de `<source>` importa (el navegador toma el primero que soporta).

### `srcset` + `sizes` responsivos

3–5 variantes de ancho (heurística sensata, no ley) + `sizes` **preciso** para que el navegador elija la variante más chica que satisface. **Siempre** `width`/`height` intrínsecos o `aspect-ratio` para reservar espacio y matar CLS.

```html
<img
  src="p-800.avif"
  srcset="p-400.avif 400w, p-800.avif 800w, p-1200.avif 1200w, p-1600.avif 1600w"
  sizes="(max-width: 600px) 100vw, 50vw"
  width="1200" height="800"
  alt="…">
```

### LCP image: reglas duras (MDN, "Fixing image LCP")

| DO | DON'T |
|---|---|
| `fetchpriority="high"` en **exactamente una** imagen (la LCP) | `fetchpriority="high"` en varias (diluye la prioridad) |
| `loading="lazy"` solo **below-the-fold** | `loading="lazy"` en la imagen LCP (la retrasa) |
| Opcional: `rel="preload"` con `imagesrcset`/`imagesizes` que coincidan | Preload que no matchea el srcset (descarga doble) |

```html
<!-- imagen LCP -->
<img src="hero-800.avif" fetchpriority="high"
     srcset="hero-400.avif 400w, hero-800.avif 800w, hero-1200.avif 1200w"
     sizes="100vw" width="1200" height="675" alt="…">
```

MDN documenta una mejora real de **2.6 s → 1.9 s** de LCP aplicando estas reglas (developer.mozilla.org/en-US/docs/Web/Performance/Guides/Optimizing_LCP).

### LQIP + dimensiones explícitas (CLS ~0)

Reserva espacio con `width`/`height` o `aspect-ratio` y muestra un placeholder de baja calidad (base64 borroso o color dominante) que se reemplaza por el AVIF/WebP real. `next/image` con `placeholder="blur"` lo implementa out-of-the-box.

```css
.media { aspect-ratio: 16 / 9; background: #1a1a1a; } /* holdea el layout mientras carga */
```

---

## 7. Estrategia de fuentes

Self-hostear **gana** en 2026: los navegadores **particionan el HTTP cache por top-level site**, así que el viejo beneficio de "cache compartido" de Google Fonts ya no existe.

| DO | Por qué |
|---|---|
| **Self-host WOFF2** | Cache partitioning mató la ventaja de CDN de terceros |
| **Subsetear** (solo glyphs usados) | Roboto TTF ~168 KB → ~12 KB subset WOFF2 |
| `font-display: swap` | Texto visible ya (con fallback) mientras carga la webfont |
| `preload` 1–2 fuentes críticas | Elimina el retraso de descubrimiento |
| **Variable font** si usas ≥ 3 pesos | Break-even ~3 pesos; menos archivos = menos requests |
| **Fallback métrico-emparejado** (`size-adjust`, `ascent-override`) | Mata el CLS del swap |

```html
<link rel="preload" href="/fonts/inter-var-subset.woff2" as="font" type="font/woff2" crossorigin>
```

```css
@font-face {
  font-family: "Inter";
  src: url("/fonts/inter-var-subset.woff2") format("woff2");
  font-weight: 100 900;      /* variable */
  font-display: swap;
}
/* fallback métrico-emparejado: evita el reflow al swap */
@font-face {
  font-family: "Inter-fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
}
body { font-family: "Inter", "Inter-fallback", sans-serif; }
```

---

## 8. JS / hidratación budget (top contribuidor de INP)

La **hidratación** es una de las mayores fuentes de INP: el navegador re-ejecuta JS para "adjuntar" interactividad al HTML server-rendered, bloqueando el thread principal.

| DO | DON'T |
|---|---|
| Code-splitting + defer de lo no crítico | Enviar un bundle monolítico y hidratarlo todo |
| Romper long tasks (ninguna > 50 ms) con `scheduler.postTask` / yield con `setTimeout` | Un handler que bloquea el thread 200 ms |
| Trimear scripts de terceros (analytics, chat, ads) | Cargar 6 tags de terceros síncronos en `<head>` |
| Budget JS ≤ 300–400 KB gzip | "Ya lo optimizamos después" |

```js
// yield al thread principal entre chunks de trabajo pesado
async function processInChunks(items) {
  for (const batch of chunk(items, 50)) {
    doWork(batch);
    await (globalThis.scheduler?.yield?.() ?? new Promise(r => setTimeout(r))); // guarda el OBJETO scheduler, no solo el método (si no, ReferenceError donde no exista la API)
  }
}
```

### Recortar hidratación: RSC + islands

- **React Server Components**: 0 JS al cliente, 0 costo de hidratación para lo estático.
- **Islands** (`'use client'`, Astro islands): hidrata **solo** las partes interactivas.
- **Resumability** (Qwik): hidratación cuasi-cero — el estado se serializa, no se re-ejecuta.
- **Streaming SSR**: manda HTML en cuanto está, hidrata progresivamente.

Regla: server-render lo estático, hidrata solo lo que el usuario toca. El thread principal libre = INP bajo (patterns.dev progressive hydration; docs de Next App Router / Astro / Qwik).

---

## 9. LCP / INP tactics en móvil (checklist rápido)

**LCP:**
- Un solo `fetchpriority="high"` en la imagen LCP; nunca `loading="lazy"` en ella.
- Preconnect/preload al origen del recurso LCP crítico.
- AVIF + srcset con la variante correcta para el viewport.
- Elimina render-blocking CSS/JS del critical path; inline el CSS crítico.
- Fuentes con `swap` + preload para que el texto LCP no espere.

**INP:**
- Reduce JS y rompe long tasks (< 50 ms).
- RSC/islands para minimizar hidratación.
- Debounce/throttle handlers de input; mueve trabajo pesado a Web Workers.
- `content-visibility: auto` en secciones off-screen para diferir layout/paint (ver abajo).

**CLS:**
- `width`/`height` o `aspect-ratio` en toda imagen/embed/iframe.
- Fallback métrico-emparejado para fuentes.
- Reserva espacio para ads/embeds antes de que carguen.

---

## 10. CSS moderno production-safe (2026)

Triage de features. **SHIP FREELY** = úsalo sin miedo con fallback trivial. **ENHANCEMENT** = mejora progresiva, degrada limpio. **GATE/AVOID** = feature-detect obligatorio, no dependas de él.

### SHIP FREELY (Baseline Widely / robusto con fallback)

| Feature | Qué te da | Soporte | Caveat |
|---|---|---|---|
| **Container queries + `cqi`/`cqw`** | Componentes que responden a su propio ancho | Baseline (Chrome 105+/FF 110+/Safari 16+), ~93–95% | Solo *size* queries; style queries no |
| **`:has()`** | Estilo del padre según hijo (state-driven, sin JS) | Baseline Widely (FF 121 cerró, dic 2023) | Reglas aditivas; opcional `@supports selector(:has(*))` |
| **CSS Nesting** | Co-locar hover/media/container en el bloque del componente | Baseline Widely (Chrome 112+/FF 117+/Safari 16.5+) | Nested type selectors: empieza con `&` o `:is()` (builds viejos 112–119 / 16.5–17.1 los rechazaban) |
| **`color-mix()`** | Tints/shades/glass desde un token, sin preprocesador | Baseline Widely (Chrome 111+/Safari 16.2+/FF 113+) | Mezcla en `oklab` |
| **Subgrid** | Alinear grids anidados a los tracks del padre (bento/editorial) | **Baseline Widely 2026-03-15** | Fallback `@supports (grid-template-rows: subgrid)`; degrada a mal alineado |
| **`prefers-reduced-motion`** | Gate a11y **obligatorio** de toda animación | Baseline Widely (~2020) | Es la capa de fallback en sí |
| **`backdrop-filter`** | Glassmorphism (headers/modales frosted) | Baseline Newly ~2024-09 (Safari 18 sin prefijo) | Mantén `-webkit-`; fondo sólido-ish primero; blur es caro en GPU, no lo animes |

### ENHANCEMENT (Baseline Newly / degrada limpio)

| Feature | Qué te da | Estado | Fallback |
|---|---|---|---|
| **`@property`** | Animar gradients/ángulos/colores (props tipadas interpolan) | Baseline Newly 2024-07-09 (FF 128) | Renderiza el gradiente estático inicial |
| **Relative color** `oklch(from …)` | Derivar tints/alpha de un token en runtime | Baseline Newly (Chrome 125/FF 128/Safari 18, mid-2024) | Declaración plana primero o `@supports` |
| **View Transitions same-document** | Morphs shared-element/list-detail | **Baseline Newly 2025-10-14** (FF 144) | Feature-detect `document.startViewTransition`; no-op = nav instantáneo |
| **`text-wrap: balance`** | Headings multi-línea balanceados | Baseline Newly (Chrome 114/FF 121/Safari 17.5) | Degrada a wrap normal, sin gate |
| **`content-visibility: auto`** | Difiere layout/paint off-screen (perf en páginas largas) | **Baseline Newly 2025-09-15** (Safari 26) | Sin soporte = renderiza todo. Usa `contain-intrinsic-size` para no saltar el scrollbar |
| **CSS Anchor Positioning (core)** | Tooltips/popovers/menus tethered sin JS (reemplaza Floating UI) | **Baseline 2026** (FF 147 stable, 2026-01-13; ~91%) | `@position-try`/auto-flip necesita Chrome 125+/FF 147+/Safari 26+ → trátalo como enhancement; polyfill `@oddbird/css-anchor-positioning` |

### GATE / AVOID (no Baseline — feature-detect o polyfill obligatorio)

| Feature | Por qué NO es safe | Regla |
|---|---|---|
| **Scroll-driven animations** (`animation-timeline: scroll()/view()`) | Firefox tras flag en stable hasta FF 152 (jun 2026); solo Chrome/Edge 115+/Safari 26+ | `@supports (animation-timeline: view())` o polyfill de Bramus; **nunca** hagas visibilidad de contenido dependiente; anida en `prefers-reduced-motion` |
| **Cross-document View Transitions (MPA)** | No hay Firefox | Enhancement; no-op = nav instantáneo |
| **`text-wrap: pretty`** | No hay Firefox stable en early-2026; Chrome 117+ limitado (~4 líneas), Safari 17.5+ | Degrada a wrap normal, sin gate |
| **`@position-try` en Safari viejo** | Auto-flip incompleto | Trátalo como enhancement sobre el anchor core |

### Método universal (aplica a TODAS)

1. **Feature-detect**: `@supports` en CSS, `CSS.supports()` / `'startViewTransition' in document` en JS.
2. **Aditivo**: la feature mejora una base que ya funciona sin ella.
3. **Wrap motion** en `@media (prefers-reduced-motion: no-preference)` — siempre.

```css
/* patrón universal: base funcional + enhancement gated + gate de movimiento */
.reveal { opacity: 1; } /* base: contenido siempre visible */

@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .reveal {
      animation: fade-in linear both;
      animation-timeline: view();
      animation-range: entry 0% cover 30%;
    }
  }
}
```

---

## 11. PWA en 2026 (realista)

Una web app instalable es un default sensato, pero **no dependas de prompts de instalación en iOS**.

| Plataforma | Comportamiento |
|---|---|
| **Android** | `beforeinstallprompt` disponible → puedes ofrecer install custom |
| **iOS** | **No hay prompt automático** — el usuario instala manual (Share → Add to Home Screen) |
| **Web Push iOS** | Requiere que la app esté **instalada** + iOS **16.4+** |
| **Declarative Web Push** | Safari 18.4 (iOS/iPadOS 18.4) — notificaciones sin service worker para web apps en home screen (WebKit blog, webkit.org/blog) |

Regla: diseña la experiencia web para que funcione **sin** instalar; la instalación es bonus, no gate.

---

## 12. Checklist mobile pre-ship (objetivos numéricos)

Medido en **Slow 4G + CPU throttle 4× (o 6× si audiencia gama baja), p75 de campo**:

**Core Web Vitals**
- [ ] LCP **< 2.5 s**
- [ ] INP **< 200 ms**
- [ ] CLS **< 0.1**
- [ ] Ninguna long task **> 50 ms**

**Presupuesto**
- [ ] JS interactivo **≤ 300–400 KB gzip**
- [ ] Peso de página presupuestado por template y verificado en CI

**Táctil / UX**
- [ ] Touch targets **≥ 44–48px** (piso legal 24×24 CSS px, WCAG 2.5.8)
- [ ] Body **≥ 16px** / line-height **≥ 1.5** / measure **45–75ch**
- [ ] Inputs a **16px exactos** (sin zoom iOS)
- [ ] Nav primaria y CTA en el **tercio inferior**; nada crítico escondido en hamburger
- [ ] `viewport-fit=cover` + `env(safe-area-inset-*)` en UI fija/sticky

**Imágenes**
- [ ] AVIF → WebP → JPEG vía `<picture>`
- [ ] `width`/`height` o `aspect-ratio` en **toda** imagen (CLS 0)
- [ ] **Exactamente una** imagen con `fetchpriority="high"`; nunca `lazy` en la LCP
- [ ] `srcset` (3–5 variantes) + `sizes` preciso; LQIP en las grandes

**Fuentes**
- [ ] Self-host WOFF2 subseteado, `font-display: swap`
- [ ] Preload 1–2 fuentes críticas + fallback métrico-emparejado (CLS 0)
- [ ] Variable font si ≥ 3 pesos

**Responsive / CSS**
- [ ] Type scale con `clamp()` anclado en **rem** (max < ~2.5× min; zoom 200% OK)
- [ ] Container queries para componentes; breakpoints de viewport solo para layout global
- [ ] Toda animación dentro de `prefers-reduced-motion: no-preference`
- [ ] Features no-Baseline (scroll-driven, cross-doc VT, `text-wrap: pretty`) feature-detected

**A11y de zoom**
- [ ] Sin texto en `vw` puro (no rompe zoom, WCAG 1.4.4)
- [ ] Reflow OK a 200% de zoom

---

### Fuentes clave
- Core Web Vitals thresholds y buckets — web.dev / corewebvitals.io / webvitals.tools (2026)
- Lighthouse throttling (4×, rango 2–10×) — throttling.md, GoogleChrome/lighthouse
- WCAG 2.2 SC 2.5.8 / 2.5.5 — w3.org/WAI/WCAG22/Understanding
- Fixing image LCP (2.6 s → 1.9 s, fetchpriority) — MDN, developer.mozilla.org/en-US/docs/Web/Performance
- Fluid type Baseline + `pow()` — web.dev
- Container queries / size support — MDN + caniuse
- `env()` / `safe-area-inset-*` / `safe-area-max-inset-*` — MDN
- Cache partitioning + font strategy — web-perf guidance vigente
- Baseline dates (subgrid 2026-03-15, content-visibility 2025-09-15, same-doc View Transitions 2025-10-14, anchor positioning FF 147 2026-01-13, `@property` 2024-07-09) — web.dev Baseline digests / web-features-explorer
- Declarative Web Push Safari 18.4 — WebKit blog
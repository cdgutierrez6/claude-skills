# Anti-Flat Recipes — Cookbook de profundidad y movimiento

Recetas copy-pasteables (Tailwind + vanilla CSS) para sacar una página del look plano/barato/AI-slop. Cada receta: **propósito en 1 línea → código mínimo → "no hagas esto"**. Todo respeta `prefers-reduced-motion` y presupuesto de rendimiento.

**Reglas de oro que atraviesan todo el archivo:**

- **Método universal de compatibilidad 2026:** feature-detect (`@supports`) + reglas *aditivas* (nunca de las que dependa la visibilidad del contenido) + todo el movimiento envuelto en `@media (prefers-reduced-motion: no-preference)`.
- **Motion baseline:** micro-animación con propósito, `≤300ms`, `ease-out`. Uno o dos movimientos bien puestos, no diez decorativos.
- **Animar solo `transform` y `opacity`** (compositable). Nunca animar `box-shadow`, `width`, `height`, `top/left`, `filter` en loops.
- **Gate de a11y obligatorio:** ninguna animación puede ser la única forma de revelar contenido.

Triage de features usado en este cookbook (verificado contra Baseline mid-2026):

| Bucket | Features | Regla |
|---|---|---|
| **Ship libre** | container queries + `cqi`, `:has()`, CSS Nesting (con `&`), `color-mix()`, subgrid, `backdrop-filter` (con fondo sólido), `prefers-reduced-motion` | Úsalas directo |
| **Enhancement** | `@property`, relative color, View Transitions same-doc, `text-wrap: balance`, `content-visibility`, anchor positioning core | Degradan solas, sin gate estricto |
| **Gate / evita** | scroll-driven animations (Firefox tras flag), View Transitions cross-doc (sin Firefox), `text-wrap: pretty` (sin Firefox estable), `@position-try` en Safari viejo | `@supports` + fallback estático obligatorio |

---

## 1. Elevación por sombras suaves en capas

**Propósito:** profundidad realista apilando 2-3 sombras de baja opacidad (luz ambiente + luz clave) + un highlight interno de 1px. Es la salida #1 del look plano (Born Digital / TheeDigital, trend roundups 2026).

```css
:root {
  /* Tokens de elevación: cada nivel = ambient + key + inset highlight */
  --elev-1:
    0 1px 2px -1px rgb(0 0 0 / 0.08),
    0 2px 4px -2px rgb(0 0 0 / 0.06),
    inset 0 1px 0 0 rgb(255 255 255 / 0.06);
  --elev-2:
    0 2px 4px -2px rgb(0 0 0 / 0.10),
    0 6px 12px -4px rgb(0 0 0 / 0.08),
    inset 0 1px 0 0 rgb(255 255 255 / 0.08);
  --elev-3:
    0 4px 8px -3px rgb(0 0 0 / 0.12),
    0 12px 28px -6px rgb(0 0 0 / 0.10),
    inset 0 1px 0 0 rgb(255 255 255 / 0.10);
}
.card { box-shadow: var(--elev-2); border-radius: 16px; }
```

Tailwind (arbitrary + config):

```html
<div class="rounded-2xl shadow-[0_2px_4px_-2px_rgb(0_0_0/0.10),0_6px_12px_-4px_rgb(0_0_0/0.08),inset_0_1px_0_0_rgb(255_255_255/0.08)]">…</div>
```

> **No hagas esto:** una sola `box-shadow: 0 4px 6px rgba(0,0,0,.3)` dura y opaca (el tell #1 del flat barato). Tampoco **animes `box-shadow` en hover** (repinta): cambia el token de elevación con una capa/pseudo-elemento con `opacity` (ver receta 9), o transiciona `filter: drop-shadow` solo si es puntual.

---

## 2. Overlay de grano / ruido (SVG feTurbulence)

**Propósito:** la capa "premium" más barata; mata el gradiente estéril y liso (CSS-Tricks "Grainy Gradients", Jimmy Chion). GPU-cheap vs PNG.

```css
.grain::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  opacity: 0.06;               /* 0.03–0.08 es el rango util */
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
.grain { position: relative; }
```

- `baseFrequency` alto (`0.7–0.9`) = grano fino tipo film; bajo = manchas.
- Va **encima del gradiente**, `pointer-events: none`, y es estático (no animar).

> **No hagas esto:** PNG de ruido de 500KB tileado (mata el LCP). Ni `opacity` alta (>0.1) que ensucia el texto. Ni ponerlo con `background` en el mismo elemento del contenido: usa `::after` con `pointer-events: none` para no romper clicks.

---

## 3. Fondo aurora / mesh gradient

**Propósito:** hero atmosférico actual (washes fríos de baja saturación, blur, movimiento lento 20–40s + grano encima). Distinto del gradiente arcoíris candy-stripe de 2021.

```css
.aurora {
  position: relative;
  overflow: hidden;
  background: #0b0b12;         /* base zinc, no #000 */
}
.aurora::before {
  content: "";
  position: absolute;
  inset: -20%;
  z-index: 0;
  filter: blur(80px) saturate(1.1);
  background:
    radial-gradient(40% 40% at 20% 30%, oklch(0.72 0.13 265 / 0.55), transparent 70%),
    radial-gradient(35% 35% at 80% 20%, oklch(0.70 0.12 200 / 0.50), transparent 70%),
    radial-gradient(45% 45% at 60% 80%, oklch(0.68 0.14 320 / 0.45), transparent 70%);
}
@media (prefers-reduced-motion: no-preference) {
  .aurora::before { animation: aurora-drift 32s ease-in-out infinite alternate; }
}
@keyframes aurora-drift {
  from { transform: translate3d(-3%, -2%, 0) scale(1.05); }
  to   { transform: translate3d(3%, 4%, 0) scale(1.15); }
}
```

Superpón la receta 2 (grano) encima para el acabado. Los colores del mesh **deben salir de 2 tokens que ya estén en tu paleta** (regla de paleta disciplinada: base neutra calma + UN acento saturado + textura).

> **No hagas esto:** gradiente lineal de 5 colores saturados (arcoíris 2021). No animes `background-position` de un gradiente (repinta cada frame) — anima `transform` de una capa blurreada. No pongas texto directo sobre el blur sin una capa de contraste (ver receta 4).

---

## 4. Glassmorphism v2 bien hecho (light + dark)

**Propósito:** panel esmerilado disciplinado. En web **no existe "liquid glass"**: Apple mostró Liquid Glass (WWDC 2025) pero la refracción/specular/tint adaptativo es nativo. En CSS envías glass honesto: `rgba` fill + `backdrop-filter` blur + borde (Setproduct comparison).

```css
.glass {
  --glass-bg: 255 255 255;            /* light */
  background: rgb(var(--glass-bg) / 0.65);   /* fill SÓLIDO detrás de texto para WCAG AA */
  border: 1px solid rgb(255 255 255 / 0.35);
  border-radius: 16px;
  box-shadow: var(--elev-2);
  -webkit-backdrop-filter: blur(12px) saturate(1.4);
  backdrop-filter: blur(12px) saturate(1.4);
}
@media (prefers-color-scheme: dark) {
  .glass {
    --glass-bg: 18 18 24;
    background: rgb(var(--glass-bg) / 0.55);
    border-color: rgb(255 255 255 / 0.10);
  }
}
/* Fallback: sin backdrop-filter → sube el fill a opaco para no perder legibilidad */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass { background: rgb(var(--glass-bg) / 0.92); }
}
```

- `backdrop-filter` es Baseline Newly (~sept 2024, Safari 18 sin prefijo). **Mantén `-webkit-` para Safari viejo.**
- Blur es caro en GPU: **capa pequeña, no animar el blur, no anidar varios glass**.

> **No hagas esto:** texto sobre `rgba(...,0.1)` casi transparente (falla contraste AA sobre fondos variables). No pongas `backdrop-filter` en un elemento full-screen que scrollea (jank). No finjas "liquid glass" con reflejos SVG animados: es peso muerto que no convence.

---

## 5. Scroll-driven reveal (`animation-timeline`)

**Propósito:** reveal/parallax off-main-thread, **cero JS**, cero scroll listeners (`animation-timeline: view()`). PERO **no es Baseline** (Firefox tras flag `layout.css.scroll-driven-animations.enabled` hasta ≥152, jun 2026). Enhancement-only → gate + fallback estático obligatorio.

```css
.reveal { opacity: 1; }   /* ESTADO BASE = visible. Nunca depender del scroll para ver contenido */

@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .reveal {
      opacity: 0;
      transform: translateY(24px);
      animation: reveal-in linear both;
      animation-timeline: view();
      animation-range: entry 0% cover 35%;
    }
  }
}
@keyframes reveal-in {
  to { opacity: 1; transform: none; }
}
```

> **No hagas esto:** poner `opacity: 0` como estado por defecto fuera del `@supports` → en Firefox estable (sin la feature) y con reduced-motion, el contenido **queda invisible para siempre**. La visibilidad nunca puede depender de la animación. Tampoco recrees parallax con `scroll` + JS `requestAnimationFrame` en 2026 (era: heavy JS parallax, ya está OUT).

---

## 6. Navegación con View Transitions

**Propósito:** morphs nativos entre estados/páginas sin librería. **Same-document es production-safe** (Baseline Newly, 14-oct-2025, Firefox 144). **Cross-document (MPA) NO** (sin Firefox) → enhancement.

Same-doc (SPA / cambios de estado) — feature-detect:

```js
function navigate(update) {
  if (!document.startViewTransition) return update();   // fallback: cambio instantáneo
  document.startViewTransition(update);
}
```

```css
/* Nombra el elemento compartido para que "vuele" entre estados */
.hero-img { view-transition-name: hero; }

/* Gate de a11y: neutraliza la animación bajo reduced-motion */
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation-duration: 0s !important; }
}
```

Cross-doc (MPA, solo Chrome 126+/Safari 18.2+) — **puro CSS, no-op en Firefox**:

```css
@view-transition { navigation: auto; }
```

> **No hagas esto:** asumir cross-doc `@view-transition` como base cross-browser (en Firefox simplemente navega instantáneo — bien si lo tratas como enhancement, mal si tu UX depende de la transición). No dupliques el mismo `view-transition-name` en dos elementos visibles a la vez (rompe la transición). No olvides el reset bajo `prefers-reduced-motion`.

---

## 7. Tipografía cinética / variable

**Propósito:** peso/ancho animados por interacción (`font-variation-settings`) como palanca premium. Confinado a hero/transiciones de sección y gateado por reduced-motion (Studio Meyer reality-check: la cinética pelea con SR/crawlers y suma CLS).

```css
.kinetic {
  font-family: "InterVariable", system-ui, sans-serif;   /* fuente ejemplo */
  font-variation-settings: "wght" 400;
  transition: font-variation-settings 200ms ease-out;
}
@media (prefers-reduced-motion: no-preference) {
  .kinetic:hover,
  .kinetic:focus-visible { font-variation-settings: "wght" 720; }
}
```

Display tipografía-como-arte (sin movimiento, siempre seguro) — oversized + tracking negativo + balance:

```css
.display {
  font-size: clamp(2.5rem, 6vw + 1rem, 6rem);
  line-height: 0.95;
  letter-spacing: -0.03em;
  text-wrap: balance;         /* Baseline Newly; degrada a wrap normal, sin gate */
}
```

> **No hagas esto:** animar `font-weight` en cuerpos de texto o en loop (reflow + CLS + ilegible). No uses fuente variable si solo cargas 1-2 pesos: pesa más que 2 estáticas. No hagas kinetic type esencial para leer. Evita el default AI-slop de Inter/Poppins en TODO: reserva un display serif de alto contraste para el hero.

---

## 8. Bento grid

**Propósito:** layout premium por defecto de 2026 — asimétrico, celdas de tamaños distintos, cada vez más interactivo. Con `grid-template-areas` + spans por breakpoint.

```css
.bento {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(160px, auto);
}
.bento > .lg { grid-column: span 2; grid-row: span 2; }
.bento > .wide { grid-column: span 2; }

@media (max-width: 720px) {
  .bento { grid-template-columns: repeat(2, 1fr); }
  .bento > .lg, .bento > .wide { grid-column: span 2; grid-row: auto; }
}
```

Tailwind:

```html
<div class="grid grid-cols-2 md:grid-cols-4 auto-rows-[minmax(160px,auto)] gap-4">
  <div class="md:col-span-2 md:row-span-2 rounded-2xl shadow-[var(--elev-2)]">…</div>
  <div class="md:col-span-2 rounded-2xl">…</div>
</div>
```

Subgrid para alinear título/cuerpo/CTA de cada tile a filas compartidas (Baseline **Widely** desde 15-mar-2026):

```css
@supports (grid-template-rows: subgrid) {
  .bento > .tile { display: grid; grid-row: span 3; grid-template-rows: subgrid; }
}
```

> **No hagas esto:** el hero centrado sobre 3 cards iguales (patrón OUT / tell AI-slop). No hagas todas las celdas del mismo tamaño (deja de ser bento, es un grid plano). No dependas de subgrid sin `@supports` en 2026 aunque sea Widely — degrada a alineación manual, no a layout roto.

---

## 9. Micro-interacción en hover SIN layout shift

**Propósito:** feedback crafted sin reflow. Solo `transform`/`opacity`; la profundidad se cambia en una capa aparte, no en el `box-shadow` del elemento.

```css
.tile {
  position: relative;
  transition: transform 180ms ease-out;
  will-change: transform;
}
.tile::after {                 /* capa de elevación pre-renderizada, se sube su opacity */
  content: "";
  position: absolute; inset: 0;
  border-radius: inherit;
  box-shadow: var(--elev-3);
  opacity: 0;
  transition: opacity 180ms ease-out;
  pointer-events: none;
}
@media (prefers-reduced-motion: no-preference) {
  .tile:hover, .tile:focus-visible { transform: translateY(-3px); }
  .tile:hover::after, .tile:focus-visible::after { opacity: 1; }
}
```

`:has()` para que el padre reaccione al estado de un hijo (JS-free, Baseline Widely desde fin 2023):

```css
.card:has(:focus-visible) { outline: 2px solid var(--accent); }
```

> **No hagas esto:** hover que cambia `padding`, `border-width`, `font-size`, `width` o `margin` → empuja a los vecinos (CLS + jank). No uses `transform: scale()` en texto (blur en subpíxel). No olvides `:focus-visible` junto a `:hover` (accesibilidad de teclado). No dejes `will-change` permanente en cientos de elementos (agota memoria de compositor).

---

## 10. Texto con gradiente

**Propósito:** acento tipográfico premium, colores tomados de tus tokens.

```css
.gradient-text {
  background: linear-gradient(90deg, var(--brand-1), var(--brand-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
@supports not (background-clip: text) {   /* fallback: color sólido legible */
  .gradient-text { color: var(--brand-1); background: none; }
}
```

Tailwind: `bg-gradient-to-r from-brand-1 to-brand-2 bg-clip-text text-transparent`.

> **No hagas esto:** gradiente morado→azul (`#7C3AED → #2563EB`), el fingerprint exacto del AI-slop landing. No apliques gradient-text a párrafos largos ni a texto pequeño (contraste impredecible, falla AA). Deriva los dos colores de la paleta core con `color-mix()`/relative color, no inventes un gradiente ajeno a la marca.

---

## 11. Bordes animados

**Propósito:** borde con brillo/rotación como acento vivo. La palanca real es `@property` (Baseline Newly, 9-jul-2024): registra el ángulo como tipo para que el gradiente **interpole** en vez de saltar.

```css
@property --angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}
.animated-border {
  position: relative;
  border-radius: 16px;
  background: var(--surface) padding-box;   /* contenido */
  border: 1.5px solid transparent;
  background-image:
    linear-gradient(var(--surface), var(--surface)),
    conic-gradient(from var(--angle), var(--brand-1), var(--brand-2), var(--brand-1));
  background-origin: border-box;
  background-clip: padding-box, border-box;
}
@media (prefers-reduced-motion: no-preference) {
  .animated-border { animation: spin-border 6s linear infinite; }
}
@keyframes spin-border { to { --angle: 360deg; } }
```

- Sin `@property`, el navegador **no anima** `--angle` → se ve el gradiente estático (degradación limpia, sin gate).
- Anima **una custom property** (interpolada en compositor-friendly), no `background-position`.

> **No hagas esto:** simular el borde con un `::before` blurreado que anima `filter`/`box-shadow` en loop (repintado constante, chupa batería). No pongas bordes animados en más de 1-2 controles por vista (ruido). Confina el brillo al acento único de la paleta, no arcoíris.

---

## Anexo — Primitivas CSS 2026 que hacen que la página se sienta "tipografiada" a mano

La capa invisible que el output templated/AI se salta (GDM Pixel):

```css
/* Derivar sistema tonal desde UN token — sin preprocesador */
:root {
  --brand: oklch(0.62 0.19 265);
  --brand-hover: color-mix(in oklab, var(--brand), black 12%);   /* Widely */
  --brand-tint: oklch(from var(--brand) calc(l + 0.15) c h);      /* relative color, Newly → dar fallback */
}
/* Type/space que escala al TAMAÑO del contenedor, no del viewport */
@container (min-width: 30rem) { .card-title { font-size: clamp(1rem, 4cqi, 1.6rem); } }
.card { container-type: inline-size; }
/* Nesting con & (evita el bug de type-selector desnudo en Chrome 112-119 / Safari 16.5-17.1) */
.btn { &:hover { filter: brightness(1.05); } }
```

Reglas: `container-type` + `cqi` para componentes modulares (bento/cards), `:has()` para estado contextual, `text-wrap: balance` en headings (`pretty` solo como enhancement — sin Firefox estable), `color-mix()`/relative color para derivar tints/glass desde tokens. Siempre declara el fallback plano **antes** de la versión con relative color, o gatéala con `@supports`.

## Checklist de rendimiento y a11y (aplica a TODAS las recetas)

- [ ] Todo `@keyframes`/`transition` con movimiento vive dentro de `@media (prefers-reduced-motion: no-preference)`.
- [ ] Se anima solo `transform`/`opacity` (o una custom property registrada con `@property`). Cero `box-shadow`/`width`/`top` en loop.
- [ ] Ninguna animación es la única forma de ver contenido (estado base = visible).
- [ ] `backdrop-filter`, blur y grano: capa pequeña, estática, con fondo sólido de fallback (`@supports not`).
- [ ] Features del bucket "gate/evita" (scroll-driven, View Transitions cross-doc, `text-wrap: pretty`, `@position-try`) van con `@supports` + fallback estático.
- [ ] `content-visibility: auto` + `contain-intrinsic-size` en secciones pesadas fuera de pantalla (Baseline Newly, 15-sept-2025) para pagar el presupuesto del movimiento.
- [ ] `:focus-visible` cubierto en cada estado `:hover`.
- [ ] Contraste texto AA verificado sobre cualquier superficie glass/gradiente/aurora.

## Notas de honestidad (para no vender humo)

- **Neumorphism / soft-UI:** vuelve, pero SOLO como acento en 1-2 controles, nunca como sistema de página. Falla afordancias y contraste WCAG si lo generalizas (Figma / Setproduct). Verifica AA a mano.
- **3D/WebGL heroes:** premium solo si la marca *es* la experiencia. Si no, es lastre de Core Web Vitals (~800KB-2MB de runtime Spline/WebGL): lazy-init post-LCP, poster estático, respeto a reduced-motion.
- **"Liquid glass":** no lo prometas en web. Ships glassmorphism disciplinado (receta 4); la refracción real es nativa.
- **Cifras de conversión/engagement de vendors** (p. ej. el "-91% de conversión del AI-slop" de Monet, o "+23% scroll-depth" de bento de Studio Meyer): son claims de un solo proveedor / data propia, no estudio independiente. Úsalas como dirección, no como hecho. No inventes números.
- **AI-slop fingerprint a invertir:** Inter/Poppins, gradiente morado→azul, todo redondeado, todo centrado, grises default de shadcn, íconos Lucide/Hero por defecto, stock photos. Cada tell tiene su reemplazo en las recetas de arriba.

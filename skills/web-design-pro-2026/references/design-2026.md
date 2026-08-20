# Lenguaje visual 2026 — catálogo de diseño premium

> Referencia operativa para producir páginas que se vean **caras y no genéricas**. Cada sección es accionable: specs, números y snippets copiables. La regla madre de todo el documento: **profundidad + textura + una decisión tipográfica fuerte + un solo acento saturado sobre base calma**. Lo plano, centrado y pastel ya lee como "AI slop" (ver §6).
>
> Terminología: "Baseline Widely" = seguro sin gate. "Baseline Newly" = seguro como enhancement con fallback. "Gate/Avoid" = feature-detect obligatorio o no usar aún. Detalle por feature en §8.

---

## 1. Principios anti-flat

El look "barato" de 2020-2023 era plano: un color sólido, una sombra dura, cero material. Salir de ahí no es decorar — es modelar **luz, material y jerarquía**. Cuatro palancas.

### 1.1 Profundidad por elevación en capas (la palanca #1)

No uses **una** `box-shadow` dura. Modela luz ambiental + luz clave con 2-3 sombras suaves de baja opacidad, más un highlight interno de 1px arriba que simula el borde iluminado. Esto es lo que separa un card plano de uno que "flota". (Layered elevation es tema anti-flat consistente en los roundups 2026 — Born Digital; TheeDigital.)

```css
:root {
  /* tokens de elevación — ambient + key light apilados */
  --elev-1: 0 1px 2px rgb(0 0 0 / .06), 0 1px 1px rgb(0 0 0 / .04);
  --elev-2: 0 2px 4px rgb(0 0 0 / .05), 0 4px 8px rgb(0 0 0 / .05),
            inset 0 1px 0 rgb(255 255 255 / .06);
  --elev-3: 0 4px 8px rgb(0 0 0 / .05), 0 12px 24px rgb(0 0 0 / .08),
            0 1px 2px rgb(0 0 0 / .06), inset 0 1px 0 rgb(255 255 255 / .08);
}
.card { box-shadow: var(--elev-2); border: 1px solid rgb(255 255 255 / .04); }
.card:hover { box-shadow: var(--elev-3); }
```

**Regla de calibración:** en dark mode las sombras casi no se ven — la profundidad la aporta el **inset highlight** y un borde `1px` semitransparente, no la sombra. En light mode, al revés.

### 1.2 Textura sobre superficies lisas

Un gradiente perfectamente liso lee estéril. La capa de acabado más barata y "premium" es **grano/ruido** encima, generado con SVG `feTurbulence` (GPU-cheap, sin PNG). La técnica es vieja (~2021, CSS-Tricks "Grainy Gradients", Jimmy Chion — https://css-tricks.com/grainy-gradients/) pero hoy es acabado por defecto en héroes con gradiente.

```css
/* grano como overlay — data-URI SVG, ~1KB, sin request extra */
.grain::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  opacity: .06; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```

Opacidad útil: **4-8%** sobre gradientes; 2-4% sobre fotos. Más de 10% ensucia.

### 1.3 Movimiento con propósito (no decorativo)

El baseline de motion que separa "artesanal" de "genérico": **uno o dos movimientos bien puestos, ≤300ms, ease-out**, que respondan a intención del usuario, no que se muevan solos. (Restraint-based motion — Monet; Index.dev.) Kinetic type y parallax se reservan a héroe/transiciones de sección (§4.2), nunca en todo.

- Duración: micro-interacción `120-200ms`; transición de sección `250-400ms`.
- Easing: `cubic-bezier(.2,.8,.2,1)` (ease-out expresivo) para entradas; nunca `linear` salvo loops de ambiente.
- **Todo** movimiento va envuelto en `prefers-reduced-motion` (§8, obligatorio).

### 1.4 Tipografía como arte, no como texto

La tipografía es la decisión de diseño de mayor ROI. Un display oversized con buen tracking convierte una página plana en editorial sin agregar un solo gráfico. Detalle en §4. Principio: **una** familia expresiva para el impacto (display/serif de alto contraste), una neutra legible para el cuerpo — nunca Inter en todo.

---

## 2. Catálogo de direcciones estéticas 2026

Cada dirección con **cuándo usarla** y **cuándo NO**. No son excluyentes salvo donde se indica; se combinan (p.ej. base calma dark + bento + aurora hero + grano).

| Dirección | Qué es | Cuándo usarla | Cuándo NO | Confianza |
|---|---|---|---|---|
| **Base calma dark-first** | Near-black tintado (zinc), un acento saturado, textura visible | Default premium para SaaS, portafolio, producto | — (es el default) | Alta |
| **Glassmorphism disciplinado** | Panel `rgba` + `backdrop-filter: blur` + borde 1px | Nav sticky, modales, cards sobre fondo con color/foto | Sobre fondo plano liso (no hay qué refractar); texto largo | Alta |
| **Aurora / mesh gradient** | 2-4 blobs radiales difusos, baja saturación, deriva lenta + grano | Fondo de héroe atmosférico, secciones de respiro | Detrás de tablas/datos densos; marcas ruidosas | Alta |
| **Dithering** | Gradiente bandeado, paleta limitada (4-8 colores), Bayer/Floyd-Steinberg | Textura retro-digital fresca, cover art, secciones de marca | Donde se necesite suavidad fotográfica | Media |
| **Bento grid** | Grid asimétrico de tiles de distinto tamaño, a veces interactivos | Feature overview, "cómo funciona", dashboards de landing | Narrativa lineal larga; formularios | Alta |
| **Tipografía-como-arte** | Display oversized + serif de alto contraste | Héroe, editorial, portafolio, marca con voz | UI densa de app; donde legibilidad manda sobre impacto | Alta |
| **Texture maximalism** | Collage, sticker/cutout, papel roto, chrome/pixel retrofuturista | Marca expresiva, música, moda, eventos, indie | B2B serio, fintech, salud; riesgo kitsch | Media |
| **Anti-grid / neo-brutalist** | Ruptura deliberada del grid, bordes duros, contraste alto | Diferenciación cuando todos convergen en bento pulido | Si sacrifica foco/contraste (a11y); productos que exigen confianza | Media |
| **Neumorphism / soft-UI** | Relieve extruido suave, sombra doble | **Solo** 1-2 controles de acento (toggle, play) | Como sistema de página; afordancias/contraste fallan WCAG | Media |
| **3D / WebGL hero** | Escena interactiva Spline/Three | Solo si la marca **ES** la experiencia (3D/producto/juego) | Todo lo demás — es pasivo de Core Web Vitals | Alta |

### 2.1 Base calma dark-first (el default)

Dark mode como **expresión de marca diseñada**, no como toggle. La base dominante premium es un near-black **tintado con zinc**, nunca `#000` puro (Recursion, UI color trends 2026 — https://recursion.agency confirma `#09090B` y adopción dark-mode 80%+). Negro puro lee barato y vibra contra texto blanco.

```css
:root {
  /* rampa neutra zinc-tinted — nunca #000 */
  --bg:      #09090B; /* base */
  --surface: #101013;
  --surface-2:#18181B;
  --border:  #27272A;
  --text:    #FAFAFA;
  --text-dim:#A1A1AA;
  --accent:  #6EE7B7; /* UN acento saturado (ejemplo) */
}
```
*(No hay evidencia verificada de un aumento de engagement cuantificado por dark mode — no cites cifras; la premisa de la rampa se sostiene sola.)*

### 2.2 Glassmorphism disciplinado (NO "liquid glass" falso)

Apple presentó **"Liquid Glass"** en WWDC 2025 — pero la refracción real (specular, tinte adaptativo, distorsión del fondo) es **nativa, no web**. En web se envía glassmorphism disciplinado: fill `rgba` + `backdrop-filter` + borde. No finjas liquid glass con CSS; no se puede refractar en CSS puro (Setproduct comparison).

```css
.glass {
  background: rgb(255 255 255 / .06);
  backdrop-filter: blur(16px) saturate(1.4);
  -webkit-backdrop-filter: blur(16px) saturate(1.4); /* Safari viejo */
  border: 1px solid rgb(255 255 255 / .12);
  border-radius: 16px;
}
@supports not (backdrop-filter: blur(1px)) {
  .glass { background: rgb(20 20 24 / .92); } /* fallback sólido */
}
```

**Regla WCAG-AA:** detrás de texto, el tinte debe ser suficientemente sólido para pasar contraste AA por sí solo — nunca dependas del blur para legibilidad. El blur es caro en GPU: capa pequeña, no animar el `blur()`.

### 2.3 Aurora / mesh gradient

Distinto del gradiente arcoíris "candy stripe" de 2021. Aurora = **lavados fríos de baja saturación**, blur atmosférico, movimiento lento (20-40s), grano encima. Mesh de 2-4 blobs radiales.

```css
.aurora {
  position: relative; overflow: hidden; background: var(--bg);
}
.aurora::before {
  content:""; position:absolute; inset:-40%;
  background:
    radial-gradient(40% 50% at 20% 30%, #3b82f6aa, transparent 60%),
    radial-gradient(45% 55% at 80% 20%, #8b5cf699, transparent 60%),
    radial-gradient(50% 60% at 60% 80%, #06b6d488, transparent 60%);
  filter: blur(60px); animation: drift 32s ease-in-out infinite alternate;
}
@keyframes drift { to { transform: translate3d(4%, -3%, 0) rotate(8deg); } }
@media (prefers-reduced-motion: reduce){ .aurora::before{ animation:none; } }
```
Encima, la capa `.grain` de §1.2. Generadores de mesh: MagicPattern (https://www.magicpattern.design).

### 2.4 Dithering

El movimiento de textura más plausiblemente **nuevo para 2026**, distinto del grano aleatorio: cuantización a 4-8 colores + patrón ordenado (Bayer) o Floyd-Steinberg. Estética retro-digital, banded a propósito. (Design Magazine "How Gradients Got Rough"; Artcoast — fuentes trend, confianza media.) Se produce en export (Photoshop/ImageMagick `-dither`, o shader), no en CSS puro.

### 2.5 Texture maximalism

Polo opuesto a la base calma — coexisten según marca. Collage, sticker/cutout con sombra de recorte, papel roto, chrome/pixel retrofuturista. (Figma 2026 trends; Artcoast — confianza media, riesgo kitsch alto.) Úsalo con intención de marca o se ve amateur. No mezclar con bento pulido en la misma vista.

### 2.6 Anti-grid / neo-brutalist

Contra-movimiento legítimo de diferenciación mientras todos convergen en bento (Studio Meyer reality-check; Fireart, confianza media). Encuádralo como **clarificar, no shockear**. Caveat a11y crítico: el brutalismo suele regresar foco visible y contraste — verifica AA y `:focus-visible` explícito.

### 2.7 Neumorphism / soft-UI

Vuelve **solo como acento** en 1-2 controles, tratado como riesgo de reciclaje (Figma; Setproduct, media). El modo de fallo de 2020 es real: afordancias invisibles y contraste que falla WCAG. Úsalo en un toggle o botón de play, nunca como sistema de página, y verifica AA.

### 2.8 3D / WebGL hero

Premium **solo cuando la marca ES la experiencia** (Studio Meyer reality-check; Figma). Si no, es pasivo de Core Web Vitals — el runtime de Spline/WebGL pesa del orden de ~800KB-2MB. Mitigaciones si va: lazy-init **después** del LCP, poster estático como primer paint, desactivar bajo `prefers-reduced-motion`.

---

## 3. Color & gradientes 2026

### 3.1 La fórmula ganadora

**Base neutra calma + UN acento saturado + textura visible**, y **cada gradiente sale de dos colores que ya están en tus tokens** (Recursion; Lounge Lizard; Figma 2026 color). El acento saturado como micro-glow de "dopamina", no como fondo de página.

| DO | DON'T |
|---|---|
| Un solo acento saturado, usado con parquedad | 3-4 colores de marca compitiendo |
| Gradiente entre dos tokens existentes | Gradiente de colores random fuera de la paleta |
| Neutros tintados (zinc/slate/stone), no grises `shadcn` default | Grises `#888` planos por defecto |
| Acento como glow/estado/foco | Acento como fondo de secciones enteras |

### 3.2 Sistemas tonales sin preprocesador

Deriva toda la rampa de **un** token con `color-mix()` (Baseline Widely) y relative color syntax (Baseline Newly). Sin Sass.

```css
:root {
  --brand: oklch(70% .17 160);
  --brand-tint:  color-mix(in oklab, var(--brand) 20%, var(--bg));
  --brand-shade: color-mix(in oklab, var(--brand) 70%, black);
  /* relative color: mismo hue, más claro y con alpha */
  --brand-hi: oklch(from var(--brand) calc(l + .12) c h);
  --glass-tint: oklch(from var(--brand) l c h / .08);
}
```
Trabaja en **oklch/oklab**: mezclas perceptualmente uniformes, sin zonas muertas grisáceas que da el sRGB. Da siempre una declaración de fallback plana antes de `color-mix`/relative color, o gate con `@supports`.

### 3.3 Gradientes animables con `@property`

`@property` (Baseline Newly, 2024-07-09) hace interpolables los custom properties tipados — habilita gradientes cónicos/lineales animados, bordes de gradiente rotatorios, hue-shifts. Sin soporte, se renderiza el gradiente estático inicial (sin romper).

```css
@property --angle { syntax: "<angle>"; initial-value: 0deg; inherits: false; }
.ring {
  border: 2px solid transparent;
  background:
    linear-gradient(var(--bg), var(--bg)) padding-box,
    conic-gradient(from var(--angle), var(--accent), #8b5cf6, var(--accent)) border-box;
  animation: spin 6s linear infinite;
}
@keyframes spin { to { --angle: 360deg; } }
@media (prefers-reduced-motion: reduce){ .ring{ animation:none; } }
```

---

## 4. Tipografía expresiva 2026

### 4.1 Display oversized + revival de serif de alto contraste

Contra el "Inter en todo": headlines display enormes con tracking negativo, y revival de **serifs de alto contraste** (estilo Denton) para impacto editorial/héroe (DesignMonks; IK Agency; Creative Bloq 2026). Los nombres de fuente son ejemplos, no prescripción.

```css
.display {
  font-size: clamp(2.75rem, 6vw + 1rem, 7rem);
  line-height: .95;
  letter-spacing: -0.03em;      /* tracking negativo en tamaños grandes */
  text-wrap: balance;           /* headings equilibrados, Baseline Newly */
  font-weight: 600;
}
p { text-wrap: pretty; }        /* reduce huérfanos — enhancement, sin Firefox stable */
```

Reglas:
- **Tracking negativo** solo en tamaños grandes (`> ~2rem`); en cuerpo, tracking normal o ligeramente positivo.
- `line-height` cae hacia `.9-1.0` en display, sube a `1.5-1.7` en cuerpo.
- `text-wrap: balance` en todos los headings (§8, seguro). `text-wrap: pretty` para huérfanos de cuerpo es enhancement (no hay Firefox stable a inicios 2026) — degrada a wrap normal, sin gate.
- Par tipográfico: **una** display expresiva + **una** neutra legible. Nunca tres familias.

### 4.2 Variable fonts + kinetic type (con freno)

Animar `font-variation-settings` (peso/anchura por interacción/scroll) es una palanca premium real. Pero kinetic type pelea con screen readers y crawlers, mete CLS y castiga Core Web Vitals (Studio Meyer reality-check). Confínalo a **héroe/transiciones de sección** y gate con `prefers-reduced-motion`.

```css
@media (prefers-reduced-motion: no-preference) {
  .kinetic { transition: font-variation-settings .3s ease; }
  .kinetic:hover { font-variation-settings: "wght" 720, "wdth" 110; }
}
```
No animes el peso de párrafos de cuerpo (relayout constante). Reserva la variación a titulares y a estados de interacción puntuales.

---

## 5. Sistemas de layout

### 5.1 Bento grid (el default premium)

Patrón asentado en 2026, no novedad — asimétrico y cada vez más interactivo (Studio Meyer reality-check; adopción amplia en big-tech, reportada por la agencia como observación propia, dirección creíble). Construcción: `grid-template-areas`, spans por breakpoint, tiles con hover-expand.

```css
.bento {
  display: grid; gap: clamp(.75rem, 2vw, 1.25rem);
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: minmax(160px, auto);
}
.bento > .lg { grid-column: span 2; grid-row: span 2; }
.bento > .wide { grid-column: span 2; }
@container (max-width: 640px) {   /* container query, no media query */
  .bento { grid-template-columns: 1fr 1fr; }
  .bento > .lg, .bento > .wide { grid-column: span 2; }
}
```
*(No cites cifras de scroll-depth: el "+23%" que circula es dato propio de una agencia sobre su clientela, anecdótico. La técnica se sostiene sin la cifra.)*

- Asimetría intencional: un tile hero grande + satélites. Evita 4 tiles iguales (eso es el patrón slop, §6).
- Tiles interactivos: hover-expand, preview inline, mini-charts.
- **Subgrid** para alinear el contenido interno de cada tile a las pistas del padre (§8, Baseline Widely desde 2026-03-15).

### 5.2 Editorial / magazine

Grid multi-columna con **subgrid** para que título/cuerpo/CTA de cards hermanas compartan filas sin alturas hardcodeadas.

```css
.article-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
.article-grid .card {
  display: grid; grid-row: span 3;
  grid-template-rows: subgrid;  /* filas heredadas del padre */
}
@supports not (grid-template-rows: subgrid) {
  .article-grid .card { grid-template-rows: auto 1fr auto; }
}
```

### 5.3 Scroll-telling

Narrativa guiada por scroll. En 2026 corre en **CSS nativo** con scroll-driven animations (`animation-timeline: scroll()/view()`), off-main-thread, cero JS — **pero NO es Baseline** (Firefox tras flag en stable hasta v152, jun 2026; prioridad Interop 2026). Es **enhancement-only**: gate con `@supports`, fallback estático, nunca hagas depender la visibilidad del contenido del efecto.

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    @keyframes reveal { from { opacity:0; transform: translateY(24px); } }
    .reveal {
      animation: reveal linear both;
      animation-timeline: view();
      animation-range: entry 0% cover 30%;
    }
  }
}
/* sin soporte: .reveal queda visible por defecto — no se oculta nunca */
```
Alternativa portable (con Firefox incluido): polyfill de Bramus, o `IntersectionObserver` para el reveal. Para MPA con morph entre páginas, ver View Transitions cross-doc (§8, aún sin Firefox → enhancement).

---

## 6. Qué está OUT / "AI slop"

### 6.1 El fingerprint de la landing "AI slop"

Bien documentado (Monet "Escape AI Slop" — https://www.monet.design; corroborado por 925studios, Developers Digest). Memoriza los tells e **invierte cada uno**:

| Tell de slop | Inversión premium |
|---|---|
| Inter / Poppins en todo | Display expresiva + serif de alto contraste + una neutra (§4) |
| Gradiente morado→azul | Un acento saturado sacado de tokens + aurora de baja saturación (§3) |
| Todo redondeado (`rounded-2xl` everywhere) | Radios variados e intencionales; algún borde recto |
| Todo centrado | Asimetría, grid editorial/bento, alineación a la izquierda (§5) |
| Grises `shadcn` default | Neutros tintados zinc/slate (§2.1) |
| Íconos Lucide/Hero genéricos | Set de íconos con peso/estilo propio o custom |
| Fotos de stock | Imágenes reales, ilustración propia, o textura/3D de marca |
| 3 cards iguales bajo un hero centrado | Bento asimétrico (§5.1) |
| Una sombra dura plana | Elevación en capas (§1.1) |
| Gradiente liso estéril | Gradiente + grano (§1.2) |

*(Monet cita "~91% menos conversión" para páginas slop — es afirmación de un solo vendor con interés comercial, no estudio independiente. Úsala como claim de proveedor, no como hecho establecido.)*

### 6.2 Direcciones DATADAS / retiradas

Cada una con su reemplazo nombrado (TinyFrog in/out; Figma; Wix 2026):

| OUT (se ve barato) | IN (reemplazo) |
|---|---|
| Flat design puro | Profundidad por elevación en capas (§1.1) |
| Hero centrado sobre 3 cards iguales | Bento asimétrico (§5.1) |
| Pastel plano "corporate Memphis" | Base calma + acento dopamina + textura (§2.1, §3) |
| Fotos de stock genéricas | Imagen real / ilustración / textura de marca |
| Parallax pesado en JS | Scroll-driven CSS nativo (§5.3) |
| Negro puro `#000` | Near-black zinc-tinted `#09090B` (§2.1) |

---

## 7. Tabla maestra DO / DON'T

| DO | DON'T |
|---|---|
| Elevación en capas: 2-3 sombras suaves + inset highlight | Una sola `box-shadow` dura y plana |
| Grano `feTurbulence` a 4-8% sobre gradientes | Dejar el gradiente liso y estéril |
| Base zinc-tinted `#09090B`, dark como marca | `#000` puro; grises `shadcn` default |
| UN acento saturado, usado con parquedad | 3-4 colores de marca compitiendo |
| Gradientes derivados de dos tokens existentes | Gradiente morado→azul random fuera de paleta |
| Display oversized + serif alto contraste + neutra | Inter/Poppins en todos los pesos y roles |
| `text-wrap: balance` en headings | Headings con líneas huérfanas descuadradas |
| Bento asimétrico con jerarquía | 3 cards idénticas centradas bajo el hero |
| Motion ≤300ms, ease-out, con propósito, 1-2 moves | Animaciones decorativas por todos lados |
| Todo motion envuelto en `prefers-reduced-motion` | Movimiento sin gate de a11y |
| Glassmorphism con tinte AA-sólido detrás de texto | Fingir "liquid glass"; confiar legibilidad al blur |
| 3D/WebGL solo si la marca ES la experiencia | WebGL decorativo que hunde Core Web Vitals |
| Neumorphism en 1-2 controles, contraste AA verificado | Neumorphism como sistema de página |
| Scroll-driven CSS con `@supports` + fallback | Parallax pesado en JS en el hilo principal |
| Radios e íconos intencionales y variados | Todo `rounded-2xl` + íconos genéricos default |
| Imagen real / ilustración / textura de marca | Fotos de stock |

---

## 8. Capa CSS invisible — lo que hace la página "bespoke"

Los primitivos modernos de CSS son la capa que el output de IA templatizado se salta y que hace que una página se sienta tipografiada a mano (GDM Pixel). **Triage de producción 2026** — método universal: feature-detect, reglas aditivas, motion siempre bajo `prefers-reduced-motion`.

### SHIP FREELY (Baseline Widely — sin gate)

| Feature | Uso | Nota |
|---|---|---|
| **Container queries + unidades `cqi/cqw`** | Componentes que se estilan por su **propio** tamaño; backbone de bento/modular | Chrome/Edge 105+, FF 110+, Safari 16+. Fallback: `@supports(container-type)` o media-query base |
| **`:has()`** | Estado sin JS: padre reacciona a hijo (`:checked`, `:focus`, quantity queries) | Baseline fin 2023 (FF 121 cerró el set). Mantén reglas aditivas |
| **CSS Nesting** | Co-locar hover/media/container dentro del bloque del componente | Chrome 112+, FF 117+, Safari 16.5+. Caveat: en builds viejos, inicia selector de tipo anidado con `&` o `:is()` |
| **`color-mix()`** | Rampas/tints/shades/overlays de glass desde un token (§3.2) | Chrome 111+, Safari 16.2+, FF 113+. Da fallback plano primero |
| **Subgrid** | Alinear grids anidados a las pistas del padre; magazine/bento (§5.2) | **Baseline Widely 2026-03-15**. Fallback `@supports`: degrada solo alineación |
| **`prefers-reduced-motion`** | Gate a11y de **todo** motion | Baseline Widely ~2020. Es la capa de fallback |
| **`backdrop-filter`** | Glassmorphism (§2.2) | Baseline Newly ~2024-09 (Safari 18 sin prefijo). Deja `-webkit-`, fondo sólido de fallback, no animes el blur |

### ENHANCEMENT (Baseline Newly — usar con fallback)

| Feature | Uso | Nota |
|---|---|---|
| **`@property`** | Gradientes/ángulos/hues animables (§3.3) | Baseline 2024-07-09. Sin soporte: gradiente estático inicial |
| **Relative color syntax** | Derivar tints/alpha de un token (§3.2) | Baseline Newly mediados 2024. Fallback plano o `@supports` |
| **View Transitions same-document** | Morphs shared-element/list-detail | Baseline Newly 2025-10-14 (FF 144). Feature-detect `startViewTransition`; gate motion |
| **`text-wrap: balance`** | Headings equilibrados (§4.1) | Baseline Newly. Degrada a wrap normal |
| **`content-visibility: auto`** | Difiere layout/paint off-screen; presupuesto de perf en páginas con motion | Soporte real: Chrome 85+, Firefox ~125+, Safari ~18 (verifica en caniuse). Pareja con `contain-intrinsic-size` para no saltar el scroll |
| **CSS Anchor Positioning (core)** | Tooltips/popovers/menús tethered en CSS puro (reemplaza Floating UI) | Baseline 2026 (FF 147 stable, 2026-01-13). `@position-try`/flip necesita Chrome 125+/FF 147+/Safari 26+ → trata el auto-flip como enhancement; polyfill OddBird |

### GATE / AVOID (aún no Baseline — feature-detect obligatorio o no usar)

| Feature | Estado | Regla |
|---|---|---|
| **Scroll-driven animations** (`animation-timeline`) | Chrome/Edge 115+, Safari 26+; **Firefox tras flag en stable hasta v152 (jun 2026)** | `@supports(animation-timeline: view())` + fallback estático + dentro de `prefers-reduced-motion`; nunca condiciones de visibilidad. Polyfill Bramus |
| **View Transitions cross-document (MPA)** | Chrome 126+/Safari 18.2+, **sin Firefox** | Enhancement; no-op a navegación instantánea. `@view-transition { navigation: auto }` |
| **`text-wrap: pretty`** | Chrome 117+ (limitado a últimas ~4 líneas), Safari 17.5+; **sin Firefox stable** | Degrada a wrap normal, sin gate necesario. No cuentes con ello |
| **`@position-try` en Safari viejo** | Requiere Safari 26+ | Fallback de posición fija o polyfill OddBird |

### Método universal (cablea esto en cada proyecto)

1. **Feature-detect** con `@supports` (o `CSS.supports()` en JS), nunca sniff de navegador.
2. **Reglas aditivas**: el enhancement se suma sobre una base que ya funciona sola.
3. **Todo motion** dentro de `@media (prefers-reduced-motion: no-preference)`; además neutraliza `::view-transition-group { animation-duration: 0 }` bajo `reduce`.
4. **Nunca** hagas depender la visibilidad/legibilidad del contenido de una feature gated.

---

### Nota lateral: legibilidad para máquinas (baja confianza, fuera del track visual)

Trata la legibilidad-para-máquinas como un **deliverable** más: datos estructurados Schema.org para visibilidad en búsqueda/AI (GEO). Es dirección real pero es el ítem de menor encaje en un track *visual*, y las afirmaciones fuertes sobre `llms.txt`/`agents.json` como requisito y cifras de citaciones son de un solo proveedor y no probadas — no las cites como hecho. Entrega el structured data; no construyas estrategia sobre las cifras.

---

## Cierre — oportunidades de mejora al usar esta referencia

1. **Verifica Baseline antes de cada release.** Las fechas de §8 son de inicios/mediados 2026; `content-visibility` en Chrome shipeó en v85 (no v108, imprecisión conocida en la fuente) y Firefox mueve scroll-driven animations activamente. Revalida en caniuse/web.dev al momento de shipear, no confíes en la tabla congelada.
2. **El riesgo #1 es sobre-aplicar.** Este catálogo tiene polos opuestos (base calma vs. texture maximalism, bento vs. anti-grid). Elige **una** dirección dominante por página; mezclarlas todas produce ruido, no premium.
3. **a11y es donde estas técnicas fallan callado.** Glass, neumorphism y brutalism regresan contraste/foco. Corre un check AA real (no a ojo) sobre texto-sobre-glass y estados `:focus-visible` antes de dar por hecho cualquier página.
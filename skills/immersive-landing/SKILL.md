---
name: immersive-landing
description: >-
  Estándar CANÓNICO y OBLIGATORIO para TODA página/landing/sitio/web/homepage/one-pager
  que se pida. Nunca generar una página estática por defecto: siempre una experiencia
  INMERSIVA scroll-driven con la mejor visualización posible (video real fundido +
  transiciones cinematográficas + tipografía serif + scroll desacoplado). Se dispara al
  crear/hacer/diseñar/mejorar/rediseñar: "crea una landing / una web / una página / un
  sitio / algo increíble para [cliente]", "landing page", "hazme la página de", "diseño
  web", "homepage", "portfolio", "one-pager", o cualquier .html/.tsx/.jsx/.vue/.svelte/.astro
  que se renderice en navegador. Va SIEMPRE dentro del pipeline de diseño web (junto a
  web-design-pro-2026): no es opcional. Aplica a cualquier rubro, no solo café.
aliases: immersive-landing
metadata:
  type: reference
---

# immersive-landing — el default de diseño de páginas de Cristian

> **Regla de existencia (Cristian, 2026-07-31):** *"esto va a estar SIEMPRE en los
> pipelines y en todo que le pida páginas y diseño web."* Esta skill es el **front door
> obligatorio** para cualquier página. Si te piden una web y NO estás aplicando esto,
> estás incumpliendo. No entregar páginas estáticas planas — **jamás por defecto.**

Validada con el primer caso real: **MERIDIANO** (café) → aprobada ("súper genial, me
encanta") y desplegada: `github.com/cdgutierrez6/meridiano-cafe` ·
`meridiano-cafe-six.vercel.app`. La receta de abajo es la que él aprobó.

---

## 1. Regla de oro — desacoplar el scroll del DOM

Capturar el progreso de scroll como **un número 0→1** y usarlo para animar
cámara / objetos / **video** / opacidades / color de luz / capítulos. **Nunca** depender
del scroll nativo crudo: siempre un valor **suavizado (inercia)** que el render lee.

```js
smoothScroll += (targetScroll - smoothScroll) * 0.085;   // inercia
const t = clamp(smoothScroll / maxScroll, 0, 1);          // reloj maestro 0..1
// t controla TODO: opacidad de clips, cortina de humo, glow, parallax, beats de texto.
```

**Invariante inquebrantable:** el héroe/media debe ser **función pura del progreso** →
scrollear hacia arriba **revierte** la animación (reversibilidad). Nunca un "video de una
sola dirección".

---

## 2. Fase Discovery OBLIGATORIA antes de instalar o programar

Responder en **máximo 5 líneas** y **esperar el "ok"** del usuario:

1. **Concepto narrativo** — qué historia cuenta el scroll (el "viaje").
2. **Rubro + emoción objetivo** — qué debe sentir el visitante.
3. **Arquetipo recomendado** (A / B / C, ver §3).
4. **Paleta + tipografía** (acento único; display serif/grotesk + body sans).
5. **Mapa de 4–7 secciones/beats** (el recorrido).

No instalar dependencias ni escribir código hasta el "ok". (Para T0/T1 no impongas
ceremonia extra; el Discovery de 5 líneas ES la ceremonia mínima.)

---

## 3. Los 3 arquetipos

- **(A) 3D real — Three.js / React Three Fiber.** Modelos `.glb`+Draco o terreno desde
  heightmap, iluminación HDRI, shaders. Para **producto físico premium** o presupuesto
  alto. Requiere proyecto (Next.js), NO cabe en un artefacto con CSP.
- **(B) VIDEO cinematográfico fundido — DEFAULT RECOMENDADO** *(el que Cristian aprobó)*.
  Clips reales **sobre fondo NEGRO** (generados con Flow/Veo, §7) a **pantalla completa**,
  fundidos con la escena vía `mix-blend-mode: screen` + máscara radial (luma-key) → el negro
  desaparece y el media **flota como parte de la página**. Transiciones = **cortina de humo**
  (§6). Tipografía serif. Sin cajas, sin rail, sin cortes: **un solo flujo**.
- **(C) Mixto / custom no-3D** — CSS/canvas (parallax, figura ancla, campo de partículas)
  o **no-code (Webflow + GSAP)** para entrega ultra-rápida. *(Corrección de investigación:
  C NO es solo "no-code"; es "custom no-3D o mixto". El 3D real (A) no es raro entre sitios
  premiados — 3 de 7 referencias lo eran.)*

> **Metáfora ≠ técnica.** "Las imágenes se desacoplan y se reintegran" es la *sensación*,
> no una única técnica. El invariante real compartido por los sitios premiados (tabasco,
> everest, ricardochance) es: **un progreso 0→1 transforma de forma reversible un héroe
> coherente**. La transición puede ser: cortina de humo (default aprobado), morph de
> partículas, crossfade de capas, o shader. **Cristian prefiere la cortina de humo; las
> partículas las descartó** ("las partículas sobran").

---

## 4. Stack base

- **Next.js + TypeScript + Tailwind** (proyecto real) · o **HTML+CSS+JS vanilla** self-contained/hosteable.
- **lenis** (scroll suave) · **gsap + @gsap/react** (ScrollTrigger pin/scrub) · **framer-motion**.
- **three + @react-three/fiber + @react-three/drei** — SOLO arquetipo A.
- Versiones de referencia: **GSAP 3.14.x · Lenis 1.3.x · Three r165+**.
- **Modo vanilla (CSP estricta / self-contained):** sustituir sin librerías —
  Lenis → `lerp` propio · GSAP scrub → rAF + timeline manual · SplitText → span por char ·
  Three → raw-GL o canvas 2D. (El caso MERIDIANO es vanilla puro y funciona.)

---

## 5. Pipeline fijo de 10 pasos

1. **Discovery** (§2) → esperar "ok".
2. **Scaffold con `prefers-reduced-motion` desde el día 1** (fallback accesible primero, nunca bolt-on).
3. **Generar media** — arquetipo B: generar clips de video vía **Flow/Veo** (§7), uno por beat +
   **un clip de humo para las transiciones**, todos **sobre negro**; descargar, transcodear
   (mute + faststart + compresión). Arquetipo A: modelar/exportar `.glb`+Draco + HDRI.
4. **Motor de scroll** — Lenis + GSAP ScrollTrigger (o lerp vanilla). Reloj 0→1 (§1).
5. **Preloader temático** 0→100% que cuente la historia de la marca ("Moliendo la experiencia").
6. **Hero full-screen** — el media más característico llenando la pantalla, fundido, serif encima.
7. **Beats con media full-bleed fundido** (no cajas) + **transición cinematográfica** (§6). Sin rail.
8. **3D (A) o VIDEO (B) sincronizado al scroll.**
9. **Parallax + micro-interacciones** — cursor reactivo (glow), botón/CTA magnético, tilt por mouse.
10. **Indicador de progreso** (barra/beats) + **optimización a 60fps** (video muted playsinline
    comprimido .mp4/.webm, .webp, .glb+Draco) + **QA responsive + fallback sin animación**.

---

## 6. La transición APROBADA: cortina de humo (no partículas)

El cambio entre escenas **no** se hace con cortes ni con partículas. Se hace con **humo**:
un clip de humo sube, **nubla toda la pantalla**, y al despejarse **emerge el siguiente
video**. Es el conector narrativo. Receta:

```js
// dentro del reloj 0..1, por tramo entre beat i → i+1:
const smokeTrans = clamp(Math.sin(tt*Math.PI)*1.5, 0, 1);      // sube y despeja
SMOKE.style.opacity = clamp(0.12 + smokeTrans*0.9, 0, 1);      // humo siempre sutil + cortina
clipA.opacity = clamp(1 - tt*2, 0, 1);                          // sale bajo el humo
clipB.opacity = clamp((tt-0.5)*2, 0, 1);                        // entra al despejar
```

Media fundido = `mix-blend-mode: screen` + máscara radial:
```css
.clip{position:fixed;inset:0;object-fit:cover;mix-blend-mode:screen;
  -webkit-mask-image:radial-gradient(125% 120% at 50% 44%,#000 46%,rgba(0,0,0,.4) 73%,transparent 100%);
  mask-image:radial-gradient(125% 120% at 50% 44%,#000 46%,rgba(0,0,0,.4) 73%,transparent 100%)}
```

---

## 7. Generar los videos con Flow/Veo (vía Claude in Chrome)

**Regla:** los clips deben ir **sobre FONDO NEGRO PURO** (para que el luma-key/screen
funcione). Flujo automatizado en el Chrome del usuario:

1. `navigate` → `https://labs.google/fx/tools/flow` → **Nuevo proyecto**.
2. **Ajustes** → Generación de video: **Veo 3.1 - Fast**, **16:9**, **x1**. (Guardar.)
3. Prompt por clip (plantilla): *"Genera un video: [SUJETO] sobre FONDO NEGRO PURO absoluto,
   luz [cálida/ámbar] suave, cámara fija, cámara lenta, alta calidad, sin texto, sin objetos,
   [sujeto] aislado flotando sobre negro."* Ej.: humo/vapor · granos cayendo · chorro con
   salpicaduras. **Siempre incluir un clip de humo** (para las transiciones).
4. Aprobar la generación (~20 pts c/u, Veo Fast, ~8s). Con el usuario, "Aprobar y no volver a
   preguntar" para encadenar el lote.
5. **Descargar** cada clip en **720p (tamaño original)** → llegan a `~/Downloads`.
6. **Transcodear** (ffmpeg): `-an -c:v libx264 -crf 27 -preset veryfast -pix_fmt yuv420p -vf scale=1000:-2 -movflags +faststart`
   → mute, comprimido, web-optimizado. Guardar en `assets/`.

> ⚠️ Gasta créditos de Veo del usuario → **generar solo con su OK**. Descartar clips con
> marcas de agua / logos de otras marcas / fondo no-negro (loremflickr y stock genérico
> NO sirven: traen fondo → no se mimetizan).

---

## 8. Sub-agentes a orquestar (ver `.claude/agents/`)

- **architect** — decide arquetipo y mapa de secciones/beats (corre en Discovery).
- **flow-video** — genera los clips vía Flow/Veo en Chrome (§7), descarga y transcodea. *(B)*
- **scroll-engine** — Lenis/lerp + GSAP + desacople 0→1 + preloader + transición de humo.
- **three-agent** — escena 3D (SOLO arquetipo A).
- **motion-agent** — Framer Motion, parallax, pins, cursor reactivo, CTA magnético.
- **perf-agent** — 60fps, compresión de assets, reduced-motion, responsive, adaptive-quality; **corre SIEMPRE al final**.

**Orquestación:** `architect` en Discovery → `flow-video` (B) genera media → `scroll-engine`
y `motion-agent` en **paralelo** → `three-agent` **bloquea** a `motion-agent` en secciones 3D →
`perf-agent` al final. Dentro del pipeline general de web, esto se coordina con
`web-design-pro-2026` (estética 2026 + SEO/AEO + a11y), `frontend-senior`, `ui-ux-pro-max`,
`ux-senior` y `creative-frontend-max` (momento signature). **No sustituye — orquesta.**

---

## 9. Checklist "NO estática" (definición de TERMINADO)

- [ ] Scroll suave con **inercia** (desacoplado del DOM).
- [ ] Media **full-bleed y fundido** con la escena (no en cajas, no "video en recuadro").
- [ ] **≥3 escenas/beats** con transición cinematográfica (cortina de humo o morph con lógica).
- [ ] Un **elemento continuo/persistente** (el media fluye por toda la página; sin rail de secciones).
- [ ] **Reversibilidad**: scrollear hacia arriba revierte (media = función pura del progreso).
- [ ] **Parallax** en 2+ capas + micro-interacción de mouse (glow/tilt/CTA magnético).
- [ ] **Preloader temático** 0→100%.
- [ ] 3D (A) o **video (B)** sincronizado al scroll.
- [ ] **60fps + responsive + fallback `prefers-reduced-motion`**.
- [ ] Deployable (carpeta estática `index.html`+`assets/` o Next.js) → GitHub + Vercel.

---

## 10. Gotchas verificados (caso MERIDIANO)

- **Fondo negro es obligatorio** para el `screen`/luma-key; stock genérico trae fondo → no sirve.
- **Videos ocultos (opacity:0) pueden no decodificar** → la cortina de humo cubre el gap; además
  `autoplay muted loop playsinline` + `.play()` explícito.
- **Loop visible corta a los 8s** → suavizar con cross-fade del propio clip (mejora pendiente).
- **`history.scrollRestoration='manual'` + `scrollTo(0,0)`** al cargar (evita abrir a mitad).
- **Fuente serif** (Playfair Display) incrustada `@font-face` (CSP bloquea CDN de fuentes).
- Entregable = **carpeta hosteable** (`index.html` + `assets/` con .mp4 + .woff2), no inline
  (los videos pesan; no caben como data-URI en un artefacto).

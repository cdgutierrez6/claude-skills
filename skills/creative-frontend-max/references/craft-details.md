# Craft details — las "cositas" que delatan a un senior

**Stack asumido:** Next.js 14.2 App Router · React 18.3 · TS · GSAP + `@gsap/react` · Lenis ·
framer-motion 11 · R3F v8 / drei v9 (**nunca** v9/v10 de drei/R3F: exigen React 19) ·
CSP estricta (cero CDN) · CWV: LCP<2.5s, INP<200ms, CLS<0.1 · `prefers-reduced-motion` · Android
de gama media · presupuesto $0.

Este documento no trae "efectos". Trae **detalles**. La diferencia:

- Un **efecto** se ve. Se comenta. A veces se odia.
- Un **detalle** no se ve: **se siente**. Nadie dice "qué bonita tu `:focus-visible`". Pero su
  ausencia hace que la página se sienta barata, y el visitante no sabe explicar por qué.

**El principio:** el slop de IA falla justo aquí. Un LLM te da el hero con gradiente y las tres
tarjetas. Casi nunca te da la scrollbar que no salta, el botón que sabe que está cargando, el 500
que suena a persona, ni el grano que le quita el plástico al gradiente. El craft vive en el 5% que
nadie te pide.

---

## GATE — Antes de añadir CUALQUIER detalle de este archivo

Cada ítem de abajo trae **coste** y **fallback**. Son obligatorios, no adorno del documento.
No añadas un detalle si no puedes contestar:

1. **¿Qué cuesta?** KB, ms de frame, capa compositada, dependencia, riesgo de CLS/INP.
2. **¿Cuál es el fallback?** Qué pasa si: no hay JS · no hay WebGL · `prefers-reduced-motion` ·
   Android gama media · lector de pantalla · navegador viejo.
3. **¿Sobra?** Si el detalle no cambia cómo se *siente* la página, es peso muerto. Bórralo.

Y la regla que gobierna todas: **ningún detalle puede retrasar el LCP ni robar INP.** El craft que
degrada Core Web Vitals no es craft, es vanidad.

---

## 1. Grano / noise — por qué lo digital se siente material

### Por qué funciona (no es nostalgia)

Tres razones técnicas, no estéticas:

1. **Mata el banding.** Un gradiente en 8 bits por canal sobre un fondo oscuro produce escalones
   visibles (bandas). El grano es **dithering**: rompe el escalón con ruido de alta frecuencia y
   el ojo integra la transición como continua. Esto es literalmente lo que hace el cine.
2. **Da materialidad.** Una superficie perfectamente lisa lee como *render*. El grano introduce
   una micro-irregularidad que el cerebro asocia con **materia** (película, papel, sensor). Es la
   misma razón por la que el diseño 2026 anti-flat vuelve a la textura.
3. **Unifica.** Una capa de grano sobre TODA la página (texto + canvas + imágenes) las mete en el
   mismo "material fotográfico". Sin grano, el canvas 3D flota encima del HTML como un sticker.

**Dosis:** `opacity: 0.03–0.06`. Por encima de 0.08 es suciedad, no textura. Si se ve el grano,
te pasaste; solo debe **notarse su ausencia** al quitarlo (prueba: toggle y compara).

### Opción A — SVG `feTurbulence` en data URI (lo que ya está en `globals.css`)

```css
/* Ya existe en portafolio-frontend: src/app/globals.css (.bg-grain) */
.bg-grain {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;              /* NUNCA olvidar: si no, come todos los clicks */
  opacity: 0.055;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```

**Los cuatro detalles que casi todo el mundo omite aquí:**

- `stitchTiles='stitch'` — sin esto, el tile de 220×220 muestra **costuras** visibles al repetirse.
- `width`/`height` **fijos** en el `<svg>` — sin ellos, Safari rasteriza el turbulence al tamaño
  del elemento (pantalla completa) → un raster gigante en cada resize. Con tile fijo, se rasteriza
  una vez y se repite.
- `pointer-events: none` — obvio hasta que te comes 40 minutos de debug.
- CSP: exige `img-src 'self' data:`. **Ya está** en `next.config.mjs` (`img-src 'self' data: blob: https:`).
  Si un día se endurece a `img-src 'self'`, esta capa muere en silencio (no lanza error, solo no
  pinta). Deja un comentario en el CSP.

**Coste:** ~1.4 KB inline, 0 JS, 0 requests. Pero `mix-blend-mode: overlay` en una capa `fixed`
a pantalla completa **fuerza al compositor a mezclar todo el stacking context debajo en cada
frame compositado**. En una laptop es gratis; en un Android de gama media con un canvas WebGL
debajo, es medible. **Mídelo, no lo asumas**: DevTools → Rendering → *Paint flashing* + *Layer
borders*, y compara el frame time con la capa activada/desactivada.

**Fallbacks (en orden de degradación):**
```css
/* 1) Móvil / gama baja: sin blend mode. Se ve casi igual y cuesta la mitad. */
@media (max-width: 768px), (pointer: coarse) {
  .bg-grain { mix-blend-mode: normal; opacity: 0.04; }
}
/* 2) Si el frame time sigue sufriendo: el grano solo donde hay gradiente (el hero), no fixed. */
.hero { position: relative; }
.hero::after { content: ""; position: absolute; inset: 0; pointer-events: none;
               opacity: .05; background-image: url("data:image/svg+xml,..."); }
/* 3) Ahorro de datos / reduced motion: el grano ESTÁTICO se queda (no es movimiento).
      Solo el grano ANIMADO respeta reduced-motion. */
```

### Opción B — Grano animado (el que "respira")

El grano estático se lee como una textura pegada. El grano **animado** (cambia cada frame) es el
que se siente film. La forma barata: desplazar el tile en `steps()` — pero **jamás** con `left/top`.

```css
@media (prefers-reduced-motion: no-preference) {
  .bg-grain { animation: grain-shift 0.6s steps(6) infinite; will-change: transform; }
}
@keyframes grain-shift {
  0%   { transform: translate3d(0,0,0); }
  16%  { transform: translate3d(-4%, -2%, 0); }
  33%  { transform: translate3d(2%, -5%, 0); }
  50%  { transform: translate3d(-3%, 4%, 0); }
  66%  { transform: translate3d(5%, 1%, 0); }
  83%  { transform: translate3d(-2%, -3%, 0); }
  100% { transform: translate3d(0,0,0); }
}
/* La capa debe ser MÁS GRANDE que el viewport o el translate deja bordes vacíos: */
.bg-grain { inset: -8%; }
```

**Coste:** solo `transform` → corre en el compositor, 0 repaints, 0 layout. Es el grano animado más
barato que existe. Pero sigue arrastrando el coste del `mix-blend-mode`.
**Fallback:** envuelto en `prefers-reduced-motion: no-preference` → con reduced-motion queda
estático, que sigue siendo correcto (el grano no es "movimiento" que maree, la animación sí).

### Opción C — Grano en el shader (el bueno, si YA tienes EffectComposer)

Si el proyecto **ya** monta `EffectComposer` (por Bloom, por ejemplo), el grano es prácticamente
gratis: va dentro de un pass que ya se está pagando, se aplica **antes** del tone mapping y afecta
al canvas y no al DOM (más correcto físicamente, y sin `mix-blend-mode`).

**Primero, la respuesta honesta:** `postprocessing` **ya trae un `<Noise />`**. Úsalo antes de
escribir GLSL:

```tsx
import { EffectComposer, Bloom, Noise } from "@react-three/postprocessing";
import { BlendFunction } from "postprocessing";

<EffectComposer disableNormalPass multisampling={0}>
  <Bloom intensity={0.6} luminanceThreshold={0.8} mipmapBlur />
  <Noise premultiply blendFunction={BlendFunction.SOFT_LIGHT} opacity={0.35} />
</EffectComposer>
```

Custom **solo** si necesitas algo que `<Noise />` no hace — p.ej. modular el grano por luminancia
(grano fuerte en medios tonos, cero en negros puros y en highlights: así se comporta la película
real, y es lo que evita que los negros se vean "sucios"):

```tsx
// src/components/three/GrainEffect.tsx
import { Effect } from "postprocessing";
import { Uniform } from "three";
import { forwardRef, useMemo } from "react";
import { wrapEffect } from "@react-three/postprocessing";

const frag = /* glsl */ `
  uniform float uAmount;
  uniform float uTime;

  // hash barato: sin textura de ruido, sin fetch, sin CDN. CSP-safe por construcción.
  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
  }

  void mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor) {
    // gl_FragCoord → el grano vive en el espacio de PANTALLA (no se estira con el objeto).
    float g = hash(gl_FragCoord.xy + vec2(uTime * 91.7, uTime * 47.3));

    float lum  = dot(inputColor.rgb, vec3(0.299, 0.587, 0.114));
    // 0 en negro puro y blanco puro, 1 en medios tonos → como la película real.
    float mask = 1.0 - abs(lum * 2.0 - 1.0);

    outputColor = vec4(inputColor.rgb + (g - 0.5) * uAmount * mask, inputColor.a);
  }
`;

class GrainImpl extends Effect {
  constructor({ amount = 0.07 } = {}) {
    super("Grain", frag, {
      uniforms: new Map<string, Uniform>([
        ["uAmount", new Uniform(amount)],
        ["uTime", new Uniform(0)],
      ]),
    });
  }
  update(_r: unknown, _i: unknown, dt: number) {
    const u = this.uniforms.get("uTime");
    if (u) u.value += dt;                      // dt, no elapsedTime: no explota tras 10 min
  }
}

const GrainRaw = wrapEffect(GrainImpl);

export const Grain = forwardRef<GrainImpl, { amount?: number }>(function Grain(props, ref) {
  const amount = props.amount ?? 0.07;
  return <GrainRaw ref={ref as never} amount={amount} />;
});
```

**Coste real y honesto:** si **NO** tienes ya `EffectComposer`, montarlo **solo por el grano es
mal negocio**: añade un render target a resolución completa, un pass extra, y **desactiva el MSAA
nativo** del canvas (los bordes de la laptop se ven aliased salvo que pagues `multisampling`, que
cuesta más todavía). En ese caso: **quédate con el CSS (Opción A/B)**. El shader gana solo cuando
el composer ya está encendido.

**Veredicto para portafolio-frontend hoy:** CSS (A + B). El canvas es de fondo, con `<Bloom>` no
encendido. Si mañana entra Bloom en el showcase, mueve el grano al composer y **quita** la capa CSS
(dos granos superpuestos = ruido, literalmente).

---

## 2. Preloader — y la regla dura que casi nadie respeta

### La regla dura (léela dos veces)

> **El preloader NUNCA retrasa el contenido. Es una CORTINA sobre contenido que YA se renderizó.**
> Si el hero se monta *después* de que el preloader termina, acabas de destruir tu LCP con tus
> propias manos.

Traducido a código: **prohibido** esto:

```tsx
// ❌ ASESINATO DE LCP. El h1 no existe en el DOM hasta 1.6s.
{loading ? <Preloader /> : <Hero />}
```

Y **obligatorio** esto (que es lo que ya hace el proyecto):

```tsx
// ✅ El Hero se renderiza en SSR, se hidrata, cuenta para LCP. El preloader solo lo TAPA.
<>
  <Preloader />     {/* position: fixed; inset: 0; z-index: 9999 — encima */}
  <Hero />          {/* debajo, ya pintado */}
</>
```

**El matiz que casi nadie sabe:** un overlay opaco encima **no impide** que Chrome registre el
elemento de abajo como candidato a LCP (el elemento *se pintó*; que esté ocluido por otra capa no
lo descalifica). Lo que SÍ lo destruye es no renderizarlo. Segundo matiz: **el contador gigante del
preloader es un nodo de texto grande y puede convertirse él mismo en el candidato LCP.** No es
grave — se pinta a los ~100 ms, así que tu LCP saldría *mejor*, no peor — pero si ves un LCP
sospechosamente bueno, ya sabes quién es. Verifica con Lighthouse el elemento LCP reportado.

### Techo duro + `Promise.race` (nunca esperes al `.glb`)

El pecado clásico: "espero a que carguen los assets". Tu `.glb` puede tardar 4s en una 3G de
Manizales. El visitante ya se fue.

```tsx
// Espera "lo razonable", pero con techo duro. Lo que no llegó, llega después: el canvas
// tiene su propio <Suspense> y aparece cuando aparezca. El HTML no lo necesita.
useEffect(() => {
  const HARD_CAP_MS = 1600;

  const ready = Promise.all([
    document.fonts.ready,                                    // sin esto, FOUT justo al abrir la cortina
    new Promise<void>((r) => {
      if (document.readyState === "complete") return r();
      window.addEventListener("load", () => r(), { once: true });
    }),
  ]);

  const cap = new Promise<void>((r) => setTimeout(r, HARD_CAP_MS));

  let cancelled = false;
  Promise.race([ready, cap]).then(() => { if (!cancelled) openCurtain(); });
  return () => { cancelled = true; };
}, []);
```

`document.fonts.ready` es el detalle senior: abrir la cortina y ver el titular **cambiar de fuente**
medio segundo después arruina el momento entero (y es CLS si las métricas difieren).

### La regla del retorno: no repitas el ritual

Un preloader que aparece en **cada** navegación pasa de "cine" a "peaje". Cóbralo una vez por sesión.

```ts
// intro-state.ts (ampliando el que ya existe)
const KEY = "intro:v1";     // versiona la clave: si rediseñas la intro, bump → v2

export function shouldPlayIntro(): boolean {
  if (typeof window === "undefined") return false;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return false;
  try {
    if (sessionStorage.getItem(KEY) === "seen") return false;
    sessionStorage.setItem(KEY, "seen");
    return true;
  } catch {
    return true;                       // Safari privado tira → mejor la intro que un crash
  }
}
```

`sessionStorage`, **no** `localStorage`: quieres que el recruiter que vuelve mañana vea el momento
otra vez; no quieres que lo vea 6 veces mientras navega hoy. (Gotcha conocido: `localStorage`
sobrevive a demasiadas cosas — el mismo error que ya se pagó con el prompt de instalación de PWA.)

### Las tres formas que NO son un spinner

**a) Contador + cortina** — ya implementado (`Preloader.tsx`). Detalles que lo hacen bueno:
`fontVariantNumeric: "tabular-nums"` (sin esto el número **baila** al cambiar de ancho: 011 → 088),
el ease `power2.inOut` en el contador (no lineal: un contador lineal se siente como una barra de
progreso de Windows), `stagger: 0.06` entre las dos mitades (la asimetría es lo que lo hace parecer
diseñado y no un `transform` simétrico de plantilla), y `height: 50.5%` (el 0.5% extra tapa la
costura subpíxel entre las mitades — **ese** es el detalle que separa a un senior).

**b) El logo que se dibuja** (SVG, cero JS de animación):

```tsx
// El path se "escribe" solo. pathLength="1" normaliza el largo → no tienes que medir el path.
<svg viewBox="0 0 120 40" className="intro-logo" aria-hidden="true">
  <path
    pathLength={1}
    d="M4 34 L20 6 L36 34 M44 6 v28 M44 6 h20 a8 8 0 0 1 0 16 h-20"
    fill="none" stroke="currentColor" strokeWidth={2}
    strokeLinecap="round" strokeLinejoin="round"
  />
</svg>
```
```css
.intro-logo path {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: draw 1.1s cubic-bezier(.65,0,.35,1) forwards;
}
@keyframes draw { to { stroke-dashoffset: 0; } }

@media (prefers-reduced-motion: reduce) {
  .intro-logo path { animation: none; stroke-dashoffset: 0; }   /* aparece dibujado, ya */
}
```
`pathLength={1}` es el truco: normaliza cualquier path a longitud 1, así el `dasharray/dashoffset`
funcionan sin JS y sin `getTotalLength()`. **Coste: 0 JS, 0 KB extra.**

**c) La máscara que se abre** — un `clip-path` que crece desde el centro. Más caro de lo que parece:
animar `clip-path` **no** siempre va al compositor (depende de la forma); un `inset()` sí, un
`polygon()` con muchos vértices no. Prefiere dos divs con `scaleY` (lo que ya haces) o
`clip-path: inset()`.

**Coste del preloader:** ~2 KB de JS, +1.15s de "no puedes hacer nada" (mitigado: el scroll se
bloquea, así que no scrolleas a ciegas), riesgo real de **fuga de visitantes** si se pasa de ~2s.
**Fallbacks:** `prefers-reduced-motion` → skip total (ya implementado). Sin JS → el preloader nunca
se monta y ves la página directamente (**correcto**: el fallback de "no JS" debe ser la página, no
una pantalla negra). Bot/Lighthouse → como el HTML ya está en SSR, no le afecta.

**Regla anti-tiro-en-el-pie:** si el preloader falla (excepción en el `useEffect`), la cortina se
queda puesta y tu portafolio es una pantalla negra. Blindaje: `try/catch` alrededor del timeline y
un `setTimeout(() => setGone(true), 3000)` **incondicional** como fusible. Nunca dejes que el
adorno pueda tumbar el contenido.

---

## 3. Transiciones de página — View Transitions + fallback determinista

### Antes del código: ¿tu sitio siquiera las necesita?

Un portafolio **one-page** con anclas **no tiene navegación de página**. La View Transitions API te
sirve aquí solo para dos cosas reales:

1. **Cambio de idioma** `/es` ↔ `/en` (rutas `[locale]` — existen en el proyecto).
2. **Detalle de proyecto** si algún día `/proyectos/[slug]` existe (y ahí el premio gordo es la
   **transición compartida**: la card de la grilla *se convierte* en el hero del detalle).

Si no tienes ninguna de las dos, **no implementes esto**. Es la respuesta honesta.

### Base CSS (funciona sola, sin JS, en navegadores que la soportan)

```css
@view-transition { navigation: auto; }   /* MPA. En Next App Router (SPA) hace falta el JS de abajo. */

::view-transition-old(root) { animation: vt-out 220ms cubic-bezier(.4,0,1,1) both; }
::view-transition-new(root) { animation: vt-in  320ms cubic-bezier(0,0,.2,1) both; }

@keyframes vt-out { to   { opacity: 0; transform: translateY(-8px) scale(.995); } }
@keyframes vt-in  { from { opacity: 0; transform: translateY(10px)  scale(1.005); } }

/* Transición COMPARTIDA: el mismo nombre en las dos rutas → el navegador interpola. */
.project-card-media  { view-transition-name: var(--vt-name); }   /* grilla */
.project-hero-media  { view-transition-name: var(--vt-name); }   /* detalle */
/* --vt-name: p-fleetvision  ← único por proyecto; DOS elementos con el mismo nombre a la vez
   en el MISMO snapshot = la transición se aborta entera y sin avisar. */

@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(root), ::view-transition-new(root) { animation: none; }
}
```

**EL GOTCHA QUE TE VA A MORDER (y que ninguna guía menciona):** tienes un `<canvas>` R3F **fixed a
pantalla completa**. Durante una view transition, el navegador toma un **snapshot** del viejo y del
nuevo → tu canvas WebGL animado aparece **congelado** en el snapshot y luego **salta** al frame
vivo. Se ve como un glitch feo. Fix: dale al canvas su **propio** `view-transition-name` para que
el navegador lo trate como un elemento persistente (se transforma, no se le hace cross-fade con el
resto):

```css
.r3f-canvas-root { view-transition-name: scene; }
::view-transition-group(scene) { animation: none; }             /* que ni se mueva */
::view-transition-old(scene), ::view-transition-new(scene) { animation: none; mix-blend-mode: normal; }
```
Aun así el snapshot congela un frame. Si sigue viéndose mal, la respuesta correcta es **pausar el
render loop** durante la transición (`useFrame` con un flag global; el store mutable que ya tienes
es el sitio perfecto) — el usuario no nota 300ms de escena quieta, pero sí nota un salto.

### El JS (Next App Router, SIN añadir dependencias)

```tsx
// src/hooks/useViewTransitionRouter.ts
"use client";
import { useRouter } from "next/navigation";
import { useCallback } from "react";

type DocWithVT = Document & {
  startViewTransition?: (cb: () => void | Promise<void>) => { finished: Promise<void> };
};

export function useViewTransitionRouter() {
  const router = useRouter();

  return useCallback((href: string) => {
    const doc = document as DocWithVT;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Firefox (hoy) y reduced-motion → navegación normal. Sin drama, sin polyfill.
    if (reduce || typeof doc.startViewTransition !== "function") {
      router.push(href);
      return;
    }

    doc.startViewTransition(() => {
      router.push(href);
      // App Router: router.push() NO devuelve una promesa que resuelva en el commit.
      // Dos rAF ≈ "React ya pintó". Es una HEURÍSTICA, no una garantía.
      return new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
      );
    });
  }, [router]);
}
```

**Sé honesto sobre esto:** el doble `requestAnimationFrame` es un **hack**, exactamente el mismo que
usa `next-view-transitions` por debajo (con más plomería). Si el payload RSC no está en caché, el
`push` tarda más que los dos frames y verás **flash de contenido viejo**. Mitigación obligatoria:
`<Link prefetch>` (default en producción) y/o prefetch en `onPointerEnter` — para cuando el usuario
suelta el click, la ruta ya está en memoria.

**Si necesitas determinismo (una demo para un cliente, un video), NO uses esto.** Usa la cortina:

```tsx
// Fallback determinista: TÚ controlas el timing. Nunca hay flash.
const transitionTo = useCallback((href: string) => {
  const el = curtainRef.current;
  if (!el) return router.push(href);

  gsap.timeline()
    .set(el, { transformOrigin: "50% 100%", scaleY: 0, display: "block" })
    .to(el, { scaleY: 1, duration: 0.42, ease: "power4.in" })
    .call(() => router.push(href))                        // navegas con la pantalla TAPADA
    .to(el, { scaleY: 0, transformOrigin: "50% 0%", duration: 0.55,
              ease: "power4.out", delay: 0.12 })          // el delay cubre el fetch RSC
    .set(el, { display: "none" });
}, [router]);
```

**Coste:** VT API = 0 KB, 0 deps, soporte Chrome/Edge/Safari 18+ (Firefox aún no → degrada a
navegación normal, que **es** un fallback aceptable). Cortina GSAP = ~0 KB extra (GSAP ya está),
funciona en todos lados, pero el `delay: 0.12` es un número **inventado**: si el fetch tarda más,
se ve el contenido viejo un instante. La solución robusta es escuchar el montaje de la nueva ruta
(un `useEffect` en el layout que dispara "revelar"), no un delay.

---

## 4. Scrollbar y `:focus-visible` — accesibilidad como craft, no como parche

### Scrollbar

```css
/* Estándar (Firefox + Chrome 121+). thin ≈ 8px, no lo puedes cambiar: es el precio del estándar. */
html {
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary) var(--color-bg);   /* thumb  track */
  scrollbar-gutter: stable;      /* ← EL DETALLE QUE VALE ORO. Ver abajo. */
}

/* WebKit: control fino. Es "no estándar" pero lo soporta Chrome/Safari/Edge. */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }     /* track invisible = menos ruido visual */
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
  border-radius: 999px;
  border: 2px solid var(--color-bg);   /* el "padding" del thumb: el truco es un borde del color del fondo */
  background-clip: padding-box;        /* sin esto, el gradiente se pinta DEBAJO del borde */
}
::-webkit-scrollbar-thumb:hover { filter: brightness(1.25); }
```

**`scrollbar-gutter: stable` es el ítem de mayor ROI de esta sección.** Cuando abres un modal y haces
`body { overflow: hidden }`, la scrollbar desaparece → el contenido **salta ~8-15px a la derecha** →
eso es CLS y se ve barato. `scrollbar-gutter: stable` reserva el carril siempre. **Una línea, CLS 0.**
(Alternativa clásica: compensar con `padding-right: calc(100vw - 100%)`. Peor: falla con `100vw` y
zoom.)

**Gotcha con Lenis:** Lenis hace **scroll real** del documento (no un transform de un wrapper), así
que la scrollbar nativa existe y todo esto aplica. Si algún día alguien lo migra a modo `wrapper`,
la scrollbar del `<html>` desaparece y estos estilos dejan de tener efecto — y habrá que pintar una
barra propia. Anótalo.

**Coste:** ~15 líneas CSS, 0 JS. **Fallback:** un navegador sin soporte muestra la scrollbar nativa.
Nadie muere. **Prohibido:** `::-webkit-scrollbar { display: none }` — esconder la scrollbar es
esconderle al usuario cuánto contenido queda. Es hostil, y en desktop rompe el arrastre.

### `:focus-visible` — el foco que se ve *diseñado*

Un `outline: none` sin reemplazo es una **falla WCAG 2.2 (2.4.7 / 2.4.11)** y, peor, es la señal
más clara de que el que hizo la página no navega con teclado. Un foco *diseñado* dice lo contrario.

```css
/* 1) Un solo token de foco para TODO el sitio. Consistencia = craft. */
:root {
  --focus-ring: 0 0 0 2px var(--color-bg), 0 0 0 4px var(--color-primary);
}

/* 2) Quita el outline del navegador SOLO cuando pones el tuyo. Nunca antes. */
:where(a, button, input, textarea, select, summary, [tabindex]):focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);           /* doble anillo: respira sobre cualquier fondo */
  border-radius: inherit;                  /* el anillo copia la forma del componente */
  transition: box-shadow 120ms ease-out;
}

/* 3) El foco del ratón NO se muestra (eso es :focus-visible), pero el de teclado SIEMPRE. */
:where(a, button):focus:not(:focus-visible) { outline: none; box-shadow: none; }

/* 4) Fallback para navegadores sin :focus-visible (muy viejos): mejor un foco de más que ninguno. */
@supports not selector(:focus-visible) {
  :where(a, button, input, textarea, select):focus { box-shadow: var(--focus-ring); }
}

/* 5) Alto contraste forzado (Windows): el box-shadow DESAPARECE en forced-colors.
      Sin esto, el usuario de alto contraste se queda SIN foco. Casi nadie sabe esto. */
@media (forced-colors: active) {
  :where(a, button, input, textarea, select, [tabindex]):focus-visible {
    outline: 3px solid Highlight;
    outline-offset: 2px;
  }
}
```

**El detalle que delata al senior de verdad: el foco vs. el botón magnético.**
Si tu botón se mueve con el cursor (magnetismo), el anillo de foco se va con él y, si el usuario
llegó con **Tab**, verás el anillo desplazado o el botón "huyendo". Fix: el magnetismo se **apaga**
mientras ese botón tiene foco de teclado.

```tsx
const onPointerMove = (e: React.PointerEvent<HTMLButtonElement>) => {
  const el = e.currentTarget;
  // Si llegó por teclado, NO lo muevas: el anillo de foco debe quedarse donde el ojo lo dejó.
  if (el.matches(":focus-visible")) return;
  if (window.matchMedia("(pointer: coarse)").matches) return;   // en touch el magnetismo no existe
  const r = el.getBoundingClientRect();
  const x = (e.clientX - (r.left + r.width / 2)) * 0.25;
  const y = (e.clientY - (r.top + r.height / 2)) * 0.35;
  el.style.setProperty("--mx", `${x}px`);      // CSS var, no re-render de React
  el.style.setProperty("--my", `${y}px`);
};
```

Y el **skip link**, que cuesta 8 líneas y ningún portafolio de IA lo trae:

```tsx
<a href="#main" className="skip-link">Saltar al contenido</a>
...
<main id="main" tabIndex={-1}>…</main>
```
```css
.skip-link {
  position: fixed; top: 0; left: 50%; translate: -50% -120%;
  z-index: 10000; padding: .75rem 1.25rem; border-radius: 0 0 .75rem .75rem;
  background: var(--color-primary); color: #050505; font-weight: 700;
  transition: translate 180ms cubic-bezier(0,0,.2,1);
}
.skip-link:focus-visible { translate: -50% 0; }    /* baja del techo. Es un detalle bonito, no un parche. */
```

**Coste: ~0.** **Impacto: es la diferencia entre "sabe hacer páginas" y "sabe hacer producto".**

---

## 5. Microinteracciones

### 5.1 Botón con máquina de estados (idle → hover → press → loading → success | error)

Un botón que se queda igual después de que lo aprietas es un botón roto. El feedback lo da el
**estado**, no la animación.

```tsx
// src/components/ui/StatefulButton.tsx
"use client";
import { useState, useRef, useEffect } from "react";

type S = "idle" | "loading" | "success" | "error";

export function StatefulButton({ action, children }: { action: () => Promise<void>; children: React.ReactNode }) {
  const [s, setS] = useState<S>("idle");
  const t = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => () => clearTimeout(t.current), []);   // no setState tras unmount

  async function run() {
    if (s === "loading") return;                        // doble-click: ignorado, no encolado
    setS("loading");
    try {
      await action();
      setS("success");
      t.current = setTimeout(() => setS("idle"), 2200); // el éxito CADUCA y vuelve a idle
    } catch {
      setS("error");
      t.current = setTimeout(() => setS("idle"), 3200); // el error dura MÁS: hay que leerlo
    }
  }

  return (
    <button
      data-state={s}
      onClick={run}
      disabled={s === "loading"}
      aria-busy={s === "loading"}
      className="btn"
      // El ancho se FIJA para que el cambio de label no reflowee la fila. CLS = 0.
      style={{ minInlineSize: "12ch" }}
    >
      <span className="btn__label">
        {s === "loading" ? "Enviando…" : s === "success" ? "Enviado ✓" : s === "error" ? "Reintentar" : children}
      </span>
      {/* aria-live fuera del label: el lector anuncia el cambio sin releer todo el botón */}
      <span aria-live="polite" className="sr-only">
        {s === "success" ? "Mensaje enviado" : s === "error" ? "No se pudo enviar" : ""}
      </span>
    </button>
  );
}
```

```css
.btn {
  position: relative; isolation: isolate;
  transform: translate3d(var(--mx, 0), var(--my, 0), 0);       /* el magnetismo entra por aquí */
  /* ASIMETRÍA: entra rápido, sale lento. Es lo que hace que se sienta "físico". */
  transition: transform 160ms cubic-bezier(.2,.8,.2,1), background-color 200ms ease;
}
.btn:hover  { --lift: -2px; }
.btn:active { transition-duration: 70ms; scale: .97; }         /* el press debe ser INMEDIATO */

/* Nunca animes box-shadow (repaint). Anima la OPACIDAD de una capa de sombra. */
.btn::after {
  content: ""; position: absolute; inset: 0; z-index: -1; border-radius: inherit;
  box-shadow: 0 10px 30px -8px var(--color-primary);
  opacity: 0; transition: opacity 220ms ease;
}
.btn:hover::after { opacity: .55; }

.btn[data-state="loading"] { cursor: progress; opacity: .8; }
.btn[data-state="success"] { background: var(--color-success); }
.btn[data-state="error"]   { background: var(--color-danger); animation: shake 320ms; }

@keyframes shake {
  0%,100% { translate: 0 } 20% { translate: -5px } 40% { translate: 5px }
  60% { translate: -3px } 80% { translate: 3px }
}
@media (prefers-reduced-motion: reduce) {
  .btn, .btn::after { transition: none; }
  .btn[data-state="error"] { animation: none; }     /* el color rojo ya comunica; el shake sobra */
}
```

Detalles que importan: **el ancho fijo** (`min-inline-size: 12ch`) para que "Enviar" → "Enviando…"
no empuje el layout; **el éxito caduca** (un botón que se queda en "✓ Enviado" para siempre es un
botón muerto); **`aria-busy`** y un `aria-live` **corto** (no anuncies el botón entero).
**Coste:** ~1 KB. **Fallback:** sin JS el `<form>` hace submit nativo y la API responde (tu
`/api/contact` es un route handler: **haz que funcione también con `application/x-www-form-urlencoded`**
y ya tienes progressive enhancement de verdad).

### 5.2 Copy-to-clipboard con feedback (y con el fallback que todos olvidan)

```tsx
"use client";
import { useState, useRef, useEffect } from "react";

export function CopyButton({ value, label = "Copiar" }: { value: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  const t = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => () => clearTimeout(t.current), []);

  async function copy() {
    try {
      // navigator.clipboard NO existe en contexto inseguro (http://IP-de-la-LAN, que es como
      // pruebas en el celular). Sin fallback, tu botón "no hace nada" y no sabes por qué.
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
      } else {
        const ta = document.createElement("textarea");
        ta.value = value;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";                 // fuera de pantalla pero enfocable
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");           // deprecado, pero es el ÚNICO camino en http://
        ta.remove();
      }
      setCopied(true);
      t.current = setTimeout(() => setCopied(false), 1800);
    } catch {
      // Último recurso honesto: no finjas que copiaste. Muestra el valor para copiar a mano.
      window.prompt("Copia esto:", value);
    }
  }

  return (
    <button onClick={copy} className="copy" data-copied={copied || undefined}>
      <span className="copy__text">{copied ? "Copiado" : label}</span>
      <span aria-live="polite" className="sr-only">{copied ? `${value} copiado al portapapeles` : ""}</span>
    </button>
  );
}
```
```css
/* El feedback NO es solo texto: es un flash. 180ms de un color que se apaga. */
.copy[data-copied] { color: var(--color-success); }
.copy[data-copied]::before {
  content: ""; position: absolute; inset: -4px; border-radius: 8px;
  background: var(--color-success); opacity: .18; animation: flash 600ms ease-out forwards;
}
@keyframes flash { to { opacity: 0; transform: scale(1.08); } }
```
**El `aria-live` es obligatorio**: sin él, un usuario de lector de pantalla aprieta el botón y **no
pasa nada** desde su punto de vista. Es el bug de accesibilidad #1 de los botones de copiar.
**Coste:** ~0.7 KB. **Fallback:** `execCommand` → `prompt()`. Nunca "silencio".

### 5.3 Tilt de tarjetas (y por qué en móvil NO)

```tsx
"use client";
import { useRef } from "react";

export function TiltCard({ children }: { children: React.ReactNode }) {
  const raf = useRef(0);

  const move = (e: React.PointerEvent<HTMLDivElement>) => {
    // pointer: coarse → NO hay hover. Un tilt en touch se dispara al TOCAR = se siente roto.
    if (window.matchMedia("(pointer: coarse)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const el = e.currentTarget;
    const { clientX, clientY } = e;
    cancelAnimationFrame(raf.current);
    raf.current = requestAnimationFrame(() => {          // 1 escritura por frame, no por evento
      const r = el.getBoundingClientRect();              // ojo: fuerza layout. Por eso va en rAF.
      const px = (clientX - r.left) / r.width  - 0.5;    // -0.5 … 0.5
      const py = (clientY - r.top)  / r.height - 0.5;
      el.style.setProperty("--rx", `${(-py * 7).toFixed(2)}deg`);   // 7°, no 20°. Sutil.
      el.style.setProperty("--ry", `${( px * 9).toFixed(2)}deg`);
      el.style.setProperty("--gx", `${(px + 0.5) * 100}%`);         // para el brillo especular
      el.style.setProperty("--gy", `${(py + 0.5) * 100}%`);
    });
  };

  const leave = (e: React.PointerEvent<HTMLDivElement>) => {
    cancelAnimationFrame(raf.current);
    const el = e.currentTarget;
    el.style.setProperty("--rx", "0deg");
    el.style.setProperty("--ry", "0deg");
  };

  return (
    <div ref={undefined} className="tilt" onPointerMove={move} onPointerLeave={leave}>
      <div className="tilt__inner">{children}</div>
    </div>
  );
}
```
```css
.tilt { perspective: 900px; }        /* la perspectiva va en el PADRE, no en el que rota */
.tilt__inner {
  transform: rotateX(var(--rx, 0)) rotateY(var(--ry, 0));
  transition: transform 400ms cubic-bezier(.2,.8,.2,1);   /* el RETORNO es lento; el seguimiento, no */
  transform-style: preserve-3d;
  position: relative;
}
.tilt:hover .tilt__inner { transition-duration: 90ms; }    /* mientras sigues el cursor, casi sin lag */

/* El brillo especular: sin esto el tilt parece un div girando, no una superficie. */
.tilt__inner::after {
  content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none;
  background: radial-gradient(circle at var(--gx,50%) var(--gy,50%),
              rgba(255,255,255,.10), transparent 55%);
  opacity: 0; transition: opacity 250ms ease;
}
.tilt:hover .tilt__inner::after { opacity: 1; }

@media (prefers-reduced-motion: reduce), (pointer: coarse) {
  .tilt__inner { transform: none !important; transition: none; }
}
```
**Los tres pecados del tilt:** (1) ángulo de 15-20° → parece un juguete; **5-8° es lo que se ve
caro**; (2) sin el brillo especular no lee como superficie; (3) activarlo en touch. **Coste:** un
`getBoundingClientRect` por frame **solo mientras hay hover** — mídelo si tienes 12 tarjetas y todas
escuchan (usa **un** listener en el contenedor con delegación si son muchas).

### 5.4 Sonido — veredicto honesto: **NO**

Casi siempre **no**. Las razones no son de gusto:

1. **Política de autoplay**: no puedes sonar hasta que haya un gesto del usuario. Así que tu primer
   hover **no suena** y el segundo sí → se siente roto, no premium.
2. **Contexto**: tu portafolio se abre en una oficina, en una reunión, con audífonos ajenos puestos.
   Un sonido inesperado no es "premium", es **una agresión** y un `Cmd+W`.
3. **Peso y CSP**: audio = KB + un `AudioContext` + `media-src` en el CSP.
4. **Accesibilidad**: el sonido no puede ser el **único** canal de feedback (WCAG). Así que igual
   tienes que hacer el feedback visual → el sonido es 100% redundante.

**Cuándo SÍ:** solo con **toggle explícito, apagado por defecto, visible desde el primer scroll**, y
solo si la marca es de audio/juego/experiencia. Si lo haces:

```ts
// Un solo AudioContext, creado en el PRIMER gesto. Nunca antes (el navegador lo suspende).
let ctx: AudioContext | null = null;
export function initAudioOnGesture() {
  if (ctx) return;
  ctx = new AudioContext();
  if (ctx.state === "suspended") void ctx.resume();
}
// Los "sonidos" se SINTETIZAN: cero KB, cero fetch, cero problema de CSP.
export function tick(freq = 880, ms = 40) {
  if (!ctx || ctx.state !== "running") return;
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.frequency.value = freq; o.type = "sine";
  g.gain.setValueAtTime(0.0001, ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.06, ctx.currentTime + 0.005);
  g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + ms / 1000);
  o.connect(g).connect(ctx.destination);
  o.start(); o.stop(ctx.currentTime + ms / 1000 + 0.02);
}
```
Sintetizar con `OscillatorNode` en vez de servir `.mp3` es la única versión defendible: **0 KB, 0
requests, 0 CSP**. Pero el default sigue siendo `false`. **Coste de NO hacerlo: cero. Recomendación:
no lo hagas.**

---

## 6. Progreso de scroll e indicador de sección

### 6.1 Barra de progreso — hazla **sin JS**

Existe ya una barra JS. La versión 2026 es **scroll-driven animations** de CSS: corre en el
compositor, **no toca el hilo principal**, y sobrevive a cualquier jank de JS.

```css
.scroll-progress {
  position: fixed; inset-block-start: 0; inset-inline: 0;
  block-size: 2px; z-index: 100;
  transform-origin: 0 50%;
  transform: scaleX(0);                 /* el estado base = el fallback */
  background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
}

@supports (animation-timeline: scroll()) {
  .scroll-progress {
    animation: sp-grow linear both;
    animation-timeline: scroll(root block);    /* ← ni un byte de JS */
  }
}
@keyframes sp-grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }

@media (prefers-reduced-motion: reduce) { .scroll-progress { transition: none; } }
```

**Coste: 0 JS, 0 frames del main thread.** **Fallback:** Chrome/Edge 115+ y Safari 26+ lo tienen;
Firefox (hoy) no → el `@supports` deja la barra en `scaleX(0)`. Eso es **peor** que no tenerla.
Solución: fallback JS **solo** si no hay soporte, montado con el store mutable que ya existe:

```tsx
"use client";
import { useEffect, useRef } from "react";

export function ScrollProgress() {
  const bar = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (CSS.supports("animation-timeline: scroll()")) return;    // el CSS ya lo hace. Sal.

    let raf = 0;
    const tick = () => {
      const doc = document.documentElement;
      const max = doc.scrollHeight - doc.clientHeight;
      const p = max > 0 ? doc.scrollTop / max : 0;
      // Escritura de estilo directa. NUNCA setState: esto corre a 60-120 Hz.
      if (bar.current) bar.current.style.transform = `scaleX(${p})`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return <div ref={bar} className="scroll-progress" aria-hidden="true" />;
}
```
`aria-hidden="true"` **siempre**: la barra es decorativa. Un `role="progressbar"` aquí es ruido para
el lector de pantalla — el usuario ya sabe dónde está por la estructura de encabezados.

**El rAF loop permanente es un coste real** (mantiene despierto el main thread). Si prefieres, engánchalo
al callback de Lenis que **ya** escribe `scrollStore.page` — ese es el sitio natural. Cero loops nuevos.

### 6.2 Indicador de sección activa — `IntersectionObserver`, jamás un scroll listener

```tsx
"use client";
import { useEffect, useState } from "react";

export function useActiveSection(ids: string[]) {
  const [active, setActive] = useState(ids[0]);

  useEffect(() => {
    const els = ids
      .map((id) => document.getElementById(id))
      .filter((e): e is HTMLElement => !!e);

    const io = new IntersectionObserver(
      (entries) => {
        // La sección "activa" = la que cruza la LÍNEA MEDIA del viewport.
        // Ese rootMargin colapsa el viewport a una franja de 1px en el centro:
        // solo puede haber una ganadora → sin parpadeo entre dos secciones.
        const hit = entries.find((e) => e.isIntersecting);
        if (hit) setActive(hit.target.id);
      },
      { rootMargin: "-50% 0px -50% 0px", threshold: 0 }
    );

    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [ids]);

  return active;
}
```
```tsx
// El nav: aria-current es lo que hace que esto sea accesible, no la clase CSS.
<nav aria-label="Secciones">
  {ids.map((id) => (
    <a key={id} href={`#${id}`} aria-current={active === id ? "true" : undefined} className="nav-link">
      {labels[id]}
    </a>
  ))}
</nav>
```
```css
/* El "pill" que se desliza entre items: UN pseudo-elemento en el nav, movido con vars.
   Alternativa cara: un div por item con opacity. Alternativa correcta: FLIP con GSAP Flip. */
.nav-link { position: relative; }
.nav-link::after {
  content: ""; position: absolute; inset-inline: 0; inset-block-end: -6px; block-size: 2px;
  background: var(--color-primary);
  transform: scaleX(0); transform-origin: 0 50%;
  transition: transform 280ms cubic-bezier(.2,.8,.2,1);
}
.nav-link[aria-current="true"]::after,
.nav-link:hover::after { transform: scaleX(1); }
/* transform-origin invertido al salir = la línea se retira por donde entró. Detalle de 1 línea. */
.nav-link:not(:hover):not([aria-current="true"])::after { transform-origin: 100% 50%; }
```
**Coste:** un `IntersectionObserver` (barato, corre off-main-thread para el cálculo). **Nunca**
`scroll` + `getBoundingClientRect()` por sección: eso es N reflows por evento de scroll = el clásico
INP muerto.
**Fallback:** sin JS, el nav sigue siendo un `<a href="#id">` que **funciona** (con
`scroll-behavior: smooth` en CSS + `scroll-margin-top` en las secciones para que el navbar fijo no
tape el título — otro detalle de 1 línea que casi nadie pone):
```css
section[id] { scroll-margin-block-start: 6rem; }
```

---

## 7. Empty / error / loading — un 500 puede ser un momento de marca

### La regla dura de la página de error

> **La página de error NO puede depender de nada que pueda fallar.**
> Cero WebGL. Cero fuentes externas. Cero fetch. Cero librerías de animación.
> HTML + CSS inline + como mucho, un `<svg>`.

Es de sentido común y casi nadie lo aplica: si el usuario llegó al 500 porque el dispositivo se
quedó sin memoria o WebGL se cayó, montar tu canvas 3D en el error **lo vuelve a matar**. El error
elegante es **el más barato** de la página, no el más caro.

```tsx
// src/app/[locale]/error.tsx  — captura errores de render de esa ruta
"use client";
import { useEffect } from "react";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // Aquí va Sentry cuando haya DSN. Hoy, al menos, no lo tragues en silencio.
    console.error("[route error]", error.digest ?? error.message);
  }, [error]);

  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: "2rem", textAlign: "center" }}>
      <div style={{ maxWidth: "46ch" }}>
        {/* El "carácter" está en el COPY, no en un efecto. Y es lo que un LLM genérico no escribe. */}
        <p style={{ fontFamily: "var(--font-mono), monospace", opacity: .6, letterSpacing: ".08em" }}>
          ERROR 500 · unhandled_exception
        </p>
        <h1 style={{ fontSize: "clamp(2rem, 6vw, 3.5rem)", lineHeight: 1.05, margin: "1rem 0" }}>
          Algo se cayó de mi lado.
        </h1>
        <p style={{ opacity: .75, lineHeight: 1.6 }}>
          Llevo 13 años arreglando estas. Esta también. Mientras tanto, el resto del sitio funciona
          — o me escribes directo y lo hablamos.
        </p>
        {error.digest && (
          <p style={{ fontFamily: "var(--font-mono), monospace", fontSize: ".8rem", opacity: .45, marginTop: "1rem" }}>
            digest: {error.digest}
          </p>
        )}
        <div style={{ display: "flex", gap: ".75rem", justifyContent: "center", marginTop: "2rem", flexWrap: "wrap" }}>
          <button onClick={reset}>Reintentar</button>
          <a href="/">Volver al inicio</a>
          <a href="mailto:hola@ejemplo.com">Escribirme</a>   {/* SIEMPRE una salida humana */}
        </div>
      </div>
    </main>
  );
}
```

Notas: `error.digest` es el ID que Next asigna al error en el servidor — **mostrarlo** es lo que hace
que un reclutador técnico piense "este sabe operar producción". Y el `mailto:` es el detalle de
producto: **el visitante nunca se queda sin canal**.

Los otros dos archivos que faltan en el 95% de los portafolios:
- `src/app/[locale]/not-found.tsx` → el 404, con **enlaces a las secciones reales** (no un "Volver"
  solitario). Un 404 útil retiene; uno decorativo, no.
- `src/app/global-error.tsx` → el error del **layout raíz**. Debe traer sus propios `<html>` y
  `<body>`, y ser **HTML plano**. Es el último salvavidas.

### Loading — skeletons con la geometría final, no spinners

```tsx
// El skeleton debe tener EXACTAMENTE la caja del contenido real, o generas CLS al reemplazarlo.
export function ProjectCardSkeleton() {
  return (
    <div className="card" aria-hidden="true" style={{ blockSize: 320 }}>   {/* misma altura que la real */}
      <div className="sk" style={{ blockSize: 180, borderRadius: 12 }} />
      <div className="sk" style={{ blockSize: 20, inlineSize: "70%", marginBlockStart: 16 }} />
      <div className="sk" style={{ blockSize: 14, inlineSize: "90%", marginBlockStart: 10 }} />
    </div>
  );
}
```
```css
.sk {
  background: linear-gradient(90deg, #17171a 25%, #222227 50%, #17171a 75%);
  background-size: 200% 100%;
  animation: sk 1.3s ease-in-out infinite;
}
@keyframes sk { to { background-position: -200% 0; } }
/* El shimmer anima background-position = REPAINT. Con 12 skeletons es medible.
   Versión compositada: un ::after con transform: translateX(). Úsala si hay muchos. */
@media (prefers-reduced-motion: reduce) { .sk { animation: none; } }
```
**El spinner es un anti-patrón** cuando conoces la forma del contenido: no informa, no ubica y no
reserva espacio. Úsalo solo para esperas **indeterminadas y cortas** dentro de un botón.

### Empty states con carácter

Un empty state genérico ("No hay resultados") es una puerta cerrada. Uno bueno tiene **tres partes**:
qué pasó · por qué · **qué hacer ahora** (una acción, no un párrafo).

```tsx
<div className="empty">
  <h3>Nada bajo “{query}”.</h3>
  <p>Busqué en 14 proyectos, .NET, Node, React y agentes LLM. Ese término no aparece.</p>
  <div className="empty__actions">
    <button onClick={clear}>Ver todo</button>
    <span>o prueba: <button onClick={() => setQuery("microservicios")}>microservicios</button></span>
  </div>
</div>
```
**Coste de todo el bloque 7: ~0 KB de runtime, cero deps.** Es puro **copy + estructura**. Y es de
lo más alto en relación impacto/coste de todo este documento.

### El fallback de WebGL (que no es opcional)

```tsx
// Si el GPU es malo o WebGL no existe, NO renderices el canvas. Muestra un poster.
"use client";
import { Suspense, useMemo } from "react";

function hasWebGL() {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2") || c.getContext("webgl"));
  } catch { return false; }
}

export function Scene3DGate({ children, poster }: { children: React.ReactNode; poster: string }) {
  const ok = useMemo(() => {
    if (typeof window === "undefined") return false;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return false;  // ← también aquí
    if (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) return false; // heurística de gama baja
    return hasWebGL();
  }, []);

  if (!ok) {
    // Un PNG/WebP del mismo frame. Zero-cost, y la página SIGUE contando la misma historia.
    return <img src={poster} alt="" aria-hidden="true" className="scene-poster" loading="lazy" decoding="async" />;
  }
  return <Suspense fallback={null}>{children}</Suspense>;
}
```
`hardwareConcurrency <= 4` es una **heurística tosca** y lo sé: descarta algún teléfono decente. La
alternativa "correcta" (`useDetectGPU` de drei) descarga una lista de GPUs → **fetch externo → viola
la CSP**. Entre falso-negativo y CSP rota, elijo el falso-negativo. Es un trade-off consciente, no
un descuido. (`useDetectGPU` acepta una lista local si quieres afinar: pásale el JSON desde `/public`.)

---

## 8. Checklist ANTI-AI-SLOP (la definitiva)

Esto es un **gate binario**, no una guía. Si un solo ítem de la sección A está presente, la página
es slop y no se entrega.

### A. Muerte súbita — si aparece **uno**, se rehace

- [ ] Gradiente **morado→azul** (`#6366f1 → #a855f7`, `from-indigo-500 to-purple-600`, y primos).
- [ ] **Blob** morado/rosa difuminado flotando en el fondo (`blur-3xl`, `opacity-20`, `rounded-full`).
- [ ] **Glassmorphism por defecto** (`backdrop-blur` + `bg-white/10` + `border-white/20`) sin razón
      de diseño. Bonus de vergüenza: `backdrop-filter` en móvil = frame killer.
- [ ] **Inter / system-ui en todo**, un solo peso, sin jerarquía. (Y su primo: dos fuentes de Google
      que no conversan.)
- [ ] **Emojis como iconos** (🚀 ⚡ 🎯 ✨) en una página que se dice senior.
- [ ] **Badge pill** en el hero: `✨ Now available` / `🚀 v2.0 is here`.
- [ ] Copy de plantilla: *"Elevate your workflow"*, *"Crafting digital experiences"*, *"Where
      innovation meets design"*, *"Let's build something amazing together"*.
- [ ] **Tres tarjetas de features** equidistantes, mismo `rounded-xl`, misma sombra, icono arriba.
- [ ] `hover:scale-105` aplicado a **todo** lo que tiene borde.
- [ ] **Lorem ipsum**, `[Your Name]`, `project description here`, links a `#`, `example.com`.
- [ ] Partículas / estrellitas flotando **sin significado** (motion decorativo, no dirigido).
- [ ] Todo el texto **centrado** con `max-w-2xl mx-auto` de arriba a abajo.
- [ ] Espaciado **uniforme** entre todas las secciones (`py-24` × 6). El ritmo plano = sin dirección.
- [ ] `outline: none` sin `:focus-visible` de reemplazo.
- [ ] **Cero contenido real.** Un portafolio sin métricas, sin nombres de sistemas, sin números.

### B. La prueba de las cinco preguntas (todas deben pasar)

1. **Prueba del screenshot.** Tapa el nombre. ¿Podría ser el portafolio de otras 500 personas?
   → Si sí: no hay dirección de arte, hay un tema de Tailwind.
2. **Prueba de la frase.** ¿Un visitante podría describirle a un amigo, **con palabras**, un momento
   de esta página? ("Se abre una cortina y un laptop atraviesa el titular.")
   → Si no sale en una frase, **no hay momento**.
3. **Prueba del contenido.** Quítale TODOS los efectos, déjala en HTML negro sobre blanco.
   ¿Sigue siendo impresionante lo que dice? → Si no, estás maquillando un vacío. **El efecto no
   salva a un CV vacío; lo delata.**
4. **Prueba del outlier.** ¿Hay **una** decisión que ninguna plantilla tomaría? (Una tipografía rara
   y bien usada. Un color que asusta. Un layout que rompe la grilla en un punto exacto. Una sección
   que un template no tiene.) → Si todo es "seguro", es promedio. El promedio no gana nada.
5. **Prueba del Moto G.** Ábrela en un Android de gama media, con 4G. ¿60fps? ¿LCP<2.5s?
   → Si no: es bonita en tu monitor y basura en el mundo. **No cuenta.**

### C. Los detalles que un LLM genérico casi nunca escribe (si están, no es slop)

- [ ] `scrollbar-gutter: stable` (CLS del modal = 0).
- [ ] `:focus-visible` **diseñado** + `@media (forced-colors: active)` + skip-link.
- [ ] `font-variant-numeric: tabular-nums` en cualquier número que **cambia**.
- [ ] `scroll-margin-block-start` en las secciones con ancla (el navbar fijo no tapa el título).
- [ ] Ancho fijo (`min-inline-size`) en botones que **cambian de label** (Enviar → Enviando…).
- [ ] `aria-live` en copy-to-clipboard y en el resultado del formulario.
- [ ] Asimetría en las transiciones: **entrada rápida (~120-160ms), salida lenta (~250-400ms)**.
- [ ] Ángulo de tilt **5-8°**, no 20°.
- [ ] `error.tsx` + `not-found.tsx` + `global-error.tsx`, **sin WebGL, sin deps**, con `error.digest`
      y una salida humana (`mailto:`).
- [ ] Fallback de WebGL a un **poster**, y fallback del formulario a **submit nativo** sin JS.
- [ ] `prefers-reduced-motion` respetado **de verdad** (no un `transition: none` global que rompe
      la UI: se apaga el **movimiento**, no el **feedback de estado**).
- [ ] El preloader tiene **fusible**: si su timeline explota, la cortina se cae igual.
- [ ] Grano a `opacity` 0.03–0.06 con `stitchTiles` y `pointer-events: none`.
- [ ] El scroll no dispara **ni un** `setState` (store mutable + `useFrame`/rAF).

### D. Verificación (no se marca "hecho" sin correr esto)

```bash
# 1) Vitals reales, no vibras. Móvil, throttling ON.
npx unlighthouse --site http://localhost:3000    # o Lighthouse en DevTools, perfil "Mobile"

# 2) Reduced motion: fuerza la preferencia y RECORRE LA PÁGINA ENTERA.
#    DevTools → Rendering → Emulate CSS prefers-reduced-motion: reduce
#    Gate: nada se mueve Y todo sigue siendo usable (los estados de botón SIGUEN dando feedback).

# 3) Teclado puro: desconecta el mouse. Tab de arriba a abajo.
#    Gate: se ve SIEMPRE dónde estás, se puede llegar a TODO, y el skip-link aparece primero.

# 4) Sin JS. DevTools → Settings → Debugger → Disable JavaScript.
#    Gate: se lee el contenido, el nav ancla funciona, el formulario hace submit.

# 5) Frame time con el grano y el canvas encendidos, en throttling 4x/6x CPU.
#    DevTools → Performance → grabar 5s de scroll. Gate: sin frames >16.7ms sostenidos.
```

---

## Prioridad si solo tienes una tarde (impacto / coste)

| # | Detalle | Coste | Impacto |
|---|---|---|---|
| 1 | `:focus-visible` + skip-link + `forced-colors` | 20 líneas CSS | Altísimo (a11y + señal de senior) |
| 2 | `error.tsx` / `not-found.tsx` con copy propio | 1 hora, 0 KB | Altísimo (momento de marca) |
| 3 | `scrollbar-gutter: stable` + scrollbar diseñada | 15 líneas CSS | Alto (CLS 0, se siente cuidado) |
| 4 | Botón con máquina de estados + `tabular-nums` | ~1 KB | Alto (el sitio "responde") |
| 5 | Grano (ya está — solo ajusta dosis y el fallback móvil) | 0 | Medio-alto (mata el plástico) |
| 6 | Barra de progreso a `animation-timeline: scroll()` | 10 líneas | Medio (main thread libre) |
| 7 | Indicador de sección con IO + `aria-current` | ~30 líneas | Medio |
| 8 | Tilt de tarjetas (5-8°, solo `pointer: fine`) | ~40 líneas | Medio |
| 9 | View Transitions (solo si hay `[locale]` o detalle) | ~40 líneas | Bajo hoy |
| 10 | Sonido | — | **No lo hagas** |

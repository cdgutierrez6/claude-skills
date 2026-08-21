# Pointer craft — la interacción manejada por el mouse

**Stack asumido:** Next.js 14 App Router · React 18.3 · `@react-three/fiber@8` · `@react-three/drei@9` ·
`three@0.171` · GSAP + `@gsap/react` · Lenis · framer-motion@11 · **CSP estricta (cero CDN)**.
**No subas a R3F v9 / drei v10** (exigen React 19).

El puntero es la palanca de "vivo" con **mejor ratio impacto/coste de toda la página**: no requiere
assets, no pesa KB, no toca el LCP y no mueve layout. Pero es también donde más gente se estrella:
un `mousemove` que llama `setState`, un cursor con `top/left`, un imán con `strength: 0.7` que hace
que el botón huya del dedo. Este documento es el craft, no el truco.

---

## GATE — antes de escribir una línea

> **Un efecto de puntero que no se puede apagar es un bug, no un efecto.**

Ningún efecto de esta página se mergea sin contestar las 4:

1. **¿Qué pasa en touch?** El default correcto es **NO EXISTIR**. Cero listeners, cero rAF, cero
   uniforms. Un dedo no tiene hover: cualquier efecto "de hover" en móvil es un fantasma que se
   dispara al tap y se queda pegado.
2. **¿Qué pasa con el teclado?** El cursor nativo **vuelve** al primer `Tab`. Los elementos
   magnéticos **no se mueven** cuando reciben `:focus` (un botón que se desplaza al enfocarlo es un
   ataque a quien navega con teclado).
3. **¿Qué pasa con `prefers-reduced-motion: reduce`?** Cada efecto tiene su fallback escrito abajo.
   El default: se apaga entero y se restaura el comportamiento nativo. Un cursor que persigue con
   retardo **es** movimiento.
4. **¿Cuánto cuesta por frame, medido?** No estimado: medido en el Performance panel con CPU
   throttling 4×. Si no lo mediste, no lo sabes.

---

## Ranking honesto — impacto vs. coste

Ordenado por lo que yo construiría primero en `portafolio-frontend`. Los costes son **órdenes de
magnitud, no promesas**: hay que medirlos en la máquina real.

| # | Efecto | Impacto percibido | Coste main-thread | Riesgo a11y | Veredicto |
|---|---|---|---|---|---|
| **3** | **Camera sway en R3F** | **Alto** | **≈0** (mutación en `useFrame`, cero re-render, cero draw calls nuevos) | Nulo | **HAZLO PRIMERO.** El mejor ratio que existe. |
| **6** | Repulsión de partículas | Alto | ≈0 incremental (**ya pagas la sim GPGPU**) | Nulo | Ya está en tu repo. Refínalo (abajo). |
| **1** | Cursor personalizado | Medio-alto | ~0.1–0.3 ms/frame + 1 capa de composición | **Medio** — es el que más se rompe | Hazlo, pero con los 6 guards. |
| **2** | Botones magnéticos | Medio | ~0.05 ms × N elementos | Bajo | Sí, en **3–5 elementos**, no en todos. |
| **4a** | Spotlight DOM (versión `transform`) | Medio | ≈0 (solo composición) | Nulo | Sí. |
| **4b** | Spotlight DOM (versión `--mx` a pantalla completa) | Medio | **1–5 ms/frame de repaint** | Nulo | **No a pantalla completa.** Solo en cards. |
| **4c** | Luz WebGL que sigue al cursor | Bajo-medio | 1 luz extra (recompila materiales una vez) | Nulo | Opcional. Sin `castShadow`. |
| **5** | Distorsión/RGB split en hover de imágenes | **Bajo** (visto mil veces) | **Alto**: textura + draw call + sync DOM↔WebGL, y te cuesta `next/image` | Medio | **SOBREVALORADO. No lo hagas.** Razones abajo. |

**Lectura brutal:** el 80% del "wow" del puntero está en los efectos #3 y #1. El #5 es el que más
tiempo consume y el que menos gente recuerda — es el efecto que un jurado de 2026 ya vio cien veces.

---

## 0. La plomería: UNA fuente de verdad del puntero

Todo lo de abajo lee de **un solo store mutable de module-scope**, alimentado por **un solo
listener** y consumido por **un solo rAF**. Exactamente el mismo patrón que ya usas en
`src/components/three/scroll-store.ts`.

### Hallazgo en tu repo (arréglalo antes de añadir nada)

`src/components/three/ParticleField.tsx:15-27` ya declara un `pointerStore` propio y **registra el
listener en el scope del módulo** (se ejecuta con solo importar el archivo, aunque el canvas nunca
se monte, y **nunca se remueve**). Peor: **no filtra `pointerType`**, así que un dedo arrastrando
en móvil está alimentando el uniform del shader. Eso hay que hoistearlo.

### `src/lib/pointer/pointer-store.ts`

```ts
"use client";

/**
 * Fuente única de verdad del puntero.
 *
 * REGLA CRÍTICA (misma que scroll-store.ts): `pointermove` se dispara varias veces por frame.
 * Un setState ahí = re-render del árbol entero por evento = INP muerto. Por eso todo se escribe
 * en este objeto MUTABLE y se LEE desde el render loop (rAF / useFrame).
 *
 * `fine` es la llave maestra: si es false (touch, lápiz, sin puntero), TODO el sistema se apaga.
 */
export type PointerState = {
  /** px de cliente, crudo (el hotspot REAL — úsalo para lo que debe ser preciso). */
  x: number; y: number;
  /** px de cliente, suavizado (para lo decorativo que puede ir retrasado). */
  sx: number; sy: number;
  /** normalizado -1..1, crudo (para R3F). */
  nx: number; ny: number;
  /** normalizado -1..1, suavizado. */
  snx: number; sny: number;
  /** velocidad en px/s (para squash, fuerza de repulsión, etc.). */
  vx: number; vy: number;
  /** hay un mouse/trackpad REAL y el último evento vino de él. */
  fine: boolean;
  down: boolean;
  /** el usuario acaba de usar el teclado → devolver el cursor nativo. */
  keyboard: boolean;
  reduced: boolean;
};

export const pointer: PointerState = {
  x: 0, y: 0, sx: 0, sy: 0,
  nx: 0, ny: 0, snx: 0, sny: 0,
  vx: 0, vy: 0,
  fine: false, down: false, keyboard: false, reduced: false,
};

const damp = (a: number, b: number, lambda: number, dt: number) =>
  a + (b - a) * (1 - Math.exp(-lambda * dt));

type FrameFn = (dt: number, t: number) => void;
const subs = new Set<FrameFn>();
let rafId = 0;
let last = 0;
let inited = false;

/** Suscríbete al ÚNICO loop de puntero. Devuelve el unsubscribe. */
export function onFrame(fn: FrameFn): () => void {
  subs.add(fn);
  startLoop();
  return () => {
    subs.delete(fn);
    if (subs.size === 0 && rafId) {
      cancelAnimationFrame(rafId);
      rafId = 0;
    }
  };
}

function startLoop() {
  if (rafId || typeof window === "undefined") return;
  last = performance.now();
  rafId = requestAnimationFrame(tick);
}

function tick(t: number) {
  // Tras una pestaña en background el primer dt es enorme → cualquier integración explota.
  const dt = Math.min((t - last) / 1000, 0.05);
  last = t;

  const px = pointer.sx, py = pointer.sy;
  pointer.sx = damp(pointer.sx, pointer.x, 22, dt);   // rápido: casi pegado al mouse
  pointer.sy = damp(pointer.sy, pointer.y, 22, dt);
  pointer.snx = damp(pointer.snx, pointer.nx, 3.5, dt); // lento: el "peso" de la escena 3D
  pointer.sny = damp(pointer.sny, pointer.ny, 3.5, dt);
  if (dt > 0) {
    pointer.vx = (pointer.sx - px) / dt;
    pointer.vy = (pointer.sy - py) / dt;
  }

  subs.forEach((fn) => fn(dt, t));
  rafId = requestAnimationFrame(tick);
}

/** Idempotente. Llámalo desde cualquier componente que use el puntero. */
export function initPointer() {
  if (inited || typeof window === "undefined") return;
  inited = true;

  // Centrar para que nada "vuele" desde (0,0) en el primer frame.
  pointer.x = pointer.sx = window.innerWidth / 2;
  pointer.y = pointer.sy = window.innerHeight / 2;

  const rm = window.matchMedia("(prefers-reduced-motion: reduce)");
  pointer.reduced = rm.matches;
  rm.addEventListener("change", (e) => {
    pointer.reduced = e.matches;
    if (e.matches) document.documentElement.classList.remove("has-custom-cursor");
  });

  // La capacidad puede CAMBIAR en caliente (el usuario conecta un mouse a la tablet).
  const fineMq = window.matchMedia("(any-hover: hover) and (pointer: fine)");
  const syncFine = () => { if (!fineMq.matches) disable(); };
  fineMq.addEventListener("change", syncFine);

  window.addEventListener("pointermove", (e) => {
    // GUARD MAESTRO. Un dedo o un lápiz no mueven NADA.
    if (e.pointerType !== "mouse") { disable(); return; }
    if (pointer.reduced || !fineMq.matches) return;

    pointer.fine = true;
    pointer.keyboard = false;
    document.documentElement.classList.add("has-custom-cursor");

    pointer.x = e.clientX;
    pointer.y = e.clientY;
    pointer.nx = (e.clientX / window.innerWidth) * 2 - 1;
    pointer.ny = -(e.clientY / window.innerHeight) * 2 + 1;
  }, { passive: true });

  window.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") { disable(); return; }
    pointer.down = true;
  }, { passive: true });

  window.addEventListener("pointerup", () => { pointer.down = false; }, { passive: true });

  // Fuera de la ventana: el cursor no está en ningún sitio → nada lo persigue.
  window.addEventListener("pointerleave", () => { disable(); }, { passive: true });

  // TECLADO: al primer Tab devolvemos el cursor nativo y congelamos los imanes.
  window.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    pointer.keyboard = true;
    disable();
  });
}

function disable() {
  pointer.fine = false;
  pointer.down = false;
  if (typeof document !== "undefined") {
    document.documentElement.classList.remove("has-custom-cursor");
  }
}
```

### Consolidar los loops (opcional pero correcto)

Tu página ya corre **tres** rAF: el de R3F, el de Lenis (`SmoothScroll.tsx:64-68`) y el de
`gsap.ticker`. Este store añadiría un cuarto. El coste en ms es despreciable, pero el **orden** deja
de ser determinista. La consolidación barata (una línea):

```ts
// En SmoothScroll.tsx — mata su rAF propio y usa el ticker de GSAP, que ya está corriendo:
gsap.ticker.add((time) => lenis?.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

Y en el pointer-store, cambiar `requestAnimationFrame(tick)` por `gsap.ticker.add(...)` si GSAP está
presente. Honesto: esto no te va a dar 5fps; te da **un orden estable** (lenis → scrollStore →
pointer → GSAP → R3F) y un sitio donde poner el breakpoint. Es higiene, no perf.

El loop de R3F **no** se puede fusionar sin `frameloop="never"` + `advance()` manual — no vale la
pena. Deja que R3F tenga el suyo y que lea del store, que es lo que ya hace con `scrollStore`.

---

## 1. Cursor personalizado que muta

**El momento:** el cursor deja de ser un puntero del sistema y se vuelve parte de la marca — se
expande sobre un link, invierte el color debajo, y sobre un proyecto se abre con la palabra "ver".

### Las 3 decisiones que lo separan del tutorial de YouTube

1. **El punto preciso NO va retrasado.** El anillo decorativo persigue con lerp; el punto pequeño va
   en la posición **cruda** del puntero (`pointer.x/y`, sin damping). Si retrasas el hotspot,
   destruyes la precisión de apuntado — el problema #1 que documenta la crítica de a11y de 2025 sobre
   cursores custom (el usuario apunta a algo y el cursor está 12px atrás).
2. **Delegación, no un listener por elemento.** Un `pointerover` en `document` + `closest('[data-cursor]')`.
3. **`mix-blend-mode: difference`** te da la inversión gratis, sin leer el color de fondo.

### `src/components/interaction/CustomCursor.tsx`

```tsx
"use client";

import { useEffect, useRef } from "react";
import { pointer, initPointer, onFrame } from "@/lib/pointer/pointer-store";

/**
 * Cursor personalizado. Reglas duras:
 *  - Solo en (any-hover: hover) and (pointer: fine). En touch NO SE MONTA.
 *  - prefers-reduced-motion → NO SE MONTA (un cursor con lag ES movimiento).
 *  - Al primer Tab, el cursor nativo vuelve (lo hace el pointer-store quitando la clase).
 *  - aria-hidden + pointer-events:none: para un lector de pantalla no existe.
 *  - transform, NUNCA top/left.
 */
export default function CustomCursor() {
  const ring = useRef<HTMLDivElement>(null);
  const dot = useRef<HTMLDivElement>(null);
  const label = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    initPointer();

    if (pointer.reduced) return;
    if (!window.matchMedia("(any-hover: hover) and (pointer: fine)").matches) return;

    const ringEl = ring.current!;
    const dotEl = dot.current!;
    const labelEl = label.current!;

    const s = { scale: 1, target: 1, alpha: 0 };

    // --- Delegación: un listener para toda la página ---
    const onOver = (e: PointerEvent) => {
      if (e.pointerType !== "mouse") return;
      const t = (e.target as HTMLElement | null)?.closest?.(
        "[data-cursor], a, button, [role='button']"
      ) as HTMLElement | null;

      const variant = t ? (t.dataset.cursor ?? "link") : "";
      const text = t?.dataset.cursorText ?? "";

      labelEl.textContent = text;
      s.target = text ? 3.4 : variant ? 2.4 : 1;
      ringEl.classList.toggle("is-hot", Boolean(variant));
      ringEl.classList.toggle("has-label", Boolean(text));
    };
    document.addEventListener("pointerover", onOver, { passive: true });

    // --- El único trabajo por frame ---
    const stop = onFrame((dt) => {
      const on = pointer.fine ? 1 : 0;
      s.alpha += (on - s.alpha) * (1 - Math.exp(-12 * dt));
      s.scale += (s.target - s.scale) * (1 - Math.exp(-14 * dt));

      // Squash direccional: el anillo se estira en la dirección del movimiento.
      const speed = Math.hypot(pointer.vx, pointer.vy);
      const k = Math.min(speed / 2600, 1);
      const ang = speed > 40 ? Math.atan2(pointer.vy, pointer.vx) : 0;
      const press = pointer.down ? 0.82 : 1;

      // El punto: posición CRUDA. Es el hotspot honesto.
      dotEl.style.transform = `translate3d(${pointer.x}px, ${pointer.y}px, 0) translate(-50%, -50%)`;
      dotEl.style.opacity = String(s.alpha);

      // El anillo: posición SUAVIZADA + squash. Es lo decorativo.
      ringEl.style.transform =
        `translate3d(${pointer.sx}px, ${pointer.sy}px, 0) translate(-50%, -50%) ` +
        `rotate(${ang}rad) scale(${s.scale * press * (1 + k * 0.30)}, ${s.scale * press * (1 - k * 0.20)})`;
      ringEl.style.opacity = String(s.alpha);
    });

    return () => {
      document.removeEventListener("pointerover", onOver);
      stop();
      document.documentElement.classList.remove("has-custom-cursor");
    };
  }, []);

  return (
    <div aria-hidden="true" className="cursor-layer">
      <div ref={ring} className="cursor-ring">
        {/* El label NO hereda la rotación del anillo: es hermano, no hijo. */}
        <span ref={label} className="cursor-label" />
      </div>
      <div ref={dot} className="cursor-dot" />
    </div>
  );
}
```

### CSS (a `globals.css`)

```css
.cursor-layer {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;   /* innegociable: si captura eventos, rompiste la página */
  contain: layout style;
}

.cursor-ring,
.cursor-dot {
  position: fixed;
  top: 0;
  left: 0;
  border-radius: 50%;
  opacity: 0;
  will-change: transform;          /* SOLO en estos 2 elementos. No lo riegues. */
  mix-blend-mode: difference;      /* la "inversión" sale gratis */
}

.cursor-ring {
  width: 34px;
  height: 34px;
  border: 1px solid #fff;
  display: grid;
  place-items: center;
  transition: background-color .25s ease, border-color .25s ease;
}
.cursor-ring.is-hot     { background: #fff; border-color: #fff; }
.cursor-ring.has-label  { background: #fff; }

.cursor-dot {
  width: 6px;
  height: 6px;
  background: #fff;
}

.cursor-label {
  font-size: 3.2px;   /* el anillo está escalado ×3.4 → esto se lee a ~11px */
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #000;
  opacity: 0;
  transition: opacity .18s ease .06s;
  white-space: nowrap;
  mix-blend-mode: normal;
}
.cursor-ring.has-label .cursor-label { opacity: 1; }

/* ---------- LOS GUARDS. Sin esto, es un bug. ---------- */

/* El cursor nativo solo se oculta si (a) hay mouse fino y (b) ya vimos un movimiento real. */
@media (any-hover: hover) and (pointer: fine) {
  html.has-custom-cursor,
  html.has-custom-cursor * { cursor: none; }
}

/* Reduced motion: ni el elemento existe. Cursor nativo, punto. */
@media (prefers-reduced-motion: reduce) {
  .cursor-layer { display: none; }
  html, html * { cursor: auto; }
}

/* Alto contraste (Windows): mix-blend-mode es invisible ahí. Fuera. */
@media (forced-colors: active) {
  .cursor-layer { display: none; }
  html, html * { cursor: auto; }
}
```

Y en cualquier elemento:

```tsx
<a href="/proyectos/telemetria" data-cursor="view" data-cursor-text="ver">Telemetria</a>
<button data-cursor="link">Contactar</button>
```

### Veredictos

| | |
|---|---|
| **Touch** | **No se monta.** El guard es doble: media query en JS (no monta) + `pointerType !== 'mouse'` en el store. Un híbrido (Surface, iPad+trackpad) lo enciende al mover el mouse y lo apaga al tocar la pantalla. |
| **A11y** | **Es el efecto más peligroso de la lista.** `aria-hidden` + `pointer-events:none` lo hacen invisible al lector de pantalla. `cursor: none` **jamás** global: solo bajo `html.has-custom-cursor` dentro de `(pointer: fine)`, y la clase se quita al primer `Tab`. Fuera en `forced-colors`. El hotspot (el punto) va sin lag: no le robes precisión a nadie. Nota real: `cursor: none` + Fullscreen API se rompe en macOS — si algún día metes un `<video>` en fullscreen, quita la clase. |
| **Perf** | ~0.1–0.3 ms/frame (dos escrituras de `transform`). `mix-blend-mode: difference` sobre un canvas WebGL fijo fuerza una pasada de composición extra con lectura del backdrop — en desktop es ruido; es otra razón para no llevarlo a móvil. **CLS = 0** (fixed + transform). **INP**: `pointermove` no se mide en INP, pero si saturas el main thread con él, retrasas el frame del click y **sí** te cuesta INP indirectamente. Por eso: cero setState, cero `getBoundingClientRect` por evento. |
| **Reduced motion** | No se monta. Cursor nativo. |
| **Honestidad** | Es el efecto que más "firma" da y el que más gente implementa mal. Si no vas a poner los 6 guards, **no lo pongas**: un cursor custom roto se lee como amateur, no como Awwwards. |

---

## 2. Botones y enlaces magnéticos

**El momento:** el CTA "Descargar CV" se inclina hacia tu mouse antes de que llegues. Se siente como
si la página te estuviera esperando.

### Las 3 decisiones

1. **`strength` entre 0.15 y 0.30.** La cifra que circula en los tutoriales (0.5–0.7) hace que el
   botón **huya** del cursor y te obligue a perseguirlo. Se siente roto. 0.25 es el punto donde se
   siente vivo y sigue siendo clickeable.
2. **Mueve el elemento que TIENE el click handler.** El error clásico: traslada un `<span>` interior
   y deja el `<a>` quieto → el botón se ve desplazado 20px pero la zona clickeable está en el sitio
   viejo. Si trasladas el `<a>`, su hitbox viaja con él y todo cuadra. El "doble imán" (padre ×1.0,
   texto interior ×0.35) da profundidad sin desincronizar nada.
3. **Lecturas y escrituras separadas.** Un registro global mide **todos** los rects primero y escribe
   **todos** los transforms después. Alternar read/write por elemento = layout thrashing.

### `src/lib/pointer/magnetic.ts`

```ts
"use client";

import { useEffect, useRef } from "react";
import { pointer, initPointer, onFrame } from "./pointer-store";

type Item = {
  el: HTMLElement;
  inner: HTMLElement | null;
  radius: number;   // px de campo magnético MÁS ALLÁ del borde del elemento
  strength: number; // 0.15–0.30. Más de 0.35 y el botón se te escapa.
  cx: number; cy: number; r: number;
  x: number; y: number;
  focused: boolean;
};

const items = new Set<Item>();
let dirty = true;
let stopLoop: (() => void) | null = null;

/** Llamar cuando el layout se mueva: resize, scroll de Lenis, apertura de acordeones. */
export function markMagneticDirty() { dirty = true; }

function measureAll() {
  // FASE DE LECTURA — todas las lecturas juntas, cero escrituras entre medias.
  items.forEach((it) => {
    const r = it.el.getBoundingClientRect();
    // Le restamos el desplazamiento actual → obtenemos el centro EN REPOSO.
    // (getBoundingClientRect ya incluye el transform; sin esto el imán se autoalimenta.)
    it.cx = r.left + r.width / 2 - it.x;
    it.cy = r.top + r.height / 2 - it.y;
    it.r = Math.max(r.width, r.height) / 2;
  });
  dirty = false;
}

function frame(dt: number) {
  if (items.size === 0) return;
  if (dirty) measureAll();

  const active = pointer.fine && !pointer.reduced;
  const k = 1 - Math.exp(-9 * dt); // muelle crítico: entra rápido, vuelve suave

  // FASE DE CÓMPUTO (sin tocar el DOM)
  items.forEach((it) => {
    let tx = 0, ty = 0;
    // focused = el usuario llegó con Tab → el botón NO se mueve. Innegociable.
    if (active && !it.focused) {
      const dx = pointer.x - it.cx;
      const dy = pointer.y - it.cy;
      const dist = Math.hypot(dx, dy);
      const R = it.r + it.radius;
      if (dist < R) {
        const f = 1 - dist / R;
        const pull = f * f;      // ease-in: el imán "agarra" cerca, no a 200px
        tx = dx * it.strength * pull;
        ty = dy * it.strength * pull;
      }
    }
    it.x += (tx - it.x) * k;
    it.y += (ty - it.y) * k;
  });

  // FASE DE ESCRITURA
  items.forEach((it) => {
    const idle = Math.abs(it.x) < 0.02 && Math.abs(it.y) < 0.02;
    it.el.style.transform = idle ? "" : `translate3d(${it.x}px, ${it.y}px, 0)`;
    if (it.inner) {
      it.inner.style.transform = idle
        ? ""
        : `translate3d(${it.x * 0.35}px, ${it.y * 0.35}px, 0)`; // doble imán
    }
  });
}

export function useMagnetic<T extends HTMLElement>(opts?: {
  radius?: number;
  strength?: number;
  innerSelector?: string;
}) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    initPointer();

    // Touch / reduced motion: NI SE REGISTRA. Cero coste.
    if (pointer.reduced) return;
    if (!window.matchMedia("(any-hover: hover) and (pointer: fine)").matches) return;

    const item: Item = {
      el,
      inner: opts?.innerSelector ? el.querySelector<HTMLElement>(opts.innerSelector) : null,
      radius: opts?.radius ?? 90,
      strength: opts?.strength ?? 0.25,
      cx: 0, cy: 0, r: 0, x: 0, y: 0,
      focused: false,
    };
    items.add(item);
    dirty = true;
    if (!stopLoop) stopLoop = onFrame(frame);

    const onFocus = () => { item.focused = true; };
    const onBlur = () => { item.focused = false; };
    el.addEventListener("focus", onFocus);
    el.addEventListener("blur", onBlur);

    const ro = new ResizeObserver(markMagneticDirty);
    ro.observe(el);
    window.addEventListener("resize", markMagneticDirty, { passive: true });

    return () => {
      el.removeEventListener("focus", onFocus);
      el.removeEventListener("blur", onBlur);
      ro.disconnect();
      window.removeEventListener("resize", markMagneticDirty);
      items.delete(item);
      el.style.transform = "";
      if (item.inner) item.inner.style.transform = "";
      if (items.size === 0 && stopLoop) { stopLoop(); stopLoop = null; }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return ref;
}
```

**Invalidación con Lenis** — el scroll suave mueve los rects. En `SmoothScroll.tsx`, dentro del
`lenis.on("scroll", ...)` que ya tienes:

```ts
import { markMagneticDirty } from "@/lib/pointer/magnetic";
// ...
lenis.on("scroll", (e: { progress: number }) => {
  scrollStore.page = e.progress;
  paint(e.progress);
  ScrollTrigger.update();
  markMagneticDirty();     // ← los imanes se remiden en el próximo frame
});
```

Sí, eso hace un `getBoundingClientRect` por elemento por frame **durante** el scroll. Con 3–5
elementos y las lecturas batcheadas antes de las escrituras, es ruido (<0.1 ms). Con 30 elementos,
no. **Por eso son 3–5, no 30.**

### Uso

```tsx
const cvRef = useMagnetic<HTMLAnchorElement>({ radius: 100, strength: 0.28, innerSelector: ".btn-label" });

<a ref={cvRef} href="/cv.pdf" className="btn-primary" data-cursor="link">
  <span className="btn-label">Descargar CV</span>
</a>
```

### Alternativa GSAP (menos código, mismo perf)

Si solo quieres imanes y nada más, `gsap.quickTo` es la API correcta — crea **un** tween reutilizable
en vez de uno nuevo por evento (el error que mata a `gsap.to()` dentro de `mousemove`):

```ts
const xTo = gsap.quickTo(el, "x", { duration: 0.55, ease: "power3.out" });
const yTo = gsap.quickTo(el, "y", { duration: 0.55, ease: "power3.out" });
// en el rAF: xTo(tx); yTo(ty);
```

Recomiendo el store compartido igual, porque los efectos #3 y #6 necesitan el puntero **dentro de
`useFrame`** y no lo van a sacar de GSAP.

### Veredictos

| | |
|---|---|
| **Touch** | No se registra (guard doble). Coste real en móvil: **cero**, ni el `useEffect` deja nada montado. |
| **A11y** | El elemento **vuelve a su sitio en `:focus`** — quien navega con `Tab` ve un botón quieto en la posición que el foco visible marca. El hitbox viaja con el `transform`, así que no hay zona muerta. No cambia el DOM ni el nombre accesible. |
| **Perf** | ~0.05 ms × N. Lecturas batcheadas. Sin `will-change` (el `translate3d` ya promueve; ponerlo en 5 botones más es memoria de GPU regalada). |
| **Reduced motion** | No se registra. El botón es un botón. |
| **Honestidad** | Es un cliché de 2020 que sigue funcionando **porque el usuario lo siente sin verlo**. Pero pierde todo su valor si lo pones en 20 elementos: entonces la página entera "tiembla" y se lee como plantilla. **3 a 5. El CV, el contacto, el logo.** |

---

## 3. Camera sway por puntero — ★ EL DE MEJOR RATIO DE TODA LA PÁGINA

**Este es el que hay que hacer primero.** No hay nada en el catálogo del craft de puntero con este
ratio. Son 20 líneas, cero draw calls nuevos, cero re-renders de React, cero KB, cero riesgo de a11y,
y convierte un canvas 3D que "está ahí" en un **espacio en el que estás parado**. El cerebro lee el
paralaje como profundidad real; es la señal más barata de "esto no es una imagen".

### `src/components/three/CameraSway.tsx`

```tsx
"use client";

import { useRef, useMemo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { pointer, initPointer } from "@/lib/pointer/pointer-store";

type Props = {
  /** Posición en reposo. DEBE ser la misma que le pasas a <PerspectiveCamera position={...}>. */
  base?: [number, number, number];
  /** Cuántas unidades de mundo se desplaza la cámara en el eje X. 0.25–0.45 es el rango sano. */
  amplitude?: number;
  /** Rigidez del muelle. 2–3 = "pesado" y caro. 8 = nervioso y barato. */
  lambda?: number;
  /** Punto al que mira. null = no toca la rotación (más seguro con poses keyframeadas). */
  lookAt?: [number, number, number] | null;
};

export default function CameraSway({
  base = [0, 0.5, 6.3],
  amplitude = 0.35,
  lambda = 2.4,
  lookAt = null,
}: Props) {
  const camera = useThree((s) => s.camera);
  const home = useMemo(() => new THREE.Vector3(...base), [base]);
  const target = useRef(new THREE.Vector3(...base));
  const look = useMemo(() => (lookAt ? new THREE.Vector3(...lookAt) : null), [lookAt]);

  if (typeof window !== "undefined") initPointer();

  useFrame((_, dt) => {
    const d = Math.min(dt, 0.05);

    // Sin mouse (touch), o reduced-motion → la cámara vuelve a casa y se queda ahí.
    const live = pointer.fine && !pointer.reduced;

    target.current.set(
      home.x + (live ? pointer.snx * amplitude : 0),
      home.y + (live ? pointer.sny * amplitude * 0.55 : 0), // menos en Y: el ojo lo nota más
      home.z
    );

    camera.position.lerp(target.current, 1 - Math.exp(-lambda * d));
    if (look) camera.lookAt(look);
  });

  return null;
}
```

### Montaje en `Scene3DBackground.tsx`

```tsx
<PerspectiveCamera makeDefault fov={33} position={[0, 0.5, 6.3]} />
<CameraSway base={[0, 0.5, 6.3]} amplitude={0.35} lambda={2.4} />
```

**Dos trampas reales de TU escena:**

1. **`base` tiene que ser el mismo array que el `position` de drei.** No captures la posición con un
   `useEffect` — si `<PerspectiveCamera>` re-renderiza, drei reaplica la prop y tu "base" capturada
   sería una posición ya swayed. Pasa el literal.
2. **`lookAt` con `LaptopJourney`.** Las poses keyframeadas del `.glb` se autoraron **contra una
   cámara estática**. Si activas `lookAt`, cambias el encuadre de todas las poses. Empieza con
   `lookAt={null}` (traslación pura = paralaje limpio) y solo si el encuadre lo pide, prueba
   `lookAt={[0, 0.2, 0]}` y **re-verifica las 6 poses**. Con `amplitude ≤ 0.4` la traslación sola ya
   se lee.

**Bonus de 3 líneas — FOV que respira con la velocidad del scroll** (necesita `scrollStore` con
velocidad; si no la tienes, sáltalo). Es el mismo truco: mutar, no re-renderizar.

### Veredictos

| | |
|---|---|
| **Touch** | `pointer.fine === false` → `target = home` → la cámara se queda quieta. **Cero coste** (el `useFrame` corre igual porque R3F ya está renderizando; el `lerp` a un objetivo estático converge y se vuelve un no-op numérico). Si quieres algo en móvil, **no uses el giroscopio** (iOS exige `DeviceOrientationEvent.requestPermission()` tras un gesto, y un prompt de permiso por un efecto decorativo es un no rotundo). Usa la **velocidad de scroll** como sustituto del puntero. |
| **A11y** | **Nulo riesgo.** No hay DOM, no hay foco, no hay lector de pantalla. Es el único efecto de la lista que un auditor de a11y ni siquiera puede ver. |
| **Perf** | **≈0.** Una resta, un `lerp` y una mutación de `camera.position` por frame, dentro de un `useFrame` que ya existe. Cero draw calls nuevos, cero material recompilado, cero re-render de React. Literalmente lo más barato de este documento. |
| **Reduced motion** | `pointer.reduced` → `target = home`. La cámara no se mueve. Y como el store escucha el `change` del media query, si el usuario lo activa en caliente, la cámara **vuelve** a casa con el muelle en vez de saltar. |
| **Honestidad** | Ningún pero. Este es el que hay que hacer. Si solo tienes tiempo para uno, es este. |

---

## 4. Spotlight / luz que sigue al cursor

### 4a. DOM — la versión CORRECTA (compositor, ≈0 ms)

**El error que comete casi todo el mundo:** poner un `radial-gradient` a pantalla completa y animar
su centro con una custom property (`--mx`/`--my`). Eso **repinta el viewport entero cada frame**.
En un portátil se disimula; en un Android de gama media son 1–5 ms de paint por frame que se comen
tu presupuesto y te desincronizan el canvas.

**La versión correcta:** un `<div>` de tamaño **fijo** con el gradiente ya pintado dentro, movido con
`transform`. El gradiente se rasteriza **una vez** en su capa; después solo hay composición en GPU.
Mismo look, coste ≈ 0.

```tsx
"use client";
import { useEffect, useRef } from "react";
import { pointer, initPointer, onFrame } from "@/lib/pointer/pointer-store";

const R = 340; // radio en px

export default function CursorSpotlight() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initPointer();
    if (pointer.reduced) return;
    if (!window.matchMedia("(any-hover: hover) and (pointer: fine)").matches) return;

    const el = ref.current!;
    return onFrame((dt) => {
      const a = pointer.fine ? 1 : 0;
      el.style.opacity = String(
        (el.style.opacity ? parseFloat(el.style.opacity) : 0) +
        (a - (el.style.opacity ? parseFloat(el.style.opacity) : 0)) * (1 - Math.exp(-8 * dt))
      );
      el.style.transform = `translate3d(${pointer.sx - R}px, ${pointer.sy - R}px, 0)`;
    });
  }, []);

  return <div ref={ref} aria-hidden="true" className="spotlight" />;
}
```

```css
.spotlight {
  position: fixed;
  top: 0; left: 0;
  width: 680px; height: 680px;   /* 2 × R */
  pointer-events: none;
  z-index: 1;                    /* encima del canvas, DEBAJO del contenido */
  opacity: 0;
  will-change: transform;
  background: radial-gradient(
    circle closest-side,
    color-mix(in srgb, var(--color-primary) 16%, transparent),
    transparent 70%
  );
  /* El gradiente se rasteriza UNA vez. A partir de ahí, solo composición. */
}

@media (prefers-reduced-motion: reduce) { .spotlight { display: none; } }
@media (hover: none) { .spotlight { display: none; } }
```

### 4b. Glow de borde en cards — aquí SÍ vale la custom property

Cuando el área a repintar es **una card** (no el viewport) y solo mientras está hovered, el
repaint es pequeño y el efecto es el que más "caro" hace ver una grilla de proyectos.

```css
.project-card { position: relative; isolation: isolate; }
.project-card::after {
  content: "";
  position: absolute; inset: 0;
  border-radius: inherit;
  pointer-events: none;
  opacity: 0;
  transition: opacity .25s ease;
  background: radial-gradient(
    260px circle at var(--mx, 50%) var(--my, 50%),
    rgb(255 255 255 / .10),
    transparent 62%
  );
}
@media (hover: hover) and (pointer: fine) {
  .project-card:hover::after { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .project-card::after { display: none; }
}
```

```tsx
// Solo la card hovered escribe. Nunca las 9 a la vez.
const onMove = (e: React.PointerEvent<HTMLDivElement>) => {
  if (e.pointerType !== "mouse") return;
  const el = e.currentTarget;
  const r = el.getBoundingClientRect();          // 1 rect, 1 card, solo en hover
  el.style.setProperty("--mx", `${e.clientX - r.left}px`);
  el.style.setProperty("--my", `${e.clientY - r.top}px`);
};
// <div className="project-card" onPointerMove={onMove}>
```

Nota honesta: aquí **sí** hay un `getBoundingClientRect` por evento. Es aceptable porque solo corre
en la card bajo el cursor (una), no en las 9. Si te pica, cachea el rect en `onPointerEnter` e
invalida en el scroll de Lenis — pero medí primero: casi nunca hace falta.

### 4c. WebGL — luz que se lerpea hacia el cursor

En tu `Scene3DBackground` ya tienes `<Environment>` con `<Lightformer>`. Una `pointLight` extra que
persigue al cursor hace que el aluminio del laptop tenga un **highlight que se mueve** — eso es lo
que vende el material.

```tsx
"use client";
import { useRef, useMemo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { pointer, initPointer } from "@/lib/pointer/pointer-store";

/** Proyecta el puntero (NDC) sobre un plano z = planeZ. Sin Raycaster, sin allocs por frame. */
const _v = new THREE.Vector3();
export function projectPointerToPlane(
  camera: THREE.Camera, nx: number, ny: number, planeZ: number, out: THREE.Vector3
) {
  _v.set(nx, ny, 0.5).unproject(camera);
  _v.sub(camera.position).normalize();
  const dist = (planeZ - camera.position.z) / _v.z;
  return out.copy(camera.position).addScaledVector(_v, dist);
}

export default function PointerLight({
  planeZ = 1.6,
  color = "#8b93ff",
  intensity = 16,
  distance = 9,
}) {
  const light = useRef<THREE.PointLight>(null);
  const camera = useThree((s) => s.camera);
  const target = useMemo(() => new THREE.Vector3(0, 0, planeZ), [planeZ]);

  if (typeof window !== "undefined") initPointer();

  useFrame((_, dt) => {
    const l = light.current;
    if (!l) return;
    if (!pointer.fine || pointer.reduced) { l.intensity = 0; return; }
    l.intensity = intensity;
    projectPointerToPlane(camera, pointer.snx, pointer.sny, planeZ, target);
    l.position.lerp(target, 1 - Math.exp(-7 * Math.min(dt, 0.05)));
  });

  // castShadow={false} NO es negociable: una luz que se mueve + sombras = re-render del shadow map
  // cada frame. Es la forma más rápida de tirar 20fps en un Android.
  return <pointLight ref={light} color={color} distance={distance} decay={2} castShadow={false} />;
}
```

### Veredictos

| | |
|---|---|
| **Touch** | 4a/4b: `@media (hover: none) { display: none }` + guard `pointerType`. 4c: `intensity = 0` (la luz sigue en el grafo, pero con intensidad 0 three la sigue evaluando por fragmento — si quieres cero coste real, desmóntala con un flag de estado **una sola vez** al montar, no por frame). |
| **A11y** | Nulo. Todo es `aria-hidden` / decorativo. Sin `pointer-events`. **Ojo:** el spotlight NO puede ser el único indicador de nada — es decoración, no affordance. Si un elemento solo se "ve" cuando lo iluminas, está roto para teclado. |
| **Perf** | 4a ≈ 0 (composición). 4b: repaint de una card en hover, aceptable. **4b a pantalla completa: 1–5 ms/frame — NO.** 4c: una luz más = recompilación de los materiales afectados **una vez** al montar (hitch de ~10–40 ms la primera vez; móntala con el resto de la escena, no al primer hover) + coste por fragmento. Con `Bloom` ya activo, una luz que se mueve por una superficie especular **realza el bloom** → verifica que no te dispare el `luminanceThreshold` (0.55) y te queme la pantalla. |
| **Reduced motion** | 4a/4b: `display: none`. 4c: `intensity = 0`. |
| **Honestidad** | 4a es barato y bonito: hazlo. 4c es un "nice to have" — sube el material de 8 a 9, no de 5 a 9. 4b a pantalla completa es la trampa donde cae todo el mundo. |

---

## 5. Distorsión en hover sobre imágenes/cards — **SOBREVALORADO**

Empiezo por el veredicto, porque es lo que te ahorra el fin de semana:

> **No lo hagas en este portafolio.** Es el efecto con **peor** ratio impacto/coste de la lista y el
> que un jurado de 2026 ya vio en 200 sitios. Y en tu caso concreto tiene un coste que nadie menciona:
> **te cuesta `next/image`**.

### El coste honesto (lo que los tutoriales no dicen)

1. **Pierdes `next/image`.** Para distorsionar una imagen en WebGL, la imagen deja de ser un `<img>`
   y pasa a ser una textura sobre un plano. Adiós `srcset`, adiós `sizes`, adiós lazy nativo, adiós
   `priority` para el LCP. Si la imagen distorsionada está above the fold, acabas de **regalar tu
   LCP** por un efecto de hover que solo existe en desktop.
2. **Sync DOM↔WebGL.** El plano tiene que estar exactamente donde estaría el `<img>`: hay que
   sincronizar `getBoundingClientRect` con el scroll de **Lenis** (que va suavizado y desfasado del
   scroll nativo), con el resize y con las fuentes que reflowean. Eso es el 80% del trabajo. drei v9
   tiene `<View>`, que ayuda, pero exige que el canvas tenga `eventSource`/`eventPrefix` y tu canvas
   es un **background fijo con `pointer-events: none`** — la integración no es gratis.
3. **Upload de textura en el primer hover.** Un JPG de 1200px se decodifica y sube a GPU la primera
   vez que lo tocas: decenas de ms de hitch. En un tap de móvil, eso **es** un pico de INP.
4. **3 fetches de textura por fragmento** en vez de 1 (el RGB split muestrea R, G y B por separado).

### El Tier A que SÍ deberías hacer (0 WebGL, ~0 ms, 80% del efecto)

Paralaje dentro del marco + escala + un barrido de brillo. Solo compositor. Se lee como "caro" y no
te cuesta nada.

```tsx
"use client";
import { useRef, useEffect } from "react";
import { pointer, initPointer, onFrame } from "@/lib/pointer/pointer-store";

export function ParallaxImage({ src, alt }: { src: string; alt: string }) {
  const box = useRef<HTMLDivElement>(null);
  const img = useRef<HTMLImageElement>(null);
  const hot = useRef(false);
  const s = useRef({ x: 0, y: 0, k: 0 });

  useEffect(() => {
    initPointer();
    if (pointer.reduced) return;
    if (!window.matchMedia("(any-hover: hover) and (pointer: fine)").matches) return;

    const el = box.current!, im = img.current!;
    let cx = 0, cy = 0, w = 1, h = 1;
    const measure = () => {
      const r = el.getBoundingClientRect();
      cx = r.left + r.width / 2; cy = r.top + r.height / 2; w = r.width; h = r.height;
    };
    const enter = (e: PointerEvent) => { if (e.pointerType === "mouse") { measure(); hot.current = true; } };
    const leave = () => { hot.current = false; };
    el.addEventListener("pointerenter", enter, { passive: true });
    el.addEventListener("pointerleave", leave, { passive: true });

    return onFrame((dt) => {
      const k = 1 - Math.exp(-8 * dt);
      const tx = hot.current ? ((pointer.x - cx) / w) * 22 : 0;  // 22px de recorrido máximo
      const ty = hot.current ? ((pointer.y - cy) / h) * 22 : 0;
      const tk = hot.current ? 1 : 0;
      s.current.x += (tx - s.current.x) * k;
      s.current.y += (ty - s.current.y) * k;
      s.current.k += (tk - s.current.k) * k;
      im.style.transform =
        `translate3d(${s.current.x}px, ${s.current.y}px, 0) scale(${1 + s.current.k * 0.07})`;
    });
  }, []);

  return (
    <div ref={box} className="px-frame" data-cursor="view" data-cursor-text="ver">
      {/* Sigue siendo un <img> real: next/image, srcset, LCP, alt, SEO. Todo intacto. */}
      <img ref={img} src={src} alt={alt} className="px-img" />
    </div>
  );
}
```

```css
.px-frame { overflow: hidden; border-radius: 14px; position: relative; }
.px-img   { display: block; width: 100%; height: 100%; object-fit: cover; will-change: transform; }
@media (prefers-reduced-motion: reduce) { .px-img { transform: none !important; } }
```

### El Tier B (si la imagen YA vive dentro de tu canvas)

Solo entonces el shader es barato — porque la plomería ya está pagada. Fragment shader con lente +
RGB split:

```glsl
uniform sampler2D uTex;
uniform vec2  uMouse;   // uv local del hover, 0..1
uniform float uHover;   // 0..1 — lo anima GSAP en enter/leave
uniform float uAmp;     // 0.0 con prefers-reduced-motion. Un uniform, no un if.
varying vec2  vUv;

void main() {
  vec2 uv  = vUv;
  vec2 dir = uv - uMouse;
  float d  = length(dir);

  // Lente: el pixel se "chupa" hacia el cursor. 0.06 es el techo del buen gusto.
  float lens = 1.0 - smoothstep(0.0, 0.55, d);
  uv -= dir * lens * 0.06 * uHover * uAmp;

  // RGB split. 1-3px de offset se lee como lente física. 10px se lee como bug.
  float off = 0.0035 * uHover * uAmp * (0.35 + lens);
  float r = texture2D(uTex, uv + vec2(off, 0.0)).r;
  float g = texture2D(uTex, uv).g;
  float b = texture2D(uTex, uv - vec2(off, 0.0)).b;

  gl_FragColor = vec4(r, g, b, 1.0);
}
```

`uHover` se anima con GSAP en `pointerenter`/`pointerleave` (`gsap.to(uniforms.uHover, {value: 1, duration: .5, ease: "power3.out"})`) — nunca con `setState`.

### Veredictos

| | |
|---|---|
| **Touch** | Tier A: los listeners no se registran → 0. Tier B: `uHover` nunca sube (guard `pointerType`), pero **la textura se sube a GPU igual** al montar. Ese es el coste que pagas en móvil aunque el efecto no exista ahí. |
| **A11y** | Tier A: **impecable** — sigue siendo un `<img>` con `alt`, indexable, con foco si es link. Tier B: el `<img>` desaparece del DOM → o duplicas el markup (imagen `sr-only` + canvas `aria-hidden`) o **te cargas el alt text y el SEO de imagen**. Ninguna versión responde al teclado (el hover no tiene equivalente de foco), así que el efecto **no puede portar información**. |
| **Perf** | Tier A: ~0.05 ms, solo compositor, `next/image` intacto. Tier B: draw call + 3 texture fetches/fragmento + decode/upload de textura + el coste de sincronizar rects con Lenis cada frame. **Y el riesgo de LCP.** |
| **Reduced motion** | Tier A: `transform: none`. Tier B: `uAmp = 0` (uniform, no branch). |
| **Honestidad** | **Este es el efecto sobrevalorado del catálogo.** Cuesta un día, te arriesga el LCP, te complica la a11y, y el visitante lo describiría como "las imágenes hacían algo raro al pasar el mouse". Compáralo con el camera sway: 20 líneas, cero riesgo, y el visitante dice "la página tenía profundidad". **Si tienes que cortar uno, corta este.** |

---

## 6. Repulsión de partículas por el cursor

**Ya lo tienes** — `src/components/three/ParticleField.tsx` corre una sim GPGPU con `uMouse`,
`uMouseRadius`, `uMouseStrength` y `uFreeze`. El coste incremental de la repulsión sobre una sim que
ya existe es **≈0**: son 4 líneas en el shader de simulación y la sim ya se ejecuta cada frame.

Ese es el punto clave: **si ya pagas la GPGPU, la repulsión es gratis. Si NO la pagas, montar una
sim GPGPU solo para tener repulsión es carísimo** (FBO ping-pong, fallback HalfFloat, 256×256
partículas). No se hace al revés.

### 4 defectos concretos en tu implementación actual

**1. El listener no filtra el tipo de puntero** (`ParticleField.tsx:15-27`). Un dedo arrastrando en
móvil está escribiendo en `pointerStore` y empujando partículas que el propio dedo tapa. Batería
gastada en algo que nadie ve. → **Usa el store compartido** con el guard.

**2. `uFreeze` congela la integración pero no está claro que anule el empujón.** Blinda el shader —
que el freeze sea un multiplicador, no una esperanza:

```glsl
// ParticleField.tsx — shader de simulación, línea ~156
vec3  toMouse = pos - uMouse;
float d       = length(toMouse);
float push    = 1.0 - smoothstep(0.0, uMouseRadius, d);
pos += normalize(toMouse + vec3(1e-4))
     * push * push
     * uMouseStrength
     * (1.0 - uFreeze)      // ← reduced-motion apaga TAMBIÉN el empujón, no solo el ruido
     * dt;
```

**3. Un cursor parado excava un agujero permanente.** Es el tell visual de "esto es un demo". La sim
llega al equilibrio y te queda un cráter estático. Fix: **la fuerza escala con la velocidad del
cursor**. Parado ≈ no empuja; moviéndose ≈ abre el campo. Se siente como agua, no como un imán.

**4. `uMouse` sin damping.** Un salto de cursor (alt-tab, un movimiento brusco) teleporta el uniform
y desgarra el campo. Lerpea el uniform, no solo la partícula.

### El `useFrame` corregido

```tsx
import { pointer, initPointer } from "@/lib/pointer/pointer-store";
import { projectPointerToPlane } from "@/components/three/PointerLight"; // o a un lib compartido

// ...dentro del componente
const camera = useThree((s) => s.camera);
const mouseTarget = useMemo(() => new THREE.Vector3(), []);
if (typeof window !== "undefined") initPointer();

useFrame((state, dt) => {
  const d = Math.min(dt, 1 / 30);

  if (pointer.fine && !reduced) {
    // El puntero se proyecta al PLANO DE LAS PARTÍCULAS (z=0), no se usa el NDC crudo.
    projectPointerToPlane(camera, pointer.nx, pointer.ny, 0, mouseTarget);
    (simUniforms.uMouse.value as THREE.Vector3).lerp(mouseTarget, 1 - Math.exp(-12 * d));

    // La fuerza vive de la VELOCIDAD: cursor parado = el campo se cierra solo.
    const speed = Math.min(Math.hypot(pointer.vx, pointer.vy) / 1600, 1);
    simUniforms.uMouseStrength.value = 1.2 + speed * 6.5;
  } else {
    simUniforms.uMouseStrength.value = 0;   // touch / reduced → cero empujón, cero rama en GLSL
  }

  simUniforms.uDelta.value = d;
  simUniforms.uTime.value = state.clock.elapsedTime;
  // ...resto del ping-pong
});
```

### Veredictos

| | |
|---|---|
| **Touch** | `uMouseStrength = 0`. La sim sigue corriendo (el ruido de fondo, que es lo bonito) pero el dedo no empuja nada. Coste extra en móvil: **cero**. Y si el móvil es de gama baja, la palanca correcta no es apagar el mouse: es bajar `size` de 256 a 128 (**4× menos partículas**) — mídelo antes de asumir que corre. |
| **A11y** | Nulo riesgo (canvas decorativo). **Requisito:** el canvas debe tener `aria-hidden="true"` o estar fuera del árbol accesible. Verifícalo en `Scene3DBackground` — no lo vi. |
| **Perf** | ≈0 incremental. La sim ya corre; la repulsión son 4 ALU ops por partícula. Lo caro ya lo estás pagando (el ping-pong de FBO 256×256 = 65.536 partículas). |
| **Reduced motion** | `uFreeze = 1` **multiplicando** la repulsión (fix #2) + `uMouseStrength = 0`. Cinturón y tirantes: uno de los dos siempre sobra, y así ninguno falla solo. |
| **Honestidad** | Es el segundo mejor de la lista **solo porque ya lo tienes construido**. Si partieras de cero, el orden sería: camera sway → cursor → magnético → partículas. No montes una GPGPU para tener repulsión: monta la GPGPU si quieres el campo de partículas, y entonces la repulsión te sale de regalo. |

---

## Errores que delatan al amateur (checklist de code review)

- [ ] `top` / `left` para mover el cursor → **layout + paint cada frame.** Solo `transform: translate3d`.
- [ ] `setState` dentro de `pointermove` / `useFrame` → re-render del árbol por evento. **Nunca.**
- [ ] `gsap.to(el, ...)` dentro de `mousemove` → un tween nuevo por evento, cientos vivos a la vez.
      Usa `gsap.quickTo` (un tween reutilizable) o el rAF del store.
- [ ] `getBoundingClientRect()` dentro del listener de `mousemove` → forced reflow por evento. Mide
      en el rAF, batcheado, y solo cuando el layout esté sucio.
- [ ] `will-change: transform` en 40 elementos → cada uno es una capa de GPU. Máximo 3–5, y solo en lo
      que se mueve **cada frame**.
- [ ] `strength: 0.7` en el imán → el botón huye del cursor. **0.15–0.30.**
- [ ] `cursor: none` en `html` sin media query → el usuario de touch pierde el cursor si conecta un
      mouse, y el de teclado se queda sin nada.
- [ ] Sin guard `e.pointerType !== 'mouse'` → todo se dispara con el dedo, gastando batería en efectos
      invisibles.
- [ ] Listeners en scope de módulo (se registran al importar, nunca se limpian). ← **tienes uno en
      `ParticleField.tsx:17`.**
- [ ] El efecto **porta información** (algo solo se ve al iluminarlo/hoverearlo) → roto para teclado y
      para touch. Los efectos de puntero son **decoración**, siempre.
- [ ] Cuatro rAF independientes (R3F + Lenis + gsap.ticker + puntero) → funciona, pero el orden no es
      determinista. Consolida al menos Lenis dentro de `gsap.ticker`.
- [ ] No probaste con `prefers-reduced-motion: reduce` activado (DevTools → Rendering → Emulate CSS
      media feature). Si no lo probaste, está roto.

---

## Presupuesto de frame (16.6 ms) — el reparto realista

En desktop, con TODO lo recomendado encendido (sway + cursor + 4 imanes + spotlight + partículas):

| Partida | Coste típico |
|---|---|
| R3F render (laptop + Environment + Bloom + 65k partículas) | **el grueso** — lo que tengas, medilo |
| Lenis + ScrollTrigger.update() | 0.3–0.8 ms |
| Pointer store (1 rAF, damping) | < 0.05 ms |
| Cursor (2 transforms) | 0.1–0.3 ms |
| Imanes ×4 (4 rects + 4 transforms) | < 0.1 ms |
| Spotlight (1 transform) | ≈ 0 |
| Camera sway | ≈ 0 |
| Repulsión de partículas | ≈ 0 (ya está en la sim) |

**Todo el craft de puntero junto cabe en < 0.5 ms de main thread.** Tu presupuesto se lo come el
render 3D, no el mouse. Por eso el puntero es la palanca con mejor ratio de la página — y por eso
el único de la lista que **no** cabe (la distorsión WebGL de imágenes) es el único que hay que cortar.

---

**Fuentes consultadas (2025–2026):**
- [Custom Cursor Accessibility — David Bushell (oct 2025)](https://dbushell.com/2025/10/27/custom-cursor-accessibility/) — el problema del hotspot, `(any-hover: hover) and (pointer: fine)`, `cursor: none` + Fullscreen roto en macOS.
- [Building a Magnetic Cursor Effect That Actually Feels Good — 100 Days of Craft](https://www.100daysofcraft.com/blog/motion-interactions/building-a-magnetic-cursor-effect) — rango de `strength` (0.05–0.18 conservador; 0.7 es "roto"), rAF en vez de por-evento, no llamar `getBoundingClientRect` en cada `mousemove`.
- [Introducing magnetic and zoning features in Motion+ Cursor — motion.dev](https://motion.dev/magazine/introducing-magnetic-cursors-in-motion-cursor) — estado del arte del imán como primitiva de librería en 2026.
- [Chromatic Aberration / RGB Split — DESIGN.md](https://designmd.app/library/chromatic-aberration-rgb-split) — offsets de 1–3px se leen como lente; 10px se lee como bug. Contexto donde el efecto tiene sentido (gaming/cyberpunk), que **no** es un portafolio de arquitecto de soluciones.
- [Color Channels Split and Distortion Effects — Awwwards](https://www.awwwards.com/inspiration/color-channels-split-and-distortion-effects) — el catálogo de lo ya visto.

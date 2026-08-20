# Scroll 3D & profundidad — estándar 2026 (web-design-pro-2026)

> Estándar pedido por Cristian (2026-07-14): **"que la web se vea más en 3D al hacer scroll"**.
> Este archivo lo aterriza SIN romper Core Web Vitals ni a11y. El efecto 3D-en-scroll es un
> **enhancement**, nunca un requisito para ver el contenido.

Recetas: **propósito 1 línea → código mínimo → "no hagas esto"**. Todo el movimiento vive dentro de
`@media (prefers-reduced-motion: no-preference)` o se neutraliza bajo `reduce`. Complementa
`anti-flat-recipes.md §5` (scroll-driven reveal) — aquí el foco es **profundidad / parallax / perspectiva**.

---

## 0. Regla de oro (leer antes de animar nada)

El objetivo es **profundidad percibida barata**, no un carrusel de efectos. La sensación 3D se logra con
**3 palancas apiladas**, no con WebGL:

1. **Parallax por capas** — fondo/mid/foreground se mueven a distinta velocidad con el scroll.
2. **Perspectiva real** — `perspective` en el contenedor + `translateZ`/`rotateX` en las capas.
3. **Elevación + luz** — sombras en capas y un highlight que sigue el scroll (ya cubierto por el gate anti-flat).

### Cuándo NO hacerlo (honestidad primero)
- **Nunca** en un dashboard de datos, tabla larga, checkout, o form: el movimiento estorba y sube INP.
- **Nunca** si mata el presupuesto: parallax/tilt solo con `transform` y `opacity` (compositor, GPU). Si te
  descubres animando `top/left/width/height/margin` → mal, eso hace layout/paint en cada frame.
- **Nunca** con `scroll` + JS `requestAnimationFrame` recalculando layout (era 2015, OUT). Usar
  `animation-timeline: scroll()/view()` (CSS, off-main-thread) o `transform` puro vía Motion.
- **Presupuesto:** el efecto no puede empujar **INP > 200ms** ni **CLS > 0.1**. Si un hero 3D pesa
  >~300KB de JS o mueve el LCP, se hace lazy post-LCP con poster estático (ver §5).

> Un buen "3D en scroll" es el que el usuario *siente* sin nombrar. Si es evidente y mareante, está mal calibrado.

---

## 1. Parallax por capas — CSS puro, cero JS (`animation-timeline: scroll()`)

**Propósito:** capas a distinta velocidad = profundidad, off-main-thread, sin scroll listeners.
**No es Baseline** (Firefox tras flag hasta ≥152) → `@supports` + fallback estático obligatorio.

```css
.scene { position: relative; overflow: clip; }
/* Estado base SIN scroll-timeline = composición estática legible (fallback) */
.layer { will-change: transform; }

@supports (animation-timeline: scroll()) {
  @media (prefers-reduced-motion: no-preference) {
    .layer--back  { animation: rise linear both; animation-timeline: scroll(root); animation-range: 0 100%; }
    .layer--mid   { animation: rise linear both; animation-timeline: scroll(root); animation-range: 0 100%; }
    .layer--front { animation: rise linear both; animation-timeline: scroll(root); animation-range: 0 100%; }
    /* Distinta magnitud = distinta "profundidad". back se mueve poco, front mucho. */
    .layer--back  { --shift: -4%;  }
    .layer--mid   { --shift: -10%; }
    .layer--front { --shift: -22%; }
  }
}
@keyframes rise { to { transform: translate3d(0, var(--shift, 0), 0); } }
```

> **No hagas esto:** poner el contenido de texto en la capa que más se mueve (se lee mareado). El texto va
> en la capa `mid`/estática; el parallax fuerte es para elementos decorativos (blobs, grano, imágenes de fondo).

---

## 2. Depth stack con perspectiva (`perspective` + `translateZ`)

**Propósito:** que las capas tengan volumen real (no solo desplazamiento) — el hero "respira" hacia el usuario.

```css
.hero-3d {
  perspective: 1000px;            /* cámara: menor = más dramático */
  transform-style: preserve-3d;
}
.hero-3d__plane {
  transform: translateZ(var(--z, 0)) scale(calc(1 + (var(--z, 0) / -1000)));
  /* z negativo empuja hacia el fondo; el scale compensa para que no encoja */
}
.hero-3d__plane--deep { --z: -300px; }   /* fondo lejano, parallax lento */
.hero-3d__plane--near { --z: -60px;  }   /* casi en pantalla */
```

Combínalo con §1: cada `plane` a distinto `--z` **y** distinto `--shift` de scroll → parallax con profundidad real.

> **No hagas esto:** `perspective` sobre un contenedor que scrollea con mucho contenido → jank. Confínalo al
> hero / secciones cortas de exhibición. No apiles >3-4 planos: el costo de composición crece y el efecto se ensucia.

---

## 3. React / Next (stack de Cristian) — Motion `useScroll` + `useTransform`

**Propósito:** parallax/3D scroll-linked cuando ya usas React y quieres control fino. Paquete: **`motion`**
(antes `framer-motion`; mismo código, v12+, importar de `motion/react`). `framer-motion` sigue funcionando idéntico.

```bash
npm i motion            # nombre actual. (npm i framer-motion también sirve, mismo build)
```

```tsx
"use client";
import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";

export function ParallaxHero() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();                 // a11y: apaga el efecto
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });

  // Capas a distinta velocidad. Si reduce → sin desplazamiento.
  const yBack  = useTransform(scrollYProgress, [0, 1], reduce ? [0, 0] : [0, -60]);
  const yFront = useTransform(scrollYProgress, [0, 1], reduce ? [0, 0] : [0, -180]);
  const rotate = useTransform(scrollYProgress, [0, 1], reduce ? [0, 0] : [8, -8]);

  return (
    <section ref={ref} className="relative overflow-clip [perspective:1000px]">
      <motion.div style={{ y: yBack }}  className="absolute inset-0 will-change-transform">{/* fondo/grain */}</motion.div>
      <motion.div style={{ y: yFront, rotateX: rotate, transformStyle: "preserve-3d" }}
                  className="relative will-change-transform">{/* card/hero visual */}</motion.div>
    </section>
  );
}
```

**Reglas de rendimiento (no negociables):**
- Solo animar `y`, `x`, `scale`, `rotate*`, `opacity` (Motion las manda al compositor). Nunca `width`/`top`.
- `will-change: transform` **solo** en las capas animadas; quitarlo cuando termina si es puntual (no dejar 30 elementos con will-change).
- Un `useScroll` por sección, no uno por elemento. Derivar capas con `useTransform` del mismo progress.
- SSR: el componente es `"use client"` island; el resto de la página server-rendered (no romper el gate SEO/SSR).

---

## 4. Tilt 3D por puntero (cards que reaccionan al mouse)

**Propósito:** micro-profundidad en cards/CTAs sin scroll — el elemento se inclina hacia el cursor.

```tsx
import { motion, useMotionValue, useSpring, useTransform } from "motion/react";
function TiltCard({ children }) {
  const mx = useMotionValue(0), my = useMotionValue(0);
  const rx = useSpring(useTransform(my, [-0.5, 0.5], [8, -8]), { stiffness: 200, damping: 20 });
  const ry = useSpring(useTransform(mx, [-0.5, 0.5], [-8, 8]), { stiffness: 200, damping: 20 });
  return (
    <motion.div
      onPointerMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        mx.set((e.clientX - r.left) / r.width - 0.5);
        my.set((e.clientY - r.top) / r.height - 0.5);
      }}
      onPointerLeave={() => { mx.set(0); my.set(0); }}
      style={{ rotateX: rx, rotateY: ry, transformStyle: "preserve-3d" }}
      className="[perspective:800px] will-change-transform"
    >{children}</motion.div>
  );
}
```

> **No hagas esto:** tilt en **cada** card de una grilla de 20 (ruido + costo puntero). Reservar para hero card,
> pricing destacado, CTA. En touch no hay hover → el efecto simplemente no aplica (no forzarlo con toques).

---

## 5. Hero WebGL / Spline / Three (solo si la marca *es* la experiencia)

Techo de gama, pero **caro**: 800KB–2MB de runtime. Reglas:
- **Lazy-init post-LCP**: poster estático (imagen AVIF) como LCP; el canvas monta después con `IntersectionObserver` / `requestIdleCallback`.
- Respeto absoluto a `prefers-reduced-motion` → servir el poster estático, no el canvas.
- Nunca como LCP element. Nunca sin fallback en móvil de gama baja (detectar `deviceMemory`/`hardwareConcurrency` bajo → poster).

Si el 3D no es el core de la marca, **§1–§4 dan el 90% de la sensación al 5% del costo.** Preferirlos.

---

## 6. 21st.dev MCP — fuente de componentes animados (herramienta, no atajo)

Registrado a nivel usuario (`x-api-key`). Úsalo para **descubrir/adaptar** componentes React/Tailwind animados
(heroes, parallax, marquees, cards 3D) en vez de escribir desde cero — **pero pásalos por el gate**:

- Buscar el componente vía las tools `mcp__*21st*` (buscar por keyword: "parallax hero", "3d card", "scroll reveal").
- **Adaptarlo, no pegarlo crudo:** re-tematizar con la paleta del `MASTER.md` de `ui-ux-pro-max` (no colores del snippet),
  envolver todo movimiento en `prefers-reduced-motion`, verificar que solo anima `transform`/`opacity`, y que no
  rompe SSR/SEO (island `"use client"` acotado).
- 21st es **inspiración + arranque**, no autoridad estética. El director sigue siendo `web-design-pro-2026`.

---

## Checklist 3D-scroll (parte del PRE-DELIVERY GATE)

- [ ] El efecto usa **solo** `transform`/`opacity` (compositor). Cero animación de layout (`top/left/width/height`).
- [ ] `animation-timeline` (CSS) bajo `@supports` + fallback estático legible; o Motion `useScroll` en island `"use client"`.
- [ ] **Todo** el movimiento gateado por `prefers-reduced-motion` (`useReducedMotion` o `@media reduce`) → sin efecto = página perfecta igual.
- [ ] Texto legible NO vive en la capa de parallax rápido; el contenido nunca depende del scroll para ser visible.
- [ ] Medido en móvil throttled (Slow 4G + CPU 4×): **INP < 200ms, CLS < 0.1, LCP < 2.5s** se mantienen.
- [ ] `will-change` solo en capas animadas (no rociado por toda la página). WebGL/Spline lazy post-LCP + poster.
- [ ] Verificado **mirando el render** (`/gstack-qa` o browser preview), no solo "compila".

---

## 7. Gotchas de producción (hard-won — 2026-07-14, taller-ejemplo + portafolio)

Un efecto scroll que "compila" y aplica el transform **en reposo** puede NO dispararse al scrollear. Verificar SIEMPRE que el transform **cambia con el scroll**, no solo que existe.

1. **CSP sin `'unsafe-eval'` rompe la hidratación en DEV (Next).** El Fast Refresh (`react-refresh`) evalúa strings → con CSP estricta, React no hidrata → **NINGÚN** efecto (framer-motion, listeners) corre, y parece que "no se ve nada". Hacer la CSP condicional: `unsafe-eval` solo en dev, prod estricto. Ver [[feedback-nextjs-csp-dev-hydration]].
2. **framer-motion `useScroll({ target })` puede quedarse en `scrollYProgress = 0`** (no actualiza su medición en ciertos layouts) → parallax muerto. Fix robusto: **driver de scroll manual** — `useEffect` con listener `scroll` (passive) + `rAF` que setea un `useMotionValue` desde `getBoundingClientRect().top`. Bulletproof y verificable.
3. **GSAP ScrollTrigger mide `start/end` demasiado pronto** → se queda en el estado inicial (`gsap.from`) y no avanza. Causas: overlay de intro que **bloquea el scroll** al montar, e imágenes que cargan async cambiando alturas. Fix: `ScrollTrigger.refresh()` en `load`, en el **primer scroll** (`{once:true}`) y con reintentos `setTimeout` (400/1200/2500ms). Un solo refresh en el setup NO basta.
4. **`requestAnimationFrame` se PAUSA en pestañas en segundo plano** → el efecto no corre ahí y no se puede medir. Para verificar: pestaña en **foco** (click antes), y medir con `getComputedStyle(el).transform` (sincrónico) tras scrollear; `await`+rAF puede colgar el CDP en pestañas sin foco.
5. **Efecto scroll-only = invisible en reposo.** Si el usuario no scrollea, no ve nada. Si se quiere señal en reposo, añadir tilt de puntero o un micro-movimiento; y comunicar "baja para verlo".
6. **`iframe` + ancestro con transform 3D parpadea** en algunos navegadores. Excluir secciones con `<iframe>` (mapas) del `rotateX`/`scale` → darles solo `y`/opacity.

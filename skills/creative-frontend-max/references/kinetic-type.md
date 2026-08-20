# Kinetic type — tipografía que deslumbra desde el primer frame

**Stack asumido:** Next.js 14.2 App Router · React 18.3 · TS · `gsap@3.15` + `@gsap/react` ·
`lenis` · `framer-motion@11` · R3F v8 / drei v9 (React 18 → **nunca** v9/v10) ·
**CSP estricta: cero CDN en runtime** · LCP < 2.5s · INP < 200ms · CLS < 0.1.

El hero es el 80% de la primera impresión y cuesta **~0 KB de JS**. Antes de tocar un shader,
se arregla la tipografía. Un canvas WebGL espectacular detrás de un H1 de 61px en Inter sigue
leyéndose como plantilla.

---

## 0. Corrección de premisa (antes de nada)

> **"El SplitText de GSAP es de pago" — FALSO desde GSAP 3.13 (2025).**
> Webflow liberó todo el Club GreenSock. Verificado en este repo:
> `node_modules/gsap/SplitText.js` existe en `gsap@3.15.0`, con `mask`, `autoSplit`,
> `onSplit`, `smartWrap` y config `aria`. **Ya lo tienes instalado y es gratis.**

Entonces, ¿para qué el splitter propio de la §2?

| | GSAP `SplitText` | Splitter propio (§2) |
|---|---|---|
| Coste | ~11 KB min | 0 KB nuevos |
| Líneas reales | sí (`type:"lines"`) | sí |
| `mask:"lines"` automático | sí | manual (3 líneas de CSS) |
| Re-split en resize/fuente | `autoSplit:true` | tu hook |
| Control del DOM generado | opaco | **total** (clases, `aria`, `data-*`, wrappers) |
| Auditable / sin plugin registrado | no | **sí** |
| Cuándo usarlo | 90% de los casos: **úsalo** | cuando el reveal necesita DOM que SplitText no produce (weaving, per-línea con dos capas, `data-index` para shaders) |

**Recomendación honesta: usa `SplitText` (§2.1) para el trabajo normal.** El splitter propio
(§2.2) está aquí porque en este portafolio el titular se pinta **dos veces** (weaving 3D, §4) y
ahí necesitas control absoluto de qué copia lleva el `<h1>` y cuál va `aria-hidden`. Un plugin
que reescribe el DOM por debajo pelea con eso.

---

## 1. El titular colosal — por qué el TAMAÑO es la emoción

### 1.1 El mecanismo (no es "poner la fuente grande")

Keltner & Haidt (2003) definen el *awe* con dos componentes: **vastness percibida** +
**need for accommodation** (el esquema mental no alcanza y hay que reajustarlo). Traducido a
una página — y esto es **heurística de dirección de arte, no un resultado medido**:

- **Vastness = el titular no cabe en el marco.** Lo que produce la sensación no es "230px",
  es que **el viewport lo corta**. Un titular que cabe holgadamente es un titular; uno que
  sangra por los bordes es un objeto que *no puedes abarcar*. Esa es toda la diferencia.
- **Accommodation = contraste de escala violento.** Si el ojo va de 11px (eyebrow) a 230px (H1)
  sin escalones intermedios, tiene que reajustar. Escalas "bonitas" con 8 pasos suaves (16→20→24→
  32→40→48→64) se leen como Bootstrap. **Heurística: ratio ≥ 15:1 entre el texto más pequeño y
  el más grande de la primera pantalla, y como mucho 3 tamaños en el hero.**

En `portafolio-frontend` hoy: eyebrow `clamp(0.6rem, .85vw, .72rem)` ≈ 11px y H1
`clamp(2.8rem, 12.6vw, 13rem)` ≈ 208px @1600 → ratio ≈ 19:1. **Eso está bien.** El problema del
hero no es la escala; es el resto (§6).

### 1.2 La matemática real del `clamp()` (deja de tantear el `vw`)

Para que la fuente valga `min` px a `Vmin` px de viewport y `max` px a `Vmax` px:

```
slope = (max - min) / (Vmax - Vmin)          // px por px
vwTerm = slope * 100                          // el número que va en vw
remTerm = (min - slope * Vmin) / 16           // el intercepto, en rem

font-size: clamp( min/16 rem , remTerm rem + vwTerm vw , max/16 rem );
```

**Ejemplo trabajado** — 44px @360 → 232px @1600:

```
slope   = (232 - 44) / (1600 - 360) = 188 / 1240 = 0.15161
vwTerm  = 15.16vw
remTerm = (44 - 0.15161 * 360) / 16 = (44 - 54.58) / 16 = -0.661rem
```

```css
font-size: clamp(2.75rem, -0.66rem + 15.16vw, 14.5rem);
/* check @360:  -10.58 + 54.58 = 44px  ✓
   check @1600: -10.58 + 242.6 = 232px ✓ */
```

**El término `rem` negativo:** es correcto (es el intercepto que hace pasar la recta por tus dos
puntos) pero **invierte la respuesta al ajuste de tamaño de fuente del usuario**: si sube el
tamaño base del navegador, el titular *encoge* un pelín. En un display de 230px eso es
irrelevante (es una imagen, no lectura). **En body copy es una regresión de a11y — ahí el
término rem tiene que ser positivo.** Regla:

- **Display / H1 colosal:** slope agresivo, rem negativo permitido.
- **Body / UI:** `clamp(1rem, 0.94rem + 0.3vw, 1.125rem)` — rem siempre positivo y dominante.

### 1.3 `vw` te va a meter scroll horizontal — usa `cqw`

`100vw` **incluye el ancho de la barra de scroll** en desktop. Un titular con
`white-space: nowrap` dimensionado en `vw` desborda por 15px y aparece scroll horizontal (y con
él, un `overflow-x:hidden` de emergencia que **rompe `position:sticky`** — ver
`[[reference-3d-scroll-r3f-blender]]`). La solución no es el hack, es medir contra el contenedor:

```css
.hero-title-inner {
  container-type: inline-size;   /* ← habilita cqw */
  max-width: 1500px;
  margin-inline: auto;
  padding-inline: clamp(1.25rem, 4vw, 3.5rem);
}

.ht-line {
  /* cqw = 1% del ancho DEL CONTENEDOR (ya sin barra de scroll y ya sin padding) */
  font-size: clamp(2.75rem, -0.66rem + 15.2cqw, 14.5rem);
}
```

Con `container-type: inline-size` el contenedor ya no puede depender del alto de sus hijos —
irrelevante aquí porque el layer tiene `height: 100vh` fijo. Verifica que no rompa el flex.

### 1.4 Fuente variable, self-hosted, CSP-safe

**`next/font/google` NO es una petición a un CDN.** Descarga el `.woff2` **en tiempo de build**
y lo sirve desde `/_next/static/media/*`. Con `font-src 'self'` funciona. La CSP estricta **no
es motivo para renunciar a Google Fonts** — solo lo es para el `<link>` a `fonts.googleapis.com`.

```ts
// src/app/[locale]/layout.tsx
import { Archivo } from "next/font/google";

const display = Archivo({
  subsets: ["latin"],
  // Sin `weight`: next/font pide la VARIABLE completa (wght 100–900).
  // Fijar weight:"900" te trae un archivo estático y pierdes la interpolación.
  axes: ["wdth"],            // Archivo trae eje de anchura además del peso.
  variable: "--font-display",
  display: "swap",
  preload: true,
  adjustFontFallback: true,  // default; NO lo apagues (ver abajo)
});
```

> **Verificación gratis:** si el eje no existe, `next build` **falla listando los ejes válidos**.
> Es la forma más barata de comprobar qué expone una variable font. Los rangos cambian entre
> versiones de la fuente — no los memorices, deja que el build te lo diga.

**`adjustFontFallback` es lo que te salva el CLS.** Con `display:swap`, el primer paint usa la
fallback y el swap re-pinta. En un H1 de 230px, una diferencia de métricas del 3% mueve
**7px de altura de línea** → CLS instantáneo. next/font genera un `@font-face` de fallback con
`size-adjust`/`ascent-override` calculados para que ocupe **exactamente lo mismo**. Apagarlo es
regalar el CLS.

**Si prefieres no depender de Google ni en build** (todo local, cero red):

```ts
import localFont from "next/font/local";

const display = localFont({
  src: [{ path: "./fonts/Archivo-Variable.woff2", weight: "100 900", style: "normal" }],
  variable: "--font-display",
  display: "swap",
  preload: true,
  adjustFontFallback: "Arial",   // el fallback contra el que se calculan las métricas
});
```
Descarga el `.woff2` variable (OFL) una vez y lo commiteas. Subconjunta con `pyftsubset`/`glyphhanger`
si quieres bajar de ~40KB → ~18KB (latin básico).

**Caras display gratis (OFL) con opinión** — todas self-hosteables:

| Fuente | Carácter | Ejes (verifica en build) | Para qué |
|---|---|---|---|
| **Archivo** | grotesca americana, sólida | `wght`, `wdth` | la que ya usas. Correcta, no espectacular. |
| **Bricolage Grotesque** | editorial, imperfecta a propósito | `wght`, `wdth`, `opsz` | "diseñado por un humano" |
| **Big Shoulders Display** | condensada extrema | `wght` | titular colosal de 3 líneas apiladas |
| **Anton** | peso máximo, estática | — | brutal, cero matices |
| **Instrument Serif** | serif de alto contraste | — | kicker/eyebrow **elegante** en contraste con la grotesca |
| **Bodoni Moda** | didone, contraste altísimo | `opsz` | si "elegante" es literalmente lo que pide |
| **Fraunces** | serif con carácter (`SOFT`, `WONK`) | `wght`, `opsz`, `SOFT`, `WONK` | personalidad sin ser payasa |

**El truco de "elegante" que Cristian ve en otras webs casi siempre es un par**: grotesca
condensada pesada para el titular + **serif de alto contraste** para el eyebrow/kicker/número.
No es una fuente mejor: es el **contraste** entre dos.

### 1.5 Ajuste óptico — lo que separa "diseñado" de "generado"

```css
.ht-line {
  font-family: var(--font-display), system-ui, sans-serif;

  /* PESO Y ANCHURA ÓPTICOS: a 230px se va MÁS ANCHO y MÁS PESADO de lo que crees,
     porque el ojo compensa. A 16px, lo contrario. */
  font-variation-settings: "wght" 880, "wdth" 108;
  font-optical-sizing: auto;

  /* TRACKING NEGATIVO — la regla de verdad: el tracking es función del tamaño.
     16px → 0em. 48px → -0.02em. 120px → -0.035em. 230px → -0.045…-0.055em.
     Si dejas 0 en un titular colosal, los huecos entre letras se vuelven agujeros. */
  letter-spacing: -0.048em;

  /* LEADING SUB-1: dos líneas de 230px con line-height 1.2 dejan un canal de aire
     que rompe la masa. En display se va POR DEBAJO de 1. */
  line-height: 0.84;

  text-transform: uppercase;
  white-space: nowrap;   /* el titular es un objeto, no un párrafo */
}
```

**Alineación óptica (esto casi nadie lo hace, y es exactamente lo que se nota):** una línea que
empieza con glifo redondo (`C`, `O`, `G`, `Q`, `S`) o diagonal (`A`, `V`, `W`, `Y`) se ve
**metida hacia dentro** aunque su caja esté perfectamente alineada. A 230px el defecto es
brutalmente visible.

```css
/* Cuelga el glifo redondo fuera del margen. Es el "optical margin alignment" de InDesign,
   a mano. Valores: redondos -0.02em, diagonales -0.03em, T/Y -0.04em, comillas -0.05em. */
.ht-line[data-optical="round"]    { margin-left: -0.020em; }
.ht-line[data-optical="diagonal"] { margin-left: -0.030em; }
```

```tsx
const OPTICAL = /^[COGQSJU]/i;   // redondos
const DIAG    = /^[AVWXYT]/i;    // diagonales
const optical = (s: string) => OPTICAL.test(s) ? "round" : DIAG.test(s) ? "diagonal" : undefined;
// <span className="ht-line" data-optical={optical(line)}>
```

En este repo: `CRISTIAN` empieza por **C** (redondo) y `GUTIÉRREZ` por **G** (redondo). Hoy
ambas están alineadas por caja → las dos se ven metidas ~4px respecto al eyebrow y al bloque
inferior. **Ese es el tipo de defecto que hace que se vea "casi bien" sin saber por qué.**

**Recorte de caja (2026):** el espacio muerto sobre las mayúsculas y bajo la baseline hace
imposible alinear el titular con nada. `text-box` (Chrome 133+, 2025) lo resuelve:

```css
@supports (text-box: trim-both cap alphabetic) {
  .ht-line { text-box: trim-both cap alphabetic; }  /* la caja == cap-height..baseline */
}
```
Progresivo: donde no exista, sigues con el hack de `padding`/`margin` negativos.

### 1.6 `text-wrap: balance` / `pretty` — veredicto honesto

| Valor | Dónde SÍ | Dónde NO |
|---|---|---|
| `balance` | headings de sección, kickers, CTAs de 2–3 líneas | **el H1 colosal**: es `white-space:nowrap` → **`balance` se ignora**. Chromium además lo limita a ~6 líneas por coste. |
| `pretty` | **body copy** (`.hero-bio`, párrafos de About) — mata huérfanas | headings (para eso está `balance`) |

```css
.section-title, .hero-eyebrow { text-wrap: balance; }
.hero-bio, p                  { text-wrap: pretty; }
```
Degrada a `normal` solo donde no hay soporte. Coste 0. Ponlo y olvídate.
**No lo vendas como "el fix del hero": no toca el titular colosal en absoluto.**

---

## 2. Split text

### 2.1 Con `SplitText` de GSAP (gratis, ya instalado) — usa esto por defecto

```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { SplitText } from "gsap/SplitText";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(SplitText, useGSAP);

export function RevealHeading({ children }: { children: string }) {
  const ref = useRef<HTMLHeadingElement>(null);

  useGSAP(() => {
    const split = SplitText.create(ref.current, {
      type: "lines",
      mask: "lines",        // crea el wrapper overflow:hidden por línea. Es la clave del efecto.
      linesClass: "st-line",
      autoSplit: true,      // re-split al cambiar el ancho o al cargar la fuente. Imprescindible.
      aria: "auto",         // aria-label en el padre + aria-hidden en los trozos.
      onSplit: (self) =>
        gsap.from(self.lines, {
          yPercent: 110,
          duration: 1.15,
          ease: "expo.out",
          stagger: 0.09,
        }),
    });
    return () => split.revert();
  }, { scope: ref });

  return <h2 ref={ref}>{children}</h2>;
}
```

`onSplit` devuelve el tween → con `autoSplit` GSAP lo mata y lo recrea limpio en cada re-split.
Sin `autoSplit`, al girar el móvil las líneas quedan partidas donde ya no van.

**Lo que `aria:"auto"` hace y por qué importa:** al trocear, el texto real deja de existir como
un nodo coherente; un lector de pantalla leería "C-R-I-S-T-I-A-N" letra a letra. `aria:"auto"`
pone `aria-label` con el texto original en el contenedor y `aria-hidden="true"` en cada trozo.
**Verifica igual con un lector real** — el plugin puede no cubrir tu wrapper custom.

### 2.2 Splitter propio, 0 KB, control total

`src/lib/split-text.ts`:

```ts
/**
 * Splitter de texto sin dependencias.
 *
 * INVARIANTE DE ACCESIBILIDAD:
 *   - el texto original vuelve como aria-label del contenedor
 *   - TODO lo generado va aria-hidden="true"
 *   → el lector de pantalla lee la frase; el DOM visual son cajas decorativas.
 *
 * INVARIANTE DE LÍNEAS:
 *   las líneas NO existen hasta que el layout corre CON LA FUENTE REAL.
 *   Partir antes de document.fonts.ready agrupa con las métricas de la fallback
 *   → los cortes quedan en sitios que no existen. Ver useSplitText.
 */
export type SplitResult = {
  chars: HTMLElement[];
  words: HTMLElement[];
  lines: HTMLElement[];
  revert: () => void;
};

export type SplitOpts = {
  chars?: boolean;   // trocear también por carácter
  lines?: boolean;   // agrupar en líneas reales (requiere layout)
  mask?: boolean;    // envolver cada línea en un contenedor overflow:hidden
};

// Intl.Segmenter parte por GRAFEMA: "ñ", "é", emoji y ligaduras se mantienen enteros.
// Array.from() rompe emojis compuestos; [...str] también. Este es el único camino correcto.
const SEG =
  typeof Intl !== "undefined" && "Segmenter" in Intl
    ? new Intl.Segmenter(undefined, { granularity: "grapheme" })
    : null;

const graphemes = (s: string): string[] =>
  SEG ? Array.from(SEG.segment(s), (g) => g.segment) : Array.from(s);

export function splitText(el: HTMLElement, opts: SplitOpts = {}): SplitResult {
  const original = el.innerHTML;
  const prevLabel = el.getAttribute("aria-label");
  const text = (el.textContent ?? "").replace(/\s+/g, " ").trim();

  el.setAttribute("aria-label", text);

  // ── 1. PALABRAS (+ caracteres) ───────────────────────────────────────────
  const words: HTMLElement[] = [];
  const chars: HTMLElement[] = [];
  const frag = document.createDocumentFragment();
  const parts = text.split(" ");

  parts.forEach((w, i) => {
    const word = document.createElement("span");
    word.className = "st-word";
    word.setAttribute("aria-hidden", "true");
    // inline-block: sin esto, transform/yPercent NO aplica a un span inline.
    word.style.display = "inline-block";
    // nowrap: una palabra troceada en chars se partiría por la mitad al final de línea.
    word.style.whiteSpace = "nowrap";

    if (opts.chars) {
      graphemes(w).forEach((g, ci) => {
        const c = document.createElement("span");
        c.className = "st-char";
        c.setAttribute("aria-hidden", "true");
        c.style.display = "inline-block";
        c.dataset.i = String(chars.length);   // índice global → stagger custom, uniforms de shader
        c.dataset.ci = String(ci);
        c.textContent = g;
        chars.push(c);
        word.appendChild(c);
      });
    } else {
      word.textContent = w;
    }

    word.dataset.i = String(i);
    words.push(word);
    frag.appendChild(word);

    // El espacio va como NODO DE TEXTO entre spans. Si lo metes DENTRO del span
    // inline-block, el colapso de espacios se lo come y las palabras se pegan.
    if (i < parts.length - 1) frag.appendChild(document.createTextNode(" "));
  });

  el.textContent = "";
  el.appendChild(frag);

  // ── 2. LÍNEAS — solo se pueden conocer DESPUÉS de este layout ────────────
  const lines: HTMLElement[] = [];
  if (opts.lines) {
    // Agrupar por offsetTop. Tolerancia de 2px: superíndices, tildes altas y
    // subpíxeles hacen que dos palabras de la misma línea difieran en 1px.
    const rows = new Map<number, HTMLElement[]>();
    for (const w of words) {
      const key = Math.round(w.offsetTop / 2) * 2;   // ← lectura de layout: 1 vez, no por frame
      const bucket = rows.get(key);
      if (bucket) bucket.push(w);
      else rows.set(key, [w]);
    }

    const sorted = [...rows.entries()].sort((a, b) => a[0] - b[0]);
    el.textContent = "";   // los spans siguen vivos en `words`; solo los desconectamos

    sorted.forEach(([, ws], li) => {
      const line = document.createElement("span");
      line.className = "st-line";
      line.setAttribute("aria-hidden", "true");
      line.style.display = "block";
      line.dataset.i = String(li);

      ws.forEach((w, i) => {
        line.appendChild(w);
        if (i < ws.length - 1) line.appendChild(document.createTextNode(" "));
      });

      if (opts.mask) {
        const m = document.createElement("span");
        m.className = "st-mask";
        m.setAttribute("aria-hidden", "true");
        m.appendChild(line);
        el.appendChild(m);
      } else {
        el.appendChild(line);
      }
      lines.push(line);
    });
  }

  return {
    chars,
    words,
    lines,
    revert() {
      el.innerHTML = original;
      if (prevLabel === null) el.removeAttribute("aria-label");
      else el.setAttribute("aria-label", prevLabel);
    },
  };
}
```

CSS que acompaña (esto es todo):

```css
.st-mask {
  display: block;
  overflow: hidden;
  /* EL BUG DE LOS DESCENDENTES: overflow:hidden corta la panza de g/j/p/y/Q
     y la coma. Se le da aire a la máscara y se recupera con margen negativo,
     así el layout NO se mueve. Sin esto, "GUTIÉRREZ" pierde la cola de la Q. */
  padding-bottom: 0.14em;
  margin-bottom: -0.14em;
}
.st-line { display: block; will-change: transform; }
.st-word,
.st-char { display: inline-block; }

@media (prefers-reduced-motion: reduce) {
  .st-line, .st-word, .st-char { transform: none !important; opacity: 1 !important; }
}
```

Hook `src/hooks/useSplitText.ts`:

```tsx
"use client";
import { useLayoutEffect, useRef, type RefObject } from "react";
import { splitText, type SplitResult, type SplitOpts } from "@/lib/split-text";

export function useSplitText(
  ref: RefObject<HTMLElement>,
  onSplit: (r: SplitResult) => (() => void) | void,
  opts: SplitOpts = { lines: true, mask: true },
) {
  const cb = useRef(onSplit);
  cb.current = onSplit;
  const optsRef = useRef(opts);   // congelado: cambiar opts NO debe re-partir

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;

    let split: SplitResult | null = null;
    let cleanup: (() => void) | void;
    let width = window.innerWidth;
    let alive = true;
    let t = 0;

    const run = () => {
      if (!alive) return;
      cleanup?.();
      split?.revert();
      split = splitText(el, optsRef.current);
      cleanup = cb.current(split);
    };

    // Partir SOLO cuando la fuente real está aplicada. Con la fallback,
    // "Solutions Architect & Senior Full-Stack" puede caer en 2 líneas y con
    // Archivo en 3 → los cortes quedarían mal para siempre.
    document.fonts.ready.then(run);

    // Re-split SOLO si cambia el ANCHO. En Android, la barra de URL al scrollear
    // dispara resize por ALTO decenas de veces → re-partir ahí es jank garantizado.
    const onResize = () => {
      if (window.innerWidth === width) return;
      width = window.innerWidth;
      clearTimeout(t);
      t = window.setTimeout(run, 150);   // debounce: el drag de la ventana dispara ~60/s
    };
    window.addEventListener("resize", onResize);

    return () => {
      alive = false;
      clearTimeout(t);
      window.removeEventListener("resize", onResize);
      cleanup?.();
      split?.revert();
    };
  }, [ref]);
}
```

---

## 3. Reveal por líneas — el que se lee caro

### 3.1 La decisión técnica: máscara + `transform`, NO `opacity`

| Técnica | Se lee como | Coste GPU |
|---|---|---|
| `opacity: 0 → 1` | **AI slop.** Es el default de AOS/framer `whileInView`. El ojo lo tiene visto. | compositor |
| `y: 40px` + fade | genérico premium 2021 | compositor |
| **máscara + `yPercent: 110 → 0`** | **caro.** La línea *sale de detrás de algo*, es física. | **compositor puro** |
| `clip-path: inset()` animado | wipe (otra cosa, ver §3.3) | **paint por frame** |
| `filter: blur()` animado | bonito en Figma, **mata el frame** en un H1 de 230px | no lo hagas |

**La máscara gana por dos razones a la vez:** es la única que se lee como material (una persiana,
no un fantasma) **y** es 100% compositor (`transform` sobre una capa promovida, cero paint).
No hay trade-off que negociar.

### 3.2 Números concretos que funcionan

**Easings.** Una sola familia en toda la página. Elegir UNA y no mezclar.

| Nombre | `cubic-bezier` | GSAP | Uso |
|---|---|---|---|
| **expo.out** | `cubic-bezier(0.16, 1, 0.30, 1)` | `"expo.out"` | **el "caro".** Arranca disparado, aterriza sin rebote. Reveal de hero. |
| power4.out | `cubic-bezier(0.19, 1, 0.22, 1)` | `"power4.out"` | idem, un pelo menos violento. Lo que ya usa el repo. |
| quint.out | `cubic-bezier(0.22, 1, 0.36, 1)` | `"power4.out"` | UI, cards, hover |
| quart.inOut | `cubic-bezier(0.76, 0, 0.24, 1)` | `"power4.inOut"` | **cortinas y wipes** (entra y sale) |
| back.out(1.4) | — | `"back.out(1.4)"` | **prohibido en tipografía display.** El rebote infantiliza 230px. |

**Duraciones.** Escalera de 3, no más:

```
micro (hover, focus, botón)          0.18 – 0.25 s
UI    (card, modal, nav)             0.55 – 0.70 s
hero  (líneas del titular)           1.05 – 1.25 s   ← el "lento caro"
cortina (preloader)                  0.90 s in / 1.10 s out
```

**Stagger.** La regla dura:

> **`duración > stagger_total`.** Si la última línea empieza cuando la primera ya acabó, no es
> un gesto: es una **cola**. Y una cola se lee como plantilla.

```
líneas   0.08 – 0.12 s      (2 líneas → 0.09 ✔)
palabras 0.03 – 0.05 s
chars    each = min(0.02, 0.45 / N)     ← tope de 0.45s de stagger TOTAL
```
Con 40 caracteres y `stagger: 0.03` acumulas **1.2s** solo de retardo. El visitante ve el texto
aparecer letra a letra como una máquina de escribir de 2012. `0.45/40 = 0.011s` → se lee como
**una ola**, que es lo que quieres.

**Overshoot.** `yPercent: 110`, no `100`. Con exactamente 100 la línea arranca justo en el borde
y los descendentes asoman un pixel antes de tiempo. 110–120 la esconde de verdad.

### 3.3 Código — reveal por máscara (el default)

```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { useSplitText } from "@/hooks/useSplitText";

export function LineReveal({ children }: { children: string }) {
  const ref = useRef<HTMLParagraphElement>(null);

  useSplitText(ref, (split) => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const tween = gsap.from(split.lines, {
      yPercent: 112,
      duration: 1.15,
      ease: "expo.out",
      stagger: 0.09,
      scrollTrigger: { trigger: ref.current, start: "top 82%", once: true },
    });
    return () => { tween.scrollTrigger?.kill(); tween.kill(); };
  });

  return <p ref={ref} className="line-reveal">{children}</p>;
}
```

`start: "top 82%"` — no `"top 80%"` por superstición: **82% es donde el elemento está
suficientemente dentro para que el reveal termine antes de que el ojo llegue.** `once: true`
porque un reveal que se repite al subir es un tic nervioso, no una decisión.

### 3.4 El wipe con `clip-path` (cuando quieres que NO se mueva)

Hay un caso donde `transform` no sirve: cuando el texto debe **aparecer sin desplazarse** (un
titular que ya está en su sitio y se "revela"). Ahí sí `clip-path`, con `@property` para poder
interpolar una custom property:

```css
@property --wipe {
  syntax: "<percentage>";
  inherits: false;
  initial-value: 100%;
}

.wipe {
  /* aire para los descendentes: el clip corta la caja, no la tinta */
  padding-bottom: 0.14em;
  margin-bottom: -0.14em;
  clip-path: inset(0 0 var(--wipe) 0);
  transition: --wipe 1.05s cubic-bezier(0.16, 1, 0.30, 1);
}
.wipe.is-in { --wipe: 0%; }
```

Y la versión **con borde suave** (la que de verdad se ve cara — el corte duro delata la técnica):

```css
@property --p {
  syntax: "<percentage>";
  inherits: false;
  initial-value: 0%;
}

.soft-wipe {
  -webkit-mask-image: linear-gradient(100deg,
      #000 calc(var(--p) - 14%), transparent calc(var(--p) + 3%));
          mask-image: linear-gradient(100deg,
      #000 calc(var(--p) - 14%), transparent calc(var(--p) + 3%));
  -webkit-mask-repeat: no-repeat;  mask-repeat: no-repeat;
  -webkit-mask-size: 100% 100%;    mask-size: 100% 100%;
  transition: --p 1.2s cubic-bezier(0.16, 1, 0.30, 1);
}
.soft-wipe.is-in { --p: 118%; }
```
El gradiente a `100deg` hace que el barrido entre en diagonal, no en horizontal. Es un detalle de
2 grados y cambia la lectura por completo.

> **Honestidad de rendimiento:** animar `clip-path`/`mask-image` **repinta la capa cada frame**.
> Sobre un H1 de 230px **con `text-shadow` de 160px de blur** (el halo actual del repo) eso es
> caro de verdad en un Android de gama media. **Regla: el hero usa máscara + transform (§3.3).
> El wipe de `clip-path` se reserva para headings de sección, que son pequeños.** Y si lo usas
> en el hero, **quita el `text-shadow` de esa capa mientras dura la animación.**

---

## 4. Weaving 3D ↔ texto — el momento signature

> **El momento, en una frase:** *el laptop atraviesa el nombre — pasa por delante de la mitad
> superior de las letras y por detrás de la mitad inferior.*

### 4.1 La técnica real

No hay forma de que un objeto WebGL se interponga *dentro* del flujo de un `<h1>` del DOM. El
truco es que **hay dos titulares**, uno a cada lado del canvas:

```
z-index 1   →  <div aria-hidden>  copia TRASERA  (sin recortar)   ← el laptop la TAPA
z-index 2   →  <canvas>           R3F, gl={{ alpha:true }}
z-index 3   →  <h1>               copia FRONTAL  recortada por clip-path  ← TAPA al laptop
```

Como las dos copias son **idénticas al píxel**, el corte es invisible: donde el objeto no está,
ves letra (venga de la capa que venga). Donde el objeto sí está, arriba lo ves a él (tapa a la
trasera) y abajo ves la letra (la frontal lo tapa a él). **El objeto queda cosido a la palabra.**

Ya está implementado en `portafolio-frontend`
(`src/components/portfolio/HeroTitle.tsx` + `globals.css`). Lo que sigue son los **tres defectos
que tiene hoy** y el upgrade.

### 4.2 BUG REAL EN EL REPO — el corte se ve

`src/app/globals.css`:

```css
/* línea ~768 */
.ht-line { color: #F2F2F2; }                       /* ← la capa TRASERA pinta gris plano */

/* línea ~789 */
.hero-title-front .ht-line {                       /* ← la FRONTAL pinta un DEGRADADO */
  background: linear-gradient(180deg, #F2F2F2 0%, var(--color-primary) 130%);
  -webkit-background-clip: text; background-clip: text;
  color: transparent;
}
```

Las dos copias **NO pintan igual**. En `y = 57%` (la línea del `clip-path: inset(57% 0 0 0)`) la
trasera vale `#F2F2F2` y la frontal ya va ~44% hacia el índigo. **Resultado: un escalón de color
horizontal recto que atraviesa las letras, visible en todo el ancho donde el laptop no está.**
El efecto se autodelata: en vez de "un objeto pasa entre las letras" se lee "alguien recortó el
texto con una regla".

**Fix — regla no negociable: las dos capas pintan EXACTAMENTE lo mismo. La única diferencia
permitida es el `z-index`.** Si quieres el degradado, va en las dos:

```css
/* El degradado se aplica en .ht-line (misma geometría en ambas capas)
   → resuelve contra la misma caja → es idéntico. El corte desaparece. */
.ht-line {
  background: linear-gradient(180deg, #F2F2F2 0%, var(--color-primary) 118%);
  -webkit-background-clip: text;
          background-clip: text;
  color: transparent;
}
/* El halo sí puede vivir SOLO en la trasera: se pinta FUERA del glifo, así que
   la capa frontal no lo recorta y queda continuo. */
.hero-title-back .ht-line {
  text-shadow: 0 0 160px color-mix(in srgb, var(--color-primary) 26%, transparent);
}
```

**Cómo verificarlo en 5 segundos sin 3D:** oculta el canvas (`display:none`). Si sigues viendo el
titular **exactamente como si fuera uno solo**, las capas casan. Si ves una línea, tienes el bug.
Este test debería ser un check fijo de QA del hero.

### 4.3 Upgrade — que el corte SIGA al objeto (no un 57% fijo)

Un `inset(57%)` fijo funciona solo si el laptop está siempre a la misma altura. En cuanto viaja
por la página (que es justo lo que hace este proyecto vía `scrollStore`), la costura y el objeto
se separan y el efecto se rompe. La solución: **proyectar la posición del objeto 3D a píxeles de
pantalla y escribir esa Y en una custom property, desde `useFrame`, sin `setState`.**

```tsx
// src/components/three/WeaveDriver.tsx   — va DENTRO del <Canvas>
"use client";
import { useRef, type RefObject } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

const v = new THREE.Vector3();

/**
 * Escribe en :root la Y (px, espacio de PÁGINA) por donde el objeto 3D cruza el titular.
 * El CSS la consume en el clip-path de la capa frontal → la costura persigue al laptop.
 *
 * CERO setState: un setState por frame es un fallo de INP garantizado (REGLA del budget).
 */
export function WeaveDriver({
  target,
  offsetY = 0,          // desplaza la costura respecto al centro del objeto (en px)
}: {
  target: RefObject<THREE.Object3D | null>;
  offsetY?: number;
}) {
  const { camera, size } = useThree();
  const last = useRef(-1);

  useFrame(() => {
    const o = target.current;
    if (!o) return;

    o.getWorldPosition(v);
    v.project(camera);                                   // → NDC (-1..1)
    const vpY = (1 - (v.y * 0.5 + 0.5)) * size.height;   // → px desde el borde superior del VIEWPORT

    // El canvas es `fixed` (viewport) y la capa del titular es `absolute` en el tope de la
    // página. Solo coinciden mientras scrollY < 100vh — es decir, exactamente durante el hero.
    // Conversión viewport → página:
    const pageY = vpY + window.scrollY + offsetY;

    // Escribir en el CSSOM cada frame provoca recálculo de estilo. Con umbral de 0.5px,
    // ~80% de los frames no escriben nada y el coste se evapora. Medido: <0.1ms cuando escribe.
    if (Math.abs(pageY - last.current) < 0.5) return;
    last.current = pageY;
    document.documentElement.style.setProperty("--weave-y", `${pageY.toFixed(1)}px`);
  });

  return null;
}
```

```css
.hero-title-front {
  z-index: 3;
  --weave-y: 57vh;                              /* valor por defecto = lo que hay hoy */
  -webkit-clip-path: inset(var(--weave-y) 0 0 0);
          clip-path: inset(var(--weave-y) 0 0 0);
  /* NO pongas transition aquí: la variable ya se actualiza a 60fps.
     Un transition encima añade lag y hace que la costura ARRASTRE tras el objeto. */
}

/* Reduced motion: el laptop se congela → la costura debe congelarse también, no saltar. */
@media (prefers-reduced-motion: reduce) {
  .hero-title-front { --weave-y: 57vh !important; }
}
```

Uso:

```tsx
const laptop = useRef<THREE.Group>(null);
// ...
<Canvas gl={{ alpha: true }} /* SIN <color attach="background"> o tapas la capa trasera */>
  <group ref={laptop}> <LaptopGLB /> </group>
  <WeaveDriver target={laptop} offsetY={40} />
</Canvas>
```

### 4.4 Las cinco trampas del weaving

1. **El canvas no puede tener fondo.** `gl={{ alpha: true }}` y **nada** de
   `<color attach="background" .../>` ni `scene.background`. Un solo píxel opaco y la capa
   trasera desaparece — con ella, todo el efecto.
2. **Las dos copias tienen que ser idénticas al píxel.** Mismo `font-size` (misma clamp, mismo
   contenedor → **mismo `cqw`**, ojo con `container-type` en solo una de las dos), mismo padding,
   mismo `max-width`, misma familia. Cualquier diferencia = doble visión fantasma.
3. **Solo UNA copia lleva el `<h1>`.** La otra va `aria-hidden="true"` y **sin heading**. Dos
   `<h1>` con el mismo texto es un defecto de SEO y de a11y. El repo lo hace bien hoy: el `<h1>`
   está en la frontal (recortada por `clip-path`, que **no** la saca del árbol de accesibilidad
   ni del crawler — es puramente visual). Correcto.
4. **El objeto tiene que solapar de verdad.** Si el laptop es pequeño o está lejos, la costura no
   se lee. **Heurística: el objeto debe cubrir ≥25% de la banda de cap-height del titular.** Si
   no, no hay weaving; hay un objeto que pasa por ahí.
5. **`will-change` en la capa recortada, no en las dos.** Promover ambas duplica la memoria de
   textura de un elemento de 100vw×100vh. Solo la que se anima.

**Alternativa rechazada:** meter el texto DENTRO de la escena 3D (`troika-three-text` o
`<Text>` de drei) para que la profundidad la resuelva el z-buffer. Técnicamente más "puro" y
**peor en todo lo que importa**: pierdes el `<h1>` real (adiós SEO/LCP/a11y — el texto pasa a ser
píxeles), pagas una dep nueva, el antialiasing de tipografía en WebGL es inferior al del sistema,
y necesitas cargar el `.woff` como recurso de la escena. **No lo hagas.** El truco de las dos
capas es gratis, accesible, y visualmente indistinguible.

---

## 5. Tipografía dirigida por scroll

### 5.1 Prerequisito: velocidad de scroll en el store

Dos líneas en `src/components/three/scroll-store.ts` y `SmoothScroll.tsx`:

```ts
export const scrollStore = {
  page: 0,
  showcase: 0,
  velocity: 0,   // ← NUEVO. Lenis la da gratis. Es lo que hace que el motion se sienta VIVO.
};
```
```ts
lenis.on("scroll", (e: { progress: number; velocity: number }) => {
  scrollStore.page = e.progress;
  scrollStore.velocity = e.velocity;      // ← px/frame, con signo (negativo = hacia arriba)
  paint(e.progress);
  ScrollTrigger.update();
});
```
En el fallback nativo (reduced-motion) déjala en `0`. Nada la leerá.

### 5.2 Marquee que reacciona al scroll

Lo que separa un marquee de un banner de rebajas: **acelera con el scroll y cambia de sentido
cuando subes.** Sin eso es decoración; con eso es respuesta.

```tsx
// src/components/ui/Marquee.tsx
"use client";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { scrollStore } from "@/components/three/scroll-store";

export default function Marquee({
  text,
  speed = 60,       // px/s en reposo
  react = 2.5,      // cuánto acelera con la velocidad de scroll
}: { text: string; speed?: number; react?: number }) {
  const track = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = track.current;
    if (!el) return;

    // Reduced motion: el marquee se queda quieto y LEGIBLE. No se oculta.
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const setX = gsap.quickSetter(el, "x", "px");   // escribe transform sin tocar el CSSOM caro

    // El ancho del ciclo (= la mitad, porque hay dos copias) se mide UNA vez.
    // Leer scrollWidth dentro del rAF fuerza reflow en CADA frame → jank garantizado.
    let cycle = 0;
    const measure = () => { cycle = el.scrollWidth / 2; };
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    measure();

    let x = 0;
    let last = performance.now();
    let raf = requestAnimationFrame(function loop(t) {
      const dt = Math.min((t - last) / 1000, 0.05);   // clamp: al volver de una pestaña en
      last = t;                                        // background, el primer dt es enorme

      const v = speed + scrollStore.velocity * react * 60;
      x -= v * dt;

      if (cycle > 0) x = (((x % cycle) + cycle) % cycle) - cycle;   // wrap sin deriva de float
      setX(x);

      raf = requestAnimationFrame(loop);
    });

    return () => { cancelAnimationFrame(raf); ro.disconnect(); };
  }, [speed, react]);

  return (
    // El texto real, una sola vez, para el lector de pantalla.
    <div className="mq" role="marquee" aria-label={text}>
      <div className="mq-track" ref={track} aria-hidden="true">
        <span className="mq-item">{text}</span>
        <span className="mq-item">{text}</span>
      </div>
    </div>
  );
}
```
```css
.mq { overflow: hidden; width: 100%; }        /* NO overflow-x:hidden en <body>: rompe sticky */
.mq-track { display: flex; width: max-content; will-change: transform; }
.mq-item {
  font-family: var(--font-display), sans-serif;
  font-size: clamp(2rem, 6cqw, 5.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  white-space: nowrap;
  padding-right: 3ch;                          /* la separación entre copias, en ch */
}
```

**Dos copias exactas, ni una más.** El wrap ocurre en `scrollWidth/2`. Si metes tres copias
"por si acaso", el ciclo deja de ser la mitad y el salto se ve.

**Alternativa 100% CSS (0 KB de JS, no reacciona al scroll)** — para marquees secundarios:

```css
@keyframes mq { to { transform: translate3d(-50%, 0, 0); } }
.mq-track { animation: mq 22s linear infinite; }
@media (prefers-reduced-motion: reduce) { .mq-track { animation: none; } }
```

**Progresivo, 2026:** donde haya soporte, el navegador puede conducirlo en el compositor sin JS:

```css
@supports (animation-timeline: scroll()) {
  .mq-track {
    animation: mq 1s linear;
    animation-timeline: scroll(root block);   /* la posición del marquee ES el scroll */
    animation-play-state: running;
  }
}
```
Chrome/Edge lo tienen; Firefox aún no de forma general. **Úsalo como mejora, nunca como base.**

### 5.3 Sticky word-swap

Sección alta, contenido pegado, la palabra cambia con el progreso. El detalle que lo hace no-slop:
**solo se escribe en el DOM cuando CAMBIA el índice**, no en cada frame de scroll.

```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export function WordSwap({ words }: { words: string[] }) {
  const sec = useRef<HTMLElement>(null);
  const cur = useRef(-1);

  useGSAP(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const items = gsap.utils.toArray<HTMLElement>(".ws-item", sec.current!);
    gsap.set(items, { autoAlpha: 0, yPercent: 40 });

    ScrollTrigger.create({
      trigger: sec.current,
      start: "top top",
      end: "bottom bottom",
      onUpdate: (self) => {
        const i = Math.min(words.length - 1, Math.floor(self.progress * words.length));
        if (i === cur.current) return;              // ← el gate. Sin esto escribes 60 veces/s.
        cur.current = i;

        gsap.to(items, {
          autoAlpha: 0, yPercent: -35,
          duration: 0.35, ease: "power3.in", overwrite: true,
        });
        gsap.fromTo(items[i],
          { autoAlpha: 0, yPercent: 45 },
          { autoAlpha: 1, yPercent: 0, duration: 0.55, ease: "expo.out", overwrite: true },
        );
      },
    });
  }, { scope: sec, dependencies: [words] });

  return (
    <section ref={sec} style={{ height: `${words.length * 90}vh` }}>
      <div className="ws-sticky">
        <span className="ws-static">Construyo</span>
        <span className="ws-slot" aria-label={words.join(", ")}>
          {words.map((w) => (
            <span key={w} className="ws-item" aria-hidden="true">{w}</span>
          ))}
        </span>
      </div>
    </section>
  );
}
```
```css
.ws-sticky {
  position: sticky; top: 0; height: 100vh;
  display: flex; align-items: center; gap: 0.4em;
  font-size: clamp(2rem, 7cqw, 7rem); font-weight: 800; letter-spacing: -0.04em;
}
.ws-slot { position: relative; display: inline-block; min-width: 8ch; }
.ws-item { position: absolute; inset: 0; white-space: nowrap; will-change: transform, opacity; }
```

> **`overflow-x: hidden` en `html`/`body` mata `position:sticky`.** Es el bug #1 de esta técnica y
> ya está documentado en `[[reference-3d-scroll-r3f-blender]]`. Si el sticky "no pega", busca el
> `overflow` antes de tocar otra cosa.

`90vh` por palabra es el número: menos y el swap se atropella; más y el usuario siente que la
página se ha quedado colgada. **Con 5 palabras son 450vh — mide cuánto scroll estás cobrando y
pregúntate si lo vale.** Un word-swap de 8 palabras es una cárcel, no un efecto.

### 5.4 Texto que escala con el scroll

**Regla dura, sin excepciones:**

> **NUNCA hagas scrub de `font-size`, `letter-spacing`, `width` o `margin`.**
> Cada frame relayoutea el documento entero. Un `scale` cuesta 0 (compositor). **Solo
> `transform` y `opacity`.**

```tsx
gsap.fromTo(el,
  { scale: 1 },
  {
    scale: 9,
    transformOrigin: "50% 50%",
    ease: "none",
    scrollTrigger: { trigger: sec.current, start: "top top", end: "+=140%", scrub: 0.6, pin: true },
  },
);
```

**El gotcha que arruina el efecto: el texto escalado sale BORROSO.** Chrome rasteriza la capa una
vez, al tamaño que tenía cuando la promovió, y luego la escala como un bitmap. Escalar ×9 = ampliar
una imagen ×9.

**Fix:** rasteriza a tamaño GRANDE y escala **hacia abajo**, no hacia arriba.

```css
.zoom-word {
  font-size: clamp(6rem, 40cqw, 30rem);   /* el tamaño FINAL, el grande */
  will-change: transform;
}
```
```tsx
gsap.fromTo(el, { scale: 0.11 }, { scale: 1, ease: "none", scrollTrigger: { /* … */ } });
// arranca "pequeño" (escalado 0.11) y llega a su tamaño nativo → la textura siempre es nítida
```
Trade-off honesto: una capa de 30rem de texto es una textura grande en VRAM. En un Android de
gama media, capa esa cifra (`clamp(..., 40cqw, 18rem)`) y mídelo con `r3f-perf` / DevTools →
Rendering → Layer borders.

`scrub: 0.6` (no `true`): el `0.6` es la inercia de recuperación. `scrub:true` pega el valor al
scroll de forma literal y en trackpad se ve nervioso. **0.5–0.8 es el rango donde se siente caro.**

---

## 6. Anti-AI-slop — por qué un hero se ve genérico

Esta es la sección que Cristian está pidiendo de verdad cuando dice *"otras webs se ven muy
elegantes"*. No le falta un efecto: le sobran señales de plantilla.

### 6.1 Los tells, y el fix

| Tell (lo genérico) | Por qué lo lees como IA | Fix |
|---|---|---|
| **Inter / Poppins / Montserrat** | son los defaults de todo generador. Inter está *diseñada* para ser invisible: es exactamente lo contrario de un titular. | Una display **con opinión** (§1.4) + **una serif de contraste** para el kicker. El "elegante" que ves es casi siempre **un par**, no una fuente. |
| **Todo centrado** | el centrado es lo que haces cuando no has decidido una retícula. | Retícula asimétrica. Titular **flush-left**, contenido **anclado a las esquinas** (eyebrow arriba-izq, meta abajo-der). *El hero de este repo ya lo hace bien — eso no es el problema.* |
| **Degradado morado/índigo** | `#6366F1` es literalmente `indigo-500` de Tailwind. **Es la firma visual del código generado.** | Ver 6.2 — hoy este repo usa **tres defaults de Tailwind a la vez**. |
| **`fade-up` en absolutamente todo** | el tell de AOS/`whileInView`. Cuando todo se revela, nada se revela. | **Presupuesto de reveal: máximo 2 tipos en toda la página.** El titular por máscara; el resto entra sin animación o con un fade de 0.3s casi imperceptible. La escasez es lo que hace que el reveal del hero *signifique* algo. |
| **Escala tipográfica suave** (16→20→24→32→40→48) | escala de framework. No hay jerarquía, hay una rampa. | **Salto violento.** 11px → 230px sin nada en medio en la primera pantalla. |
| `border-radius: 12px` en todo | un solo valor aplicado a botones, cards y avatares. | Radio **por rol**: 0 en superficies grandes, 999px en pills, 4px en inputs. O radio 0 en todo (más valiente). |
| Glass + blur + emoji ✨ 🚀 | 2021 llamando. Los emoji en un portafolio senior restan credibilidad. | Iconos SVG monocromos, 1.5px stroke. *El repo ya usa SVG inline — bien.* |
| **Texto `#FFFFFF` sobre `#000000`** | contraste 21:1 = vibración de bordes, cansa, y se ve barato. | `#EDEDED` sobre `#0A0A0B`. El repo usa `#F2F2F2`/`#0F172A` — el gris está bien; **el fondo `#0F172A` es `slate-900`, otro default.** |
| Bio de marketing ("passionate about crafting elegant solutions") | frase generada. Cero información. | Datos: *"13 años. .NET y Node. Microservicios que aguantan. Agentes LLM que no alucinan en producción."* Específico = creíble. |
| Sombras `0 4px 6px rgba(0,0,0,.1)` | la sombra por defecto de Tailwind. | Sombras de **dos capas** (una corta y opaca + una larga y difusa) o **ninguna**. |

### 6.2 La verdad incómoda sobre la paleta de este repo

```css
--color-primary:   #6366F1;   /* = Tailwind indigo-500 */
--color-secondary: #10B981;   /* = Tailwind emerald-500 */
--color-accent:    #F59E0B;   /* = Tailwind amber-500 */
--color-bg:        #0F172A;   /* = Tailwind slate-900 */
```

**Cuatro colores, cuatro defaults de Tailwind sin tocar.** Es la firma cromática exacta del
portafolio generado. Puedes poner el shader más brillante del mundo encima: mientras el degradado
sea `indigo → emerald`, cualquier persona que haya visto diez portafolios de dev en 2025 lo va a
clasificar como plantilla en 300ms — **antes de leer una palabra.**

La corrección es barata (son 4 variables) y es **el cambio con mayor retorno de toda esta skill**:

```css
:root {
  /* Un fondo que no es slate-900: casi negro, con una gota de la primaria dentro.
     Un negro "teñido" se lee como decisión; #000 y #0F172A se leen como default. */
  --color-bg:    #0A0A0C;
  --color-text:  #EDEDED;

  /* UNA primaria con temperatura, no el índigo de fábrica. Ejemplos que funcionan
     sobre negro y NO son el gradiente morado: */
  --color-primary: #C8FF3D;   /* lima ácido — techy, agresivo, memorable */
  /* --color-primary: #FF5B2E;  ámbar quemado — cálido, "editorial" */
  /* --color-primary: #E6E1D6;  hueso — el "elegante" de verdad: monocromo + una sola tinta */

  /* La secundaria NO existe. Un acento. Uno. Dos acentos = ninguno. */
  --color-accent: color-mix(in srgb, var(--color-primary) 55%, var(--color-bg));
}
```
**El camino más corto a "elegante" es MONOCROMO + una sola tinta.** Casi todo lo que se ve caro es
negro/hueso/gris con **un** color, usado en el 3% de los píxeles. El degradado de dos colores es
lo contrario: reparte el énfasis y nada destaca.

### 6.3 El auto-chequeo del hero (antes de darlo por bueno)

- [ ] ¿Se puede describir el momento del hero **en una frase** a otra persona? Si no, no hay momento.
- [ ] ¿El titular **sangra fuera del viewport** por algún borde, o cabe cómodo? (Debe sangrar.)
- [ ] ¿Hay **exactamente un** color de acento?
- [ ] ¿La fuente del titular la reconocerías **de espaldas**, o es Inter?
- [ ] ¿La primera letra de cada línea está **ópticamente** alineada (§1.5) o solo alineada por caja?
- [ ] ¿El `<h1>` es **el elemento LCP** y está en el HTML del servidor? (El canvas va
      `next/dynamic ssr:false` y **jamás** puede robar el LCP.)
- [ ] ¿Cuántos tipos de reveal hay en la página? **Si son más de 2, sobran.**
- [ ] Con `prefers-reduced-motion`: ¿el hero sigue siendo **bello y estático**, o se queda vacío?
      (Congelar, nunca ocultar.)
- [ ] Ocultando el canvas, ¿el titular de dos capas se ve **como uno solo**? (Test de la costura, §4.2.)
- [ ] ¿Medido en un **Android real**, no en el portátil?

---

## 7. Presupuesto — lo que este capítulo puede gastar

| Recurso | Coste de todo lo de arriba |
|---|---|
| JS nuevo | **0 KB** (splitter propio) o **~11 KB** (SplitText, ya instalado) |
| Deps nuevas | **0** |
| Peticiones de red en runtime | **0** — `next/font` sirve desde `/_next/static` (`font-src 'self'` ✔) |
| LCP | **mejora**: el `<h1>` es texto SSR; `adjustFontFallback` evita el reflow del swap |
| CLS | **0** si `adjustFontFallback` está activo. **Alto** si lo apagas (H1 de 230px). |
| INP | **0** si todo escribe vía `quickSetter`/custom property y **nada** hace `setState` por frame |
| GPU | máscara+transform = **compositor puro**. `clip-path` animado = **paint** → solo en headings pequeños. |

---

## 8. Honestidad obligatoria (REGLA #6)

**Lo que NO va a arreglar esto:** la paleta. Puedes implementar el weaving perfecto, el split
perfecto y el marquee reactivo, y **el hero va a seguir leyéndose como generado mientras el
degradado sea `indigo-500 → emerald-500` sobre `slate-900`.** La tipografía cinética es
amplificación; amplifica lo que hay. Si lo que hay son cuatro defaults de Tailwind, amplifica eso.

**Orden de impacto real, de mayor a menor** (si solo hay tiempo para uno, es el primero):

1. **Paleta** (§6.2) — 4 variables, 10 minutos, cambia la lectura de la página entera.
2. **El bug de la costura** (§4.2) — el signature moment ahora mismo **se autodelata**.
3. **Par tipográfico** (§1.4) — display con opinión + serif de contraste en el kicker.
4. Alineación óptica (§1.5) — nadie sabrá por qué, todos lo notarán.
5. Reveal por máscara con los números de §3.2.
6. Weaving dinámico (§4.3), marquee reactivo (§5.2). *Estos son los que apetece hacer primero.
   Son los últimos por retorno.*

**Lo que no verifiqué:** los rangos exactos de ejes de las fuentes de la tabla §1.4 (el build de
`next/font` te lo dirá y falla explícito); el soporte de `text-box` fuera de Chromium; y **nada de
este código se ha ejecutado en `portafolio-frontend`** — está escrito contra el repo real
(mismos nombres de archivo, `scrollStore`, `HeroTitle`, `globals.css`) pero **hay que correrlo
y medirlo en un Android de gama media antes de darlo por cerrado.**

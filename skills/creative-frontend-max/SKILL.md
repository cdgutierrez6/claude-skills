---
name: creative-frontend-max
description: >
  Craft de INTERACCIÓN de nivel premio (Awwwards / FWA / SOTD) para páginas que ya son
  correctas pero no deslumbran. Úsala cuando el trabajo pida "wow", "que se note",
  "que impacte", "más dinámico", "que se vea caro", "espectacular", "deslumbrante",
  "premium", "signature moment", "efecto", "animación", "interacción", "cursor
  personalizado", "cursor magnético", "botón magnético", "parallax", "hover",
  "spotlight", "shader", "GLSL", "WebGL", "R3F", "react-three-fiber", "three.js",
  "partículas", "GPGPU", "curl noise", "bloom", "postprocesado", "glass",
  "transmission", "tipografía cinética", "kinetic type", "split text", "texto gigante",
  "marquee", "scroll-driven", "morphing", "grafo 3D", "red neuronal", "visualización
  de arquitectura", "preloader", "transición de página", "grain", "textura de grano",
  "microinteracción", "que parezca de Awwwards", "wow factor", "hero impactante".
  EN: wow, stunning, award-winning, jaw-dropping, signature moment, interaction craft,
  custom cursor, magnetic button, WebGL shader, GPGPU particles, kinetic typography,
  scroll-driven animation, page transition, 3D graph, neural network viz.
  NO reemplaza a web-design-pro-2026 (que sigue siendo el front door de toda sesión web):
  es invocada POR ella cuando la página necesita un momento memorable, no sólo ser correcta.
  Todo el código es React 18 + R3F v8 + drei v9 + GSAP, CSP estricta, cero CDN externo.
---

# creative-frontend-max — El impacto humano es el gate, no el adorno

## La tesis (léela antes que nada)

**Técnica sin razón humana = slop caro.** Un shader, un cursor magnético o un titular de
40vw no valen nada por existir: valen si *mueven a un humano*. La razón por la que los
efectos mediocres se leen "baratos" no es estética, es perceptual — rompen la asignación
figura-fondo y bajan la fluidez de procesamiento, y el cerebro traduce eso en *"menos bello
Y menos verdadero"*. Por eso esta skill invierte el orden habitual: **primero el porqué
humano, después la técnica.** Si no puedes nombrar la emoción y el principio que la respalda,
no hay efecto que salvar.

El documento raíz de todo esto —el alma— es [`references/human-impact.md`](references/human-impact.md).
**Ábrelo antes de elegir una sola técnica.** Todo lo demás son manos; ese archivo es la cabeza.

---

## ⭐ DEFAULT del HERO (aprobado por Cristian 2026-07-15) — leer primero para cualquier página

Para el momento héroe de CUALQUIER página/landing/proyecto, el default NO se improvisa: es la
receta canónica en [`references/cinematic-hero-2026.md`](references/cinematic-hero-2026.md) —
**UN objeto 3D art-directed** (cristal/vidrio/cromo, no abstracción) sobre negro+fog con **UNA
luz de acento** y sombra de contacto, **cámara que VIAJA con el scroll por beats** (dolly-in →
track), **video/persona integrado por luma-key** compartiendo el grade (ACES/DoF/grano/viñeta),
todo con **RESTA** ("mucho ≠ bueno"). Implementación de referencia: repo
`cdgutierrez6/portafolio-frontend`, tag `hero-cinematic-oro-v1`. Adaptar tema/objeto/paleta/video;
la estructura y el método no cambian. Ver memoria `feedback-frontend-cinematic-standard`.

---

## Quién invoca a quién (no reemplaza a nadie)

Esta skill **es invocada POR `web-design-pro-2026`**, no la sustituye.

> `web-design-pro-2026` garantiza que la página esté **CORRECTA** (anti-flat, SEO/AEO, mobile,
> a11y WCAG 2.2, CWV). `creative-frontend-max` garantiza que **IMPACTE**.

| Skill | Rol |
|---|---|
| `web-design-pro-2026` | **Front door** de toda sesión web. Orquesta. La página *correcta*. |
| `ui-ux-pro-max` / `ux-senior` / `frontend-senior` | Paleta, flujo, implementación correcta. |
| **`creative-frontend-max`** | El **momento memorable**. Se enciende sólo cuando la base ya es correcta. |

**Regla de precedencia:** si la página aún no es correcta (SEO roto, a11y rota, layout roto),
**no se maquilla**: se arregla primero. Efecto sobre base rota = slop caro.

---

## 1. EL GATE HUMANO (primero, siempre, bloqueante)

> Ningún efecto se envía sin responder por escrito estas 5 preguntas. Si falla una, el efecto
> **no se implementa** — se rediseña o se borra.

| # | Pregunta | Qué la reprueba |
|---|---|---|
| 1 | **¿Qué emoción humana busca?** | "Se ve chévere" / "lo vi en Awwwards" = **fallo**. Nombra la emoción: awe, intriga, calma, tensión, orgullo. |
| 2 | **¿Qué principio humano lo respalda?** | Si no puedes nombrarlo (awe = vastness+accommodation, gestalt figura-fondo, fluidez cognitiva, peak-end, claroscuro, Ma 間, principios de Disney), es **decoración**: se borra. |
| 3 | **¿A qué beat narrativo pertenece?** | "A ninguno" o "a todos" = **ruido con GPU**. La página es un arco (gancho → promesa → prueba → giro → cierre); cada efecto vive en un beat. |
| 4 | **¿Qué le DA al usuario?** (no sólo qué le quita) | Si sólo hay columna de "quita" (tiempo, batería, atención), es un **impuesto sin producto**. |
| 5 | **¿Cuál es su fallback sin motion / WebGL / gama baja, y es bello por sí solo?** | "No se ve nada" es un **bug**, no una degradación. |

### Las tres leyes que gobiernan el gate

- **LEY DEL PICO ÚNICO.** Un solo momento signature memorable, nombrable en **una frase**
  que un humano repetiría a otro ("el laptop se abre y la cámara te mete dentro del sistema").
  Si hay dos candidatos, **se mata uno**. Cinco picos = ningún pico. Todo lo demás en la
  página **existe para sostener ese pico** (y las secciones de "prueba" a menudo llevan CERO
  WebGL — ese sacrificio es lo que *financia* el pico).
- **LEY DEL FINAL.** El cierre se diseña; no es un footer gris. Por peak-end, el visitante
  recuerda **el pico y el final**; el promedio no lo recuerda nadie. Un footer plano tira el
  ~50% del recuerdo.
- **LA NAVAJA (sustracción).** Comenta el efecto, recarga, míralo 30 s. **Si no se pierde
  nada, sobraba** — el commit es `git rm`. La escasez es lo que hace que se lea como decisión,
  no como relleno.

---

## 2. Workflow corto (el orden no es negociable)

1. **Emoción + arco.** ¿Qué debe *sentir* el visitante y en qué orden? Define el arco
   narrativo beat por beat. (→ `human-impact.md` §4, §7)
2. **EL momento signature.** Elige UN pico. Escríbelo en una frase repetible. Decide también
   el **final**. (→ Ley del Pico Único + Ley del Final)
3. **Recién ahora, la técnica.** Elige el vehículo que sirva a ese pico — no al revés.
   (→ mapa de referencias, §4)
4. **Gate de perf/a11y.** Todo efecto declara su presupuesto o no entra. (→ §3)
5. **Verificar MIRANDO el render.** No "compila", no "corre en mi 4070": abrir el sitio,
   ver el pico, medir en un Android real, probar con `prefers-reduced-motion` y teclado.
   (`gstack-qa` — Chromium real; `gstack-benchmark` para el baseline de Core Web Vitals)

Si en el paso 3 te descubres eligiendo un shader *antes* de tener el paso 1 y 2 escritos,
detente: estás haciendo slop con presupuesto.

---

## 3. Presupuesto DURO de perf/a11y (todo efecto lo declara o no entra)

| Métrica | Límite | Cómo se respeta |
|---|---|---|
| **INP** | < 200 ms | Handlers de pointer/scroll **O(1)**: escriben en un store mutable de module-scope, **nunca `setState`** por frame. Nada de `getBoundingClientRect()` sobre algo que se está transformando; usa `quickSetter`/custom properties. |
| **LCP** | intacto | El `<h1>` real, server-rendered, es el LCP. WebGL va **lazy, post-LCP** (`next/dynamic ssr:false`) y **nunca** roba el LCP. |
| **Frame budget móvil** | ≤ 10 ms GPU | Ladder de degradación obligatorio (`PerformanceMonitor` de drei), sin realloc. |
| **`prefers-reduced-motion`** | **apaga TODO: congelar, no ocultar** | Nube de partículas estática y bella > fondo vacío. `dt→0`, no desmontar; nunca ocultar contenido. |
| **Touch** | 0 coste | Gate `matchMedia("(pointer: fine)")`: en táctil **ni se registra el listener**. |
| **Gama baja** | degradar | Poster/estático como fallback; heurística de `hardwareConcurrency` como trade-off consciente. |
| **Teclado** | espejo `:focus-visible` | Todo hover tiene su equivalente en focus, o ese elemento no existe para el usuario de teclado. |
| **CSP** | estricta, cero CDN | GLSL lo compila WebGL (no `eval`); fuentes self-hosted (`next/font`); grain como `data:` URI. |
| **Contraste** | ≥ 4.5:1 (objetivo 7:1) | Legibilidad innegociable; un pico bonito sobre texto ilegible es un bug funcional. |

**Restricción de versión, dura:** React 18.3 → **R3F v8 / drei v9**. R3F v9 / drei v10 exigen
React 19 y **fallan en duro**. Todo el código de la skill está escrito para la línea v8
(incluida la augmentación TS de JSX, distinta en v9).

---

## 4. Mapa de referencias — abre este archivo cuando…

| Archivo | Cuándo abrirlo |
|---|---|
| [`references/human-impact.md`](references/human-impact.md) | **SIEMPRE, primero.** EL PORQUÉ: psicología del awe (Keltner & Haidt), cine (claroscuro, lenguaje de cámara), percepción (gestalt, fluidez), peak-end, principios de movimiento, historia del arte, narrativa, y LO FUNCIONAL. Contiene el gate maestro y la tabla emoción→principio→parámetro→fallback. |
| [`references/webgl-craft.md`](references/webgl-craft.md) | El pico es 3D / fondo vivo. GPGPU curl-noise (FBO ping-pong), `ShaderMaterial` crudo, uniforms sin re-render, postprocesado (y cuáles NO), fresnel/iridiscencia, la **trampa** de `MeshTransmissionMaterial`, ladder adaptativo. |
| [`references/pointer-interaction.md`](references/pointer-interaction.md) | El pico es el cursor / el hover. Store único de puntero, **camera sway = mejor ratio**, cursor que muta (6 guards a11y), botones magnéticos (`quickTo`/rAF), spotlight, luz WebGL que persigue, repulsión de partículas, **por qué RGB-split está SOBREVALORADO**. |
| [`references/kinetic-type.md`](references/kinetic-type.md) | El pico es la tipografía. Titular colosal, `SplitText` (**ya es GRATIS** desde GSAP 3.13) + splitter propio 0KB, reveal por máscara (nunca fade), weaving 3D↔texto por `scrollStore`, marquee por velocidad, sistema de motion (1 easing, 3 duraciones). |
| [`references/system-viz.md`](references/system-viz.md) | El pico es "ver el sistema". Grafo/red neuronal en 2 draw calls (nodos instanciados + aristas ribbon), **paquetes de datos viajando por las aristas**, morphing de layouts por scroll. El grafo son TUS servicios reales, no `Math.random`. |
| [`references/craft-details.md`](references/craft-details.md) | Al final, siempre. Grain, preloader (contador+curtain), transiciones de página, scrollbar, `:focus-visible`, microinteracciones, **checklist anti-AI-slop** binario. |
| `references/media-generation.md` | Necesitas VIDEO/secuencias/texturas por IA (Gemini/Veo) o un HDRI sin CDN. Prompts listos + encoding web + el gate (¿reacciona? → no es video, es WebGL). |
| [`references/video-intro-with-audio.md`](references/video-intro-with-audio.md) | La página abre con una **intro de VIDEO a pantalla completa CON AUDIO**. Regla del audio (muted autoplay + botón imperativo de unmute = gesto de usuario), hand-off por `onEnded` (nunca corta), siempre-vs-once, fill desenfocado móvil, transcode con audio (¡no `-an`!), y por qué NO se puede verificar el playback en pane/automatización (background-pause). Patrón taller-ejemplo + portafolio. |

---

## 5. Honestidad obligatoria al cerrar (REGLA #6)

- Qué efecto **NO** implementaste y por qué (coste, riesgo, se ve dated).
- Qué **no verificaste** (¿compiló el GLSL en un navegador real? ¿se midió en Android real?).
  Los ms de las referencias son **estimaciones, no mediciones**.
- Qué está **sobrevalorado**: mouse trails WebGL (2023), `cursor:none` (regresión a11y
  documentada), `MeshTransmissionMaterial` sobre canvas transparente (refracta la nada),
  DepthOfField en móvil, `filter: blur` sobre un H1 colosal, dolly-zoom (marea).
- **Oportunidades de mejora:** cierra con 1-3 puntos concretos (riesgo, deuda, siguiente paso).
  Nunca cerrar con "quedó perfecto".

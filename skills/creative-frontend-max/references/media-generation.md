# Medios generados por IA — video, secuencias y texturas (coste $0)

> Pedido por Cristian (2026-07-14): *"si se necesitan videos también creas el prompt y me lo pasas para Gemini Pro… que no nos quede grande nada absolutamente nada."*
>
> Este archivo elimina la limitante de assets. Pero **la primera regla es no usar IA donde otra cosa es mejor.**

---

## 0. La tabla de decisión (léela ANTES de generar nada)

| Lo que necesitas | Herramienta correcta | Por qué |
|---|---|---|
| Objeto girando · secuencia scrubbeable frame-perfect | **Blender** (script Python, ya instalado) | La IA **deriva** entre frames: el objeto cambia de forma, de color, de logo. Blender renderiza N frames **idénticos**, gratis y en minutos. |
| Algo que **reacciona** al mouse/scroll | **WebGL (R3F)** | Un video no reacciona. No hay debate. |
| **Atmósfera** / lo orgánico que no vas a modelar (humo, energía, líquido, ciudad, nubes, partículas de polvo) | **Veo (Gemini Pro)** | Aquí la IA gana de calle. Modelar humo volumétrico es días; Veo lo hace en un prompt. |
| Fondos, texturas, grano, matte paintings | **Imagen / Nano Banana (Gemini)** | Barato y suficiente. |
| **Reflejos de entorno (HDRI)** en la escena 3D | **Gemini → imagen equirectangular 2:1** | Reflejos ricos **sin CDN externo** (la CSP estricta bloquea los HDRI de drei). Truco de alto valor. |
| Tu cara / material real | **Cámara** | Nada de deepfakes de ti mismo. |

> **Regla dura:** el video es para **ATMÓSFERA**. El WebGL es para **INTERACCIÓN**. Si mezclas los roles, terminas con un sitio pesado que no responde.

---

## 1. Límites honestos de Veo (para que no te estrelles)

- **Clips cortos** (~8 s). Para un hero necesitas que **loopee sin costura** → Veo NO garantiza un loop perfecto. **Solución:** pide un plano donde el inicio y el final sean visualmente equivalentes (cámara lenta orbitando, humo continuo), y luego **cierra el loop en la edición** con un crossfade (ffmpeg, abajo).
- **No hay control de cámara exacto** ni de continuidad entre clips. No intentes un turntable con Veo.
- **Texto dentro del video: sale mal.** Nunca pidas que escriba tu nombre. El texto va en HTML encima (y así es accesible y seleccionable).
- **Coherencia entre generaciones: baja.** Si necesitas 3 clips del mismo objeto, van a diferir. Diseña para que no importe.

---

## 2. PROMPTS LISTOS PARA PEGAR (Gemini Pro / Veo)

> Estructura que funciona: **[Sujeto] + [Acción] + [Cámara] + [Iluminación] + [Estética] + [Restricciones]**.
> Y SIEMPRE cierra con las restricciones negativas: sin texto, sin logos, sin gente.

### 2.1 — Hero: red neuronal viva (atmósfera para el fondo)
```
A vast dark void. Thousands of luminous particles drift and slowly self-assemble
into a colossal three-dimensional neural network: glowing nodes connected by thin
filaments of light, with faint pulses of energy travelling along the connections.
The structure extends far beyond the frame, suggesting something much larger than
what we can see.

Camera: extremely slow dolly-in, almost imperceptible, on a locked tripod.
Lighting: pure chiaroscuro — deep near-black background, a single cold light source;
the network is the only thing emitting light. Indigo (#6366F1) and emerald (#10B981)
accents only. High contrast, deep shadows.
Style: cinematic, photoreal volumetric light, subtle film grain, anamorphic.
Mood: calm, vast, intelligent, expensive.

Constraints: NO text, NO letters, NO numbers, NO logos, NO people, NO UI elements.
Loopable: begin and end on a nearly identical, calm state.
Aspect ratio 16:9.
```

### 2.2 — Transición: la red se reorganiza en arquitectura de sistemas
```
A glowing network of nodes in a dark void smoothly REORGANIZES itself: the organic,
brain-like structure morphs into a clean, orthogonal architecture diagram — ordered
layers, rectilinear connections, data pulses flowing between modules along right angles.
Organic chaos becoming engineered order.

Camera: locked, slow push-out revealing the full structure.
Lighting: chiaroscuro, single cold key light, indigo and emerald emissive accents.
Style: cinematic, volumetric, high contrast, subtle grain.
Constraints: NO text, NO labels, NO logos, NO people. Aspect ratio 16:9.
```

### 2.3 — Cierre: colapso a un punto (final de la historia)
```
A vast luminous network of nodes in a dark void slowly COLLAPSES inward, all its
filaments and pulses converging into a single, brilliant point of light at the center.
Everything else fades to black. The point pulses gently, alive, waiting.

Camera: locked, very slow dolly-in toward the point.
Lighting: pure black background, the point is the only light source. Indigo core.
Style: cinematic, volumetric bloom, subtle grain, minimal.
Mood: resolution, invitation, calm.
Constraints: NO text, NO logos, NO people. Aspect ratio 16:9.
```

### 2.4 — Mapa de entorno para los reflejos 3D (¡el truco de valor!)
Genera una **imagen** (no video), 2:1, y úsala como `<Environment>` local → reflejos ricos **sin CDN**.
```
An equirectangular 360-degree panorama (2:1 aspect ratio) of a dark, minimal photography
studio. Pure black surroundings. Three large softbox light panels: one large neutral-white
panel above and behind, one tall indigo (#6366F1) strip light on the left, one tall emerald
(#10B981) strip light on the right. Smooth gradient falloff, no objects, no furniture,
no people, no text. Clean, high dynamic range, product-photography lighting setup.
Seamless horizontal wrap.
```
Guárdala en `public/env/studio.jpg` y en R3F:
```tsx
// Reflejos reales sin tocar ningún CDN (CSP-safe)
<Environment files="/env/studio.jpg" resolution={512} />
```

### 2.5 — Textura de grano (más barato que un shader)
```
A seamless, tileable film grain texture. Fine monochrome noise on a mid-grey background,
like 35mm film stock grain scanned at high resolution. Subtle, organic, non-repeating.
No patterns, no shapes, no text. Square, seamless tiling.
```

---

## 3. Del asset a la web (esto es lo que casi nadie hace bien)

### 3.1 Video de fondo — encoding y reglas duras
```bash
# AV1/WebM: el más pequeño. Con fallback MP4 para Safari viejo.
ffmpeg -i in.mp4 -c:v libsvtav1 -crf 40 -preset 6 -an -vf "scale=1920:-2" out.webm
ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -an -movflags +faststart -vf "scale=1920:-2" out.mp4
# Poster (esto es lo que puede ser el LCP; el <video> NUNCA lo es)
ffmpeg -i in.mp4 -vf "select=eq(n\,0)" -q:v 3 poster.jpg
# Cerrar el loop con crossfade si Veo no dio un loop limpio (1s de solape):
ffmpeg -i in.mp4 -filter_complex "[0]split[a][b];[a]trim=0:7,setpts=PTS-STARTPTS[v0];[b]trim=7:8,setpts=PTS-STARTPTS[v1];[v0][v1]xfade=transition=fade:duration=1:offset=6" loop.mp4
```
```html
<!-- SIN autoplay ruidoso, SIN pelear con el LCP -->
<video autoplay loop muted playsinline preload="none"
       poster="/media/hero-poster.jpg" aria-hidden="true">
  <source src="/media/hero.webm" type="video/webm">
  <source src="/media/hero.mp4"  type="video/mp4">
</video>
```
**Reglas:** `muted` + `playsinline` o iOS no reproduce · el **poster es el LCP**, el `<video>` nunca lo es · `preload="none"` y montar tras el primer paint · **con `prefers-reduced-motion` NO se reproduce: se queda el poster** · en móvil de gama baja, poster y punto.

### 3.2 Secuencia scrubbeada por scroll (la técnica de Apple)
Apple **no usa WebGL** en sus páginas de producto: usa ~150 JPG dibujados en un `<canvas>`.
**Los frames los renderiza BLENDER, no la IA** (consistencia perfecta, gratis):
```python
# En el script de Blender: renderizar 120 frames de un giro completo
import bpy, math
obj = bpy.data.objects["Chassis"]
scene = bpy.context.scene
scene.render.image_settings.file_format = 'JPEG'
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
for i in range(120):
    obj.rotation_euler[2] = i / 120 * 2 * math.pi
    scene.render.filepath = f"//../../public/seq/frame_{i:03d}.jpg"
    bpy.ops.render.render(write_still=True)
```
```tsx
// Scrubber: precarga con createImageBitmap y dibuja según el progreso.
// Frame 0 se sirve como <img> normal → SÍ puede ser LCP (el canvas NUNCA lo es).
const frames = await Promise.all(
  urls.map(u => fetch(u).then(r => r.blob()).then(createImageBitmap))
);
// en el onUpdate del ScrollTrigger (scrub) → escribir en un ref, dibujar en el rAF
const i = Math.round(progress * (frames.length - 1));
ctx.drawImage(frames[i], 0, 0, canvas.width, canvas.height);
```
**Coste honesto:** 120 frames × ~60 KB = **~7 MB**. Solo vale la pena si es EL momento signature, y **siempre** lazy tras el LCP + fallback a `<img>` estático en móvil.

---

## 4. El gate (no te saltes esto)

Antes de meter un video o una secuencia, responde:
- [ ] ¿Esto **reacciona** al usuario? → si sí, **NO es video**: es WebGL.
- [ ] ¿Podría **Blender** hacerlo mejor y más barato? (objetos, giros, secuencias → **sí**).
- [ ] ¿El **LCP** sigue siendo una imagen y no el canvas/video?
- [ ] ¿Hay **poster** y fallback estático?
- [ ] ¿Con **`prefers-reduced-motion`** se queda quieto?
- [ ] ¿Cuánto pesa en **4G y Android de gama media**? (di el número, no "está bien").
- [ ] ¿Aporta al **beat narrativo** o es decoración? (ver `human-impact.md` — si lo quitas y no se pierde nada, sobraba).

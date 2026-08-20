# WebGL craft — lo que separa un R3F "bonito" de uno de premio

**Stack asumido:** React 18.3 · `@react-three/fiber@8` · `@react-three/drei@9` · `three@0.171` ·
`@react-three/postprocessing` · CSP estricta (cero CDN, cero HDRI remoto).
**No subas a R3F v9 / drei v10:** exigen React 19 y fallan en duro.

El consenso de jurado 2025-26 (Awwwards / FWA) es que **tres cosas deben aterrizar JUNTAS**:
dirección de arte específica, **motion dirigido** (que significa algo, no efectos por deporte),
y **60fps en un teléfono de gama media**. La belleza que tira frames no clasifica.

---

## 0. La plomería: uniforms desde `useFrame` con CERO re-render de React

Esto no se ve. Es lo que permite que todo lo demás corra a 60fps.

```tsx
// El objeto de uniforms se construye UNA vez. R3F mantiene la misma referencia,
// así que three ve el valor nuevo en el siguiente draw sin reconciliación.
const uniforms = useMemo(() => ({
  uTime:     { value: 0 },
  uScroll:   { value: 0 },
  uVelocity: { value: 0 },
}), []);

useFrame((state, dt) => {
  uniforms.uTime.value = state.clock.elapsedTime;          // mutación, no setState
  uniforms.uScroll.value = THREE.MathUtils.damp(
    uniforms.uScroll.value, scrollStore.page, 6, Math.min(dt, 0.1));
});

return <points>
  <shaderMaterial uniforms={uniforms} vertexShader={V} fragmentShader={F} />
</points>;
```

**Reglas duras:**
- **NUNCA `setState` desde `useFrame`, un listener de scroll o de pointer.** Un `setState` por
  frame es un fallo garantizado de INP.
- Prefiere **`<shaderMaterial>` crudo** sobre `shaderMaterial()` + `extend()` de drei: te ahorra
  el baile de `declare global { namespace JSX { interface IntrinsicElements ... } }` que la línea
  **v8** exige. (La augmentación `ThreeElements` que verás en todo blog de 2026 es **v9-only** y
  no compila aquí.)
- `Math.min(dt, 0.1)`: tras una pestaña en background el primer `dt` es enorme y cualquier
  integración explota.

---

## 1. Campo de partículas GPGPU (curl noise, FBO ping-pong) — el momento signature

65k partículas a la deriva en un flujo incompresible. El **scroll inyecta energía** (calma en el
hero, turbulento a media página); el **cursor abre un hueco** con inercia amortiguada, así que
*persigue* en vez de saltar. Es la capa que hace que la página se sienta viva en vez de "un modelo
3D sobre un fondo oscuro".

**Impacto: signature · Esfuerzo: días · Coste: ver §6**

### Arquitectura

Dos FBOs float guardan el estado como textura (`xyz` = posición, `w` = vida). Un fragment shader
sobre un quad fullscreen, en una **escena three SEPARADA**, lee el FBO A y escribe el B; se hace
swap cada frame. La textura resultante alimenta el **vertex shader** de un `THREE.Points`, que hace
un *vertex texture fetch* (siempre disponible en WebGL2).

### 1.1 El pointer store (imprescindible: `state.pointer` está MUERTO aquí)

```ts
// src/components/three/pointer-store.ts
// El canvas de fondo tiene pointer-events:none (y DEBE tenerlo, o se come todos los clicks
// del sitio) → R3F nunca recibe pointermove → state.pointer se queda en (0,0) PARA SIEMPRE,
// sin error ni warning. Este es el #1 asesino silencioso de fondos reactivos al mouse.
export const pointerStore = { nx: 0, ny: 0 };

if (typeof window !== "undefined") {
  window.addEventListener("pointermove", (e) => {
    pointerStore.nx = (e.clientX / window.innerWidth) * 2 - 1;
    pointerStore.ny = -(e.clientY / window.innerHeight) * 2 + 1;
  }, { passive: true });   // passive obligatorio: es tu presupuesto de INP
}
```

### 1.2 Simulation fragment shader

```glsl
precision highp float;

uniform sampler2D uPrev;    // ping-pong: xyz = posición, w = vida
uniform sampler2D uOrigin;  // posiciones de reposo (inmutables)
uniform float uTime, uDelta, uScroll, uVelocity, uMouseRadius, uMouseStrength, uFreeze;
uniform vec3  uMouse;       // puntero proyectado sobre un plano del mundo
varying vec2 vUv;

// snoise() = simplex 3D de Ashima (pégalo tal cual; es dominio público).
// vec3 snoiseVec3(vec3 p) { return vec3(snoise(p), snoise(p + 19.19), snoise(p - 19.19)); }

// El curl de un potencial de ruido 3D = flujo incompresible: nunca explota, nunca colapsa.
// COSTE: 6 snoiseVec3 = 18 evaluaciones de simplex por partícula por frame.
// Este es el dial de perf #1. Si hay que cortar, corta SIM_SIZE, no el shader.
vec3 curlNoise(vec3 p) {
  const float e = 0.1;
  vec3 dx = vec3(e,0,0), dy = vec3(0,e,0), dz = vec3(0,0,e);
  vec3 px0 = snoiseVec3(p-dx), px1 = snoiseVec3(p+dx);
  vec3 py0 = snoiseVec3(p-dy), py1 = snoiseVec3(p+dy);
  vec3 pz0 = snoiseVec3(p-dz), pz1 = snoiseVec3(p+dz);
  return normalize(vec3(
    (py1.z-py0.z) - (pz1.y-pz0.y),
    (pz1.x-pz0.x) - (px1.z-px0.z),
    (px1.y-px0.y) - (py1.x-py0.x)
  ) / (2.0*e));
}

void main() {
  vec4 prev   = texture2D(uPrev,   vUv);
  vec4 origin = texture2D(uOrigin, vUv);
  vec3  pos  = prev.xyz;
  float life = prev.w;

  // dt clampeado TAMBIÉN aquí, no sólo en JS. Con dt=3.0 la integración teletransporta
  // todas las partículas al infinito y el spring no puede recuperarse de un NaN.
  float dt = min(uDelta, 0.033) * (1.0 - uFreeze);   // uFreeze=1 => prefers-reduced-motion

  // (a) SCROLL = energía del campo, + surge por velocidad en un flick fuerte.
  float energy = 0.20 + uScroll * 1.00 + uVelocity * 0.8;
  pos += curlNoise(pos * 0.28 + vec3(0.0, 0.0, uTime * 0.05)) * energy * dt * 0.6;
  pos.y -= uScroll * dt * 0.30;                       // el campo "cae" al avanzar

  // (b) Repulsión del mouse. Sin if(): smoothstep ES el falloff (branchless = mobile-friendly).
  vec3 toMouse = pos - uMouse;
  float push = 1.0 - smoothstep(0.0, uMouseRadius, length(toMouse));
  pos += normalize(toMouse + vec3(1e-4)) * push * push * uMouseStrength * dt;

  // (c) SPRING de vuelta al origen. Sin esto la nube se disuelve en papilla en ~10s.
  pos = mix(pos, origin.xyz, 0.55 * dt);

  // (d) Vida -> respawn escalonado, para que la nube nunca se mueva como un bloque.
  life -= dt * (0.06 + uScroll * 0.06);
  float dead = step(life, 0.0);
  pos  = mix(pos, origin.xyz, dead);
  life = mix(life, 1.0, dead);

  gl_FragColor = vec4(pos, life);
}
```

### 1.3 Vertex shader de los Points (la posición viene de la TEXTURA)

```glsl
uniform sampler2D uPositions;
uniform float uSize, uPixelRatio, uScroll;
attribute vec2 aRef;     // uv de esta partícula dentro de la textura de simulación
attribute float aSeed;
varying float vLife, vSeed, vDepth;

void main() {
  vec4 sim = texture2D(uPositions, aRef);   // vertex texture fetch: OK siempre en WebGL2
  vLife = sim.w; vSeed = aSeed;
  vec4 mv = modelViewMatrix * vec4(sim.xyz, 1.0);
  vDepth = -mv.z;
  gl_Position = projectionMatrix * mv;

  float size = uSize * (0.55 + aSeed * 0.9) * (0.85 + uScroll * 0.3);
  // CLAMP DURO. Sin él, UNA partícula cerca de la cámara se vuelve un quad blendeado
  // de 400px y el teléfono cae a 20fps por ese frame. Es la línea más importante del shader.
  gl_PointSize = clamp(size * uPixelRatio / max(vDepth, 0.1), 1.0, 5.0);
}
```

Fragment: sprite redondo con `smoothstep(0.25, 0.0, dot(c, c))` sobre `gl_PointCoord`.
**NUNCA `discard`** en móvil: Adreno/Mali son tile-based y `discard` fuerza late-Z, matando la
optimización de profundidad de todo el tile. Con `AdditiveBlending` un alpha 0 ya es gratis.

### 1.4 El ping-pong (donde la gente se estrella)

```tsx
const fboType = gl.extensions.get("EXT_color_buffer_float")
  ? THREE.FloatType        // desktop / la mayoría de Android moderno
  : THREE.HalfFloatType;   // fallback: SIN esto el FBO se lee NEGRO en algunos teléfonos
const opts = {
  minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter,
  format: THREE.RGBAFormat, type: fboType,
  depthBuffer: false, stencilBuffer: false, generateMipmaps: false,
};
const fboA = useFBO(size, size, opts);
const fboB = useFBO(size, size, opts);
const swap = useRef(0);

// La malla de simulación vive en SU PROPIA escena, montada con createPortal para que el
// renderer raíz de R3F ni la toque: la renderizamos a mano.
const [simScene] = useState(() => new THREE.Scene());
const simCam = useMemo(() => new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1), []);

useFrame((state, dt) => {
  const d = Math.min(dt, 0.1);

  // pointer -> mundo, AMORTIGUADO. El damping es la sensación "cara": la nube persigue, no salta.
  ray.setFromCamera(ndc.set(pointerStore.nx, pointerStore.ny), state.camera);
  if (ray.ray.intersectPlane(plane, hit)) {
    simUniforms.uMouse.value.lerp(hit, 1 - Math.exp(-6 * d));
  }

  // scroll POSICIÓN + scroll VELOCIDAD (la velocidad es lo que casi nadie alimenta)
  const p = scrollStore.page;
  const vel = Math.min(1, Math.abs(p - lastScroll.current) / Math.max(d, 1e-4) / 1.2);
  lastScroll.current = p;
  simUniforms.uVelocity.value = THREE.MathUtils.damp(simUniforms.uVelocity.value, vel, 4, d);
  simUniforms.uScroll.value   = THREE.MathUtils.damp(simUniforms.uScroll.value, p, 6, d);
  simUniforms.uTime.value  = state.clock.elapsedTime;
  simUniforms.uDelta.value = d;

  const read  = swap.current === 0 ? fboA : fboB;
  const write = swap.current === 0 ? fboB : fboA;
  simUniforms.uPrev.value = read.texture;

  const prevTarget = state.gl.getRenderTarget();
  state.gl.setRenderTarget(write);
  state.gl.render(simScene, simCam);
  state.gl.setRenderTarget(prevTarget);   // ¡RESTAURAR! Ver gotchas.

  pointUniforms.uPositions.value  = write.texture;
  pointUniforms.uPixelRatio.value = state.gl.getPixelRatio();
  swap.current ^= 1;
});
```

**Seeding:** corre la simulación UNA vez con `uDelta = 0` (todos los términos van `* dt`, así que
es una copia pura origen → FBO) hacia **ambos** targets, en un `useLayoutEffect`. Sin esto, los
primeros frames leen una textura sin inicializar (negra) y todas las partículas se apilan en (0,0,0).

**Geometría:** el atributo `position` es DUMMY (todo ceros) porque la posición real vive en la
textura. three calcularía entonces un `boundingSphere` de radio 0 y **frustum-cullearía toda la
nube**. → `frustumCulled={false}` **y** un `boundingSphere` manual.

### Reduced motion / touch
`uFreeze = 1` → `dt = 0` → la nube queda **estática pero visible** (dibuja el cloud de origen).
Una nube estática y bella es mejor experiencia reduced-motion que un fondo vacío, y es lo que un
jurado que puntúa a11y quiere ver. **No desmontes el canvas.**

---

## 2. Velocidad de scroll como uniform (el truco más barato de la lista)

**Impacto: alto · Esfuerzo: horas · Coste: ~0**

La mayoría de los sitios "buenos" sólo alimentan **posición** de scroll. Alimenta también
**velocidad** y el campo *surge y se emborrona* cuando el usuario da un flick fuerte, y se asienta
cuando para. Es la diferencia entre "scroll-linked" y "scroll-reactive".

```ts
const v = Math.abs(page - lastPage) / Math.max(dt, 1e-4);
// NUNCA metas la velocidad cruda: es picuda. Amortigua siempre.
u.uVelocity.value = THREE.MathUtils.damp(u.uVelocity.value, Math.min(1, v / 1.2), 4, dt);
```
Úsala para escalar energía del flujo, tamaño de punto e intensidad del bloom.
Reduced motion: `uVelocity = 0`.

---

## 3. Fresnel rim + iridiscencia inyectados en el PBR existente

**Impacto: alto · Esfuerzo: horas · Coste: ~0 (mismo material, +8 ALU/fragmento)**

El metal recibe un borde eléctrico que sólo enciende en ángulos rasantes, y el bisel toma un
brillo de película delgada al girar. **Lee como iluminación cara, no como filtro.**

### (a) Iridiscencia: GRATIS, nativa en three 0.171

```tsx
// dentro del traverse que ya tienes en el useLayoutEffect del modelo
if (mat instanceof THREE.MeshPhysicalMaterial) {
  mat.iridescence = 1;
  mat.iridescenceIOR = 1.3;
  mat.iridescenceThicknessRange = [100, 400];
  mat.needsUpdate = true;
}
```

### (b) Rim: `onBeforeCompile`, un archivo, cero deps

```ts
const rimUniforms = {
  uRimColor:    { value: new THREE.Color("#67e8f9") },
  uRimStrength: { value: 0.0 },
};

material.onBeforeCompile = (shader) => {
  shader.uniforms.uRimColor    = rimUniforms.uRimColor;
  shader.uniforms.uRimStrength = rimUniforms.uRimStrength;

  shader.vertexShader = shader.vertexShader
    .replace("#include <common>", `#include <common>
      varying vec3 vNormalView;
      varying vec3 vViewDir;`)
    .replace("#include <fog_vertex>", `#include <fog_vertex>
      vNormalView = normalize(normalMatrix * normal);
      vViewDir    = normalize(-(modelViewMatrix * vec4(position, 1.0)).xyz);`);

  shader.fragmentShader = shader.fragmentShader
    .replace("#include <common>", `#include <common>
      uniform vec3  uRimColor;
      uniform float uRimStrength;
      varying vec3 vNormalView;
      varying vec3 vViewDir;`)
    .replace("#include <output_fragment>", `#include <output_fragment>
      float f = pow(1.0 - clamp(dot(vNormalView, vViewDir), 0.0, 1.0), 3.0);
      gl_FragColor.rgb += uRimColor * f * uRimStrength;`);
};

// y desde useFrame:  rimUniforms.uRimStrength.value = 0.3 + scrollStore.page * 0.9;
```

> No metas `three-custom-shader-material` a menos que necesites **también** desplazamiento de
> vértices. `onBeforeCompile` es un archivo y cero dependencias.

---

## 4. Postprocesado: el que lee como premium, y los que NO

**Impacto: signature · Esfuerzo: horas**

El **banding de color en los degradados oscuros** es el tell #1 de "WebGL amateur", y casi nadie
lo arregla. El grano lo arregla.

```tsx
<EffectComposer multisampling={0}>   {/* 0 en móvil; deja que SMAA haga el AA si hace falta */}
  <Bloom mipmapBlur luminanceThreshold={0.55} intensity={0.9} radius={0.65} />
  <Vignette darkness={0.5} eskil={false} />          {/* ~gratis */}
  <Noise premultiply opacity={0.035} />              {/* ESTO mata el banding */}
</EffectComposer>
```

| Efecto | Veredicto |
|---|---|
| `Bloom` con `mipmapBlur` | **SÍ.** Es la variante moderna y barata. |
| `Vignette` | **SÍ.** Prácticamente gratis. |
| `Noise` (grain) | **SÍ, obligatorio.** Difumina el degradado y destruye el banding. |
| Aberración cromática | **Sólo radial.** Fullscreen parece TV rota. Modúlala por `radius^2` en un `Effect` custom de `postprocessing`, para que sólo muerda en las esquinas. |
| `DepthOfField` / `Bokeh` | **NO.** Multi-pass, difumina justo el contenido que quieres que se lea, y en móvil mata el frame. |
| `SSAO` | **NO.** Fuerza `enableNormalPass` = un segundo pase completo de geometría. Si de verdad quieres AO: `N8AO` (mucho más barato) — pero **nunca en teléfonos**. |
| `GodRays`, motion blur | **NO.** Coste alto, señal estética vieja. |

Coste real de `Bloom + Vignette + Noise` juntos en un Adreno de gama media: **~2-4 ms**, o sea el
**20% del presupuesto de 16.6 ms**. Tirar el post es la palanca más grande después del número de
partículas.

---

## 5. `MeshTransmissionMaterial` / glass — úsalo, pero conoce la trampa

**Impacto: medio · Esfuerzo: día · Veredicto honesto: probablemente NO**

> **LA TRAMPA:** el buffer de transmisión **sólo ve la escena WebGL**. Si tu canvas es
> **transparente y está DETRÁS del HTML**, el vidrio va a refractar el vacío y se verá como un
> **borrón gris muerto**. Gorgeous en el demo de drei, inútil en tu página.

Para que el vidrio pague hay que **meter contenido DENTRO del canvas** (drei `<Text>` / `<Image>`
detrás del vidrio) — o fingirlo en CSS con `backdrop-filter`.

Si aun así vas:
```tsx
<MeshTransmissionMaterial
  resolution={256}          // el default es FULLSCREEN. SIEMPRE fíjalo.
  samples={4}               // default 6
  backside={false}          // backside renderiza la escena DOS veces
  chromaticAberration={0.04}
  anisotropicBlur={0.1}
  distortion={0.2}
  temporalDistortion={0.1}
/>
```
Máximo **un** objeto MTM en toda la página.

---

## 6. Ladder adaptativo — esto es lo que de verdad gana el premio

**Impacto: signature · Esfuerzo: día**

No se ve nada en una buena máquina; en un Android medio la escena adelgaza en silencio y **sigue a
60fps**. Los jurados lo puntúan.

```tsx
<PerformanceMonitor
  onDecline={() => setTier((t) => Math.max(0, t - 1))}
  onIncline={() => setTier((t) => Math.min(2, t + 1))}
>
  <AdaptiveDpr pixelated />
  <AdaptiveEvents />
  {/* ... */}
</PerformanceMonitor>
```

| Tier | dpr | Partículas dibujadas | Post | ContactShadows |
|---|---|---|---|---|
| 2 (desktop) | 1.75 | SIM 256 → 65k | Bloom + Vignette + Noise | 512 |
| 1 (mid) | 1.25 | SIM 128 → drawRange 12k | Bloom sólo, `multisampling={0}` | 256 |
| 0 (low) | 1.0 | drawRange 6k | **ninguno** | off |

- Reduce partículas con **`geometry.setDrawRange(0, n)`** — *sin* reasignar el FBO. Redimensionar
  un FBO es caro; recortar el drawRange es gratis. Ese es todo el truco.
- `<ContactShadows>` **NO es gratis**: se re-renderiza CADA frame porque el objeto se mueve (un
  pase de profundidad completo a su `resolution`). Bájalo o apágalo en móvil.
- `<Environment>` con `<Lightformer>` sí es gratis: hornea el cubemap **una vez** (`frames={1}` por
  defecto) — y es **CSP-safe** (no descarga un HDRI externo). Nunca uses `frames={Infinity}`.

---

## 7. Números reales (estimaciones de ingeniería, NO mediciones — verifica con r3f-perf + un teléfono)

El shader de simulación son ~18 evaluaciones de simplex por partícula por frame (curl necesita 6
muestras del potencial × 3 componentes) ≈ **1.400-1.800 ALU ops / partícula / frame**.

**Pase de simulación (fragment sobre el FBO):**
| SIM_SIZE | Partículas | ops/frame | @60fps | Veredicto |
|---|---|---|---|---|
| 128² | 16.384 | ~25M | ~1.5 GFLOP/s | trivial en cualquier lado |
| 256² | 65.536 | ~100M | ~6 GFLOP/s | ~1.5-3 ms GPU. Cómodo en Adreno 619 / Mali-G68 |
| 512² | 262.144 | ~400M | ~24 GFLOP/s | **sólo desktop.** En Android medio son 8-15 ms: frame perdido |

**Pase de render (esto es lo que mata teléfonos):** 65k point sprites aditivos sin depth-write =
**overdraw puro**. Con `gl_PointSize ≤ 5` y dpr 1.25 → ~1.3M fragmentos blendeados/frame ≈ 0.6× un
pase fullscreen 1080p → **~2-4 ms**, aceptable. Sube el clamp a 20px y son ~26M fragmentos = **12×
fullscreen de overdraw = 20fps instantáneos**.

> **En móvil el cuello NO es la simulación, es el FILL RATE de los sprites blendeados.
> Duplicar el número de partículas es más barato que duplicar el tamaño del punto.**

**Core Web Vitals:** el campo cuesta **0 en LCP** si va dentro del `<Suspense>` y el canvas es
client-only (`next/dynamic ssr:false`). **Sí amenaza INP**: cada ms extra de GPU alarga el rAF del
main thread. El listener de `pointermove` debe ser `{ passive: true }` y jamás hacer `setState`.
Presupuesta **≤10 ms de frame en móvil** para mantener INP bajo 200 ms.

**Memoria:** 2 × FBO 256² RGBA32F = 2 MB + 1 MB de la DataTexture de origen. Irrelevante. El
problema es puramente ALU + fill rate.

---

## Gotchas (todos costaron horas a alguien)

1. **`state.pointer` es (0,0) para siempre** si el canvas tiene `pointer-events: none`. Sin error,
   sin warning. Todo tutorial de "camera parallax" que lea `state.pointer` aquí **no hace nada**.
   → `pointerStore` de module-scope alimentado por un listener de `window`.
2. **`THREE.FloatType` NO está garantizado en Android.** Sin `EXT_color_buffer_float` el FBO se crea
   pero se lee **NEGRO**, y todas las partículas colapsan al origen: parece que tu shader está roto
   cuando no lo está. → feature-detect + `HalfFloatType`.
3. **SIEMPRE restaura el render target:** `const prev = gl.getRenderTarget(); ...;
   gl.setRenderTarget(prev)`. Si hardcodeas `setRenderTarget(null)` rompes el `EffectComposer`, que
   *él mismo* está renderizando a un target offscreen cuando tu `useFrame` corre. Es el clásico
   *"mi bloom desapareció cuando añadí partículas"*.
4. **Atributo `position` dummy → boundingSphere radio 0 → frustum culling → no ves NADA.**
   `frustumCulled={false}` + boundingSphere manual.
5. **Nunca `discard` en el fragment de los puntos en móvil.** Tile-based GPUs: mata el early-Z de
   todo el tile.
6. **`gl_PointSize` DEBE ir clampeado.** Es la línea más importante del shader.
7. **Clampea `dt` también DENTRO del shader**, no sólo en JS. Un `dt` de 3.0 tras una pestaña en
   background teletransporta todo al infinito y el spring no recupera de un NaN.
8. **MTM refracta la nada** sobre un canvas transparente. Ver §5.
9. **`<ContactShadows>` re-renderiza cada frame.** No es gratis.
10. **TS en R3F v8:** la augmentación de JSX va por `declare global { namespace JSX {
    interface IntrinsicElements ... } }`. `ThreeElements` es **v9-only**. Esquívalo usando
    `<shaderMaterial>` crudo.
11. **`prefers-reduced-motion` debe CONGELAR la simulación (`dt → 0`), no ocultar el canvas.**
12. **Verifica el GLSL en un navegador de verdad.** Que TypeScript compile no dice nada del shader.

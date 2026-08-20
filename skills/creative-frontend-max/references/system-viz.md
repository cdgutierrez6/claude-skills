# system-viz — visualizar el SISTEMA, no un portátil

> "La programación no es un computador y ya." — Cristian.
>
> Un portafolio de un **Solutions Architect + AI engineer** que muestra un laptop girando
> está contando la mentira más pequeña posible sobre lo que hace. El trabajo real es
> **software distribuido, redes neuronales, agentes, grafos de dependencias**. Este archivo
> construye ESO en 3D: un grafo/red que respira, reacciona al cursor y **se transforma por
> scroll** de red neuronal → arquitectura de microservicios → constelación.
>
> El laptop.glb puede quedarse como acento del hero. Pero **el momento signature de esta
> página es el grafo**: la cosa que un recruiter puede describir con palabras ("cuando bajas,
> la red neuronal se reorganiza en la arquitectura de sus microservicios, y ves los paquetes
> de datos viajando por los cables").

Este doc asume que ya leíste `webgl-craft.md` (la plomería de uniforms sin re-render, el
ladder de `PerformanceMonitor`, el tuning de `Bloom`). Aquí **no se repite**: se referencia.

---

## GATE (contesta antes de escribir shader)

- **EL momento (1 frase):** al hacer scroll, la red neuronal en capas se reorganiza en la
  topología de microservicios de Cristian y luego se dispersa en constelación; en todo momento
  hay **pulsos de datos recorriendo las aristas**.
- **Qué SIGNIFICA:** no es un grafo genérico de librería. Los nodos son **sus servicios/capas
  reales**; las aristas son **llamadas reales**; los pulsos son **tráfico**. El motion *dice*
  "yo diseño sistemas", no "sé usar three.js".
- **60fps en Android medio:** sí, con el presupuesto de abajo (≤120 nodos, 2-3 draw calls,
  pulsos en shader sin geometría extra). Verificado por diseño, **no medido** — hay que medir.
- **¿Uno o cinco?** UNO. Un solo grafo que morfea. No cinco visualizaciones distintas.

---

## Presupuesto honesto — cuántos nodos son SEGUROS

| Tier | Dispositivo | Nodos | Aristas | Pulsos | Draw calls |
|---|---|---|---|---|---|
| 2 (desktop) | discreta / M-series | 120–160 | 200–260 | todos | 3 |
| 1 (mid) | Adreno 6xx / A-series viejo | 60–90 | 100–140 | 1 de cada 2 aristas | 3 |
| 0 (low / reduced-motion) | gama baja | 40 | 60 | congelado (estático bello) | 2 |

**Por qué esos números.** El cuello NO son los nodos (van en **un** `InstancedMesh`: 1 draw
call para 160). El cuello son las **aristas**: cada arista con grosor real es un ribbon de
~8 vértices, y el shader de pulso corre por fragment. 260 aristas ≈ 2.080 vértices y un
fragment shader barato → trivial en desktop, ajustado pero sano en un Adreno de gama media si
el pulso es `smoothstep`, no un `pow` caro. **Más de ~300 aristas con pulso + Bloom** empieza a
comerse el frame en móvil. Si dudas, baja aristas antes que nodos: el ojo cuenta luces, no cables.

---

## Arquitectura de datos — el grafo son TUS servicios, no `Math.random()`

Un grafo aleatorio se ve como screensaver. Define la topología a mano (es tu portafolio):

```ts
// src/components/three/graph/graph-data.ts
// Los 3 layouts comparten el MISMO conjunto de nodos (mismo índice = mismo nodo).
// Lo único que cambia entre layouts es la POSICIÓN. Eso es lo que permite lerpear.

export type NodeKind = "input" | "hidden" | "output" | "service" | "gateway" | "db" | "queue";

export interface GNode {
  id: string;
  kind: NodeKind;
  label?: string;
}

export interface GEdge {
  a: number; // índice en nodes[]
  b: number;
}

// Ejemplo real-ish: capas de una red (izq) que también son servicios (der).
// Mantén N constante (aquí N = 96). Rellena con "hidden" si un layout necesita menos.
export const NODE_COUNT = 96;

export const nodes: GNode[] = buildNodes(); // ver helper abajo
export const edges: GEdge[] = buildEdges();

// Paleta por tipo — emisiva. Se pasa como atributo de instancia (aColor).
export const KIND_COLOR: Record<NodeKind, [number, number, number]> = {
  input:   [0.20, 0.85, 0.75], // teal (tu "teal = dinero", aquí "teal = entrada")
  hidden:  [0.35, 0.55, 1.00], // azul
  output:  [0.85, 0.35, 0.95], // magenta
  service: [0.30, 0.80, 1.00], // cian
  gateway: [1.00, 0.70, 0.25], // ámbar
  db:      [0.55, 1.00, 0.45], // verde
  queue:   [1.00, 0.45, 0.45], // rojo suave
};
```

### Precomputar las 3 posiciones por nodo (la clave del morphing)

El morphing NO recalcula un layout en runtime. Se precomputan **3 vectores por nodo** una vez,
y en el shader/atributo se **lerpea** entre ellos según el scroll. O(N) una vez, 0 por frame.

```ts
// src/components/three/graph/layouts.ts
import * as THREE from "three";
import { NODE_COUNT, nodes } from "./graph-data";

const R = 6; // radio/escena base

// LAYOUT A — RED NEURONAL: capas en X, nodos apilados en Y dentro de cada capa.
export function layoutNeural(): THREE.Vector3[] {
  const layers = [8, 16, 20, 20, 16, 12, 4]; // suma = 96 = NODE_COUNT
  const out: THREE.Vector3[] = [];
  let li = 0;
  layers.forEach((count, layer) => {
    const x = THREE.MathUtils.mapLinear(layer, 0, layers.length - 1, -R, R);
    for (let i = 0; i < count; i++) {
      const y = THREE.MathUtils.mapLinear(i, 0, Math.max(count - 1, 1), -R * 0.6, R * 0.6);
      out.push(new THREE.Vector3(x, y, (Math.random() - 0.5) * 0.4)); // z jitter mínimo
      li++;
    }
  });
  while (out.length < NODE_COUNT) out.push(new THREE.Vector3(0, 0, 0));
  return out.slice(0, NODE_COUNT);
}

// LAYOUT B — MICROSERVICIOS: anillos concéntricos por rol (gateway centro, servicios anillo,
// db/queue anillo externo). Determinista por índice para que sea estable entre reloads.
export function layoutMicro(): THREE.Vector3[] {
  const ringOf: Record<string, number> = { gateway: 0, service: 1, hidden: 1, input: 1, output: 1, db: 2, queue: 2 };
  const radius = [0, R * 0.55, R * 0.95];
  // agrupa índices por anillo para repartir el ángulo uniformemente
  const buckets: number[][] = [[], [], []];
  nodes.forEach((n, i) => buckets[ringOf[n.kind] ?? 1].push(i));
  const out = new Array<THREE.Vector3>(NODE_COUNT);
  buckets.forEach((idxs, ring) => {
    idxs.forEach((idx, k) => {
      const ang = (k / Math.max(idxs.length, 1)) * Math.PI * 2 + ring * 0.6;
      const r = radius[ring];
      out[idx] = new THREE.Vector3(Math.cos(ang) * r, Math.sin(ang) * r * 0.7, Math.sin(ang * 2) * 0.6);
    });
  });
  for (let i = 0; i < NODE_COUNT; i++) if (!out[i]) out[i] = new THREE.Vector3(0, 0, 0);
  return out;
}

// LAYOUT C — CONSTELACIÓN: esfera de Fibonacci (distribución uniforme, se ve "espacio").
export function layoutConstellation(): THREE.Vector3[] {
  const out: THREE.Vector3[] = [];
  const phi = Math.PI * (Math.sqrt(5) - 1); // ángulo áureo
  for (let i = 0; i < NODE_COUNT; i++) {
    const y = 1 - (i / (NODE_COUNT - 1)) * 2; // 1 → -1
    const r = Math.sqrt(1 - y * y);
    const th = phi * i;
    out.push(new THREE.Vector3(Math.cos(th) * r, y, Math.sin(th) * r).multiplyScalar(R * 0.95));
  }
  return out;
}
```

Guardo estas tres posiciones en atributos de instancia (`aPosA`, `aPosB`, `aPosC`) y dejo que
el **GPU** haga el lerp. Así el morphing es gratis por frame.

---

Continúo con los nodos instanciados, las aristas con grosor real, el shader de pulsos, la
respiración/repulsión, el morphing en shader, el bloom y el ladder de degradación.

## 1. Nodos: un `InstancedMesh` con posición y color por instancia

`InstancedMesh` = **1 draw call** para los N nodos. Pero el reto: queremos que cada nodo (a)
tenga su color por tipo, (b) morfee entre 3 posiciones, (c) respire y (d) se repela del cursor.
Nada de eso cabe en `instanceMatrix` si queremos hacerlo en shader. Solución: **atributos de
instancia propios** + un `ShaderMaterial` (o `MeshStandardMaterial` con `onBeforeCompile`).

Para nodos **emisivos con bloom** no necesitamos PBR: un `ShaderMaterial` crudo es más barato
y más controlable. La geometría base es una esfera de **bajo poli** (icosaedro detail 1 = 42
vértices) — con bloom nadie nota que no es lisa.

```tsx
// src/components/three/graph/Nodes.tsx
"use client";
import { useMemo, useRef, useLayoutEffect } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { NODE_COUNT, nodes, KIND_COLOR } from "./graph-data";
import { layoutNeural, layoutMicro, layoutConstellation } from "./layouts";
import { graphStore } from "./graph-store";

const nodeVert = /* glsl */ `
  precision highp float;

  // atributos de instancia (3 layouts + color)
  attribute vec3 aPosA;
  attribute vec3 aPosB;
  attribute vec3 aPosC;
  attribute vec3 aColor;
  attribute float aSeed;   // 0..1 para desfasar la respiración por nodo

  uniform float uTime;
  uniform float uMorph;    // 0..2 : 0=A(neural) 1=B(micro) 2=C(constelación)
  uniform vec3  uPointer;  // posición del cursor en mundo (z=plano del grafo)
  uniform float uPointerActive; // 0/1 gate touch/reduced-motion

  varying vec3 vColor;
  varying float vPulseGlow; // reservado (los nodos brillan más cuando les llega un pulso)

  // lerp encadenado A->B->C con un solo escalar 0..2
  vec3 morphPos(vec3 a, vec3 b, vec3 c, float m) {
    vec3 ab = mix(a, b, clamp(m, 0.0, 1.0));
    return mix(ab, c, clamp(m - 1.0, 0.0, 1.0));
  }

  void main() {
    vColor = aColor;

    vec3 base = morphPos(aPosA, aPosB, aPosC, uMorph);

    // RESPIRACIÓN: cada nodo orbita un pelín su posición, desfasado por aSeed.
    float br = sin(uTime * 1.2 + aSeed * 6.2831) * 0.12;
    base += normalize(base + 0.001) * br;

    // REPULSIÓN del cursor: empuja radialmente si está cerca (solo pointer fino).
    vec3 toP = base - uPointer;
    float d = length(toP);
    float push = uPointerActive * smoothstep(2.4, 0.0, d) * 1.1;
    base += normalize(toP + 0.0001) * push;

    // la posición de instancia se compone con la geometría base (la esferita)
    vec4 mvPosition = modelViewMatrix * vec4(base, 1.0);
    // escala del nodo: respira levemente en tamaño también
    float s = 1.0 + 0.15 * sin(uTime * 2.0 + aSeed * 12.0);
    mvPosition.xyz += position * (0.10 * s); // 0.10 = radio del nodo en unidades de mundo

    gl_Position = projectionMatrix * mvPosition;
    vPulseGlow = 0.0;
  }
`;

const nodeFrag = /* glsl */ `
  precision highp float;
  varying vec3 vColor;
  uniform float uExposure;
  void main() {
    // color emisivo plano; el brillo lo pone el Bloom (toneMapped=false en el material)
    gl_FragColor = vec4(vColor * uExposure, 1.0);
  }
`;

export default function Nodes() {
  const mesh = useRef<THREE.InstancedMesh>(null);
  const mat = useRef<THREE.ShaderMaterial>(null);

  // geometría base: icosaedro low-poly (42 verts). NO por-nodo: es la MISMA para todas.
  const geo = useMemo(() => new THREE.IcosahedronGeometry(1, 1), []);

  // atributos de instancia: se calculan UNA vez
  const attrs = useMemo(() => {
    const A = layoutNeural();
    const B = layoutMicro();
    const C = layoutConstellation();
    const posA = new Float32Array(NODE_COUNT * 3);
    const posB = new Float32Array(NODE_COUNT * 3);
    const posC = new Float32Array(NODE_COUNT * 3);
    const col = new Float32Array(NODE_COUNT * 3);
    const seed = new Float32Array(NODE_COUNT);
    for (let i = 0; i < NODE_COUNT; i++) {
      A[i].toArray(posA, i * 3);
      B[i].toArray(posB, i * 3);
      C[i].toArray(posC, i * 3);
      const c = KIND_COLOR[nodes[i].kind];
      col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
      seed[i] = Math.random();
    }
    return { posA, posB, posC, col, seed, A, B, C };
  }, []);

  useLayoutEffect(() => {
    const m = mesh.current!;
    m.geometry.setAttribute("aPosA", new THREE.InstancedBufferAttribute(attrs.posA, 3));
    m.geometry.setAttribute("aPosB", new THREE.InstancedBufferAttribute(attrs.posB, 3));
    m.geometry.setAttribute("aPosC", new THREE.InstancedBufferAttribute(attrs.posC, 3));
    m.geometry.setAttribute("aColor", new THREE.InstancedBufferAttribute(attrs.col, 3));
    m.geometry.setAttribute("aSeed", new THREE.InstancedBufferAttribute(attrs.seed, 1));
    // instanceMatrix NO se usa para posicionar (lo hace el shader) pero R3F exige que exista;
    // la dejamos identidad. Cada instancia necesita una matriz aunque sea identidad.
    const dummy = new THREE.Object3D();
    for (let i = 0; i < NODE_COUNT; i++) { dummy.updateMatrix(); m.setMatrixAt(i, dummy.matrix); }
    m.instanceMatrix.needsUpdate = true;
  }, [attrs]);

  useFrame((state, dt) => {
    const u = mat.current!.uniforms;
    u.uTime.value = state.clock.elapsedTime;
    // morph 0..2 desde el scroll (graphStore.morph lo escribe ScrollTrigger, ver §5)
    u.uMorph.value = THREE.MathUtils.damp(u.uMorph.value, graphStore.morph, 4, Math.min(dt, 0.1));
    // cursor en mundo (ver §4 para cómo se llena graphStore.pointer)
    u.uPointer.value.copy(graphStore.pointer);
    u.uPointerActive.value = graphStore.pointerActive;
  });

  return (
    <instancedMesh ref={mesh} args={[geo, undefined, NODE_COUNT]} frustumCulled={false}>
      <shaderMaterial
        ref={mat}
        vertexShader={nodeVert}
        fragmentShader={nodeFrag}
        toneMapped={false}
        uniforms={useMemo(
          () => ({
            uTime: { value: 0 },
            uMorph: { value: 0 },
            uPointer: { value: new THREE.Vector3(999, 999, 999) },
            uPointerActive: { value: 0 },
            uExposure: { value: 1.6 }, // >1 para que el Bloom lo agarre
          }),
          []
        )}
      />
    </instancedMesh>
  );
}
```

**Nota clave sobre `InstancedMesh` + shader propio:** al posicionar en el vertex shader
(`base + position * radio`) e ignorar `instanceMatrix`, dejas `frustumCulled={false}` porque el
bounding box calculado por three ya no corresponde a dónde están realmente los nodos (three no
sabe que los moviste en el shader). Sin eso, el grafo **desaparece** cuando su bbox original sale
de cámara. Es el gotcha #1 de instancing con posición en shader.

---

Sigo con las aristas (el problema del grosor de línea) y el shader de pulsos.

## 2. Aristas que BRILLAN — por qué `THREE.Line` NO sirve, y la solución real

### El problema, sin rodeos

`THREE.Line` / `LineSegments` con `LineBasicMaterial.linewidth` **ignora `linewidth` en casi
todos los navegadores**. No es un bug de three: es una limitación del backend. La spec de
WebGL/OpenGL ES sólo obliga a soportar `gl_LineWidth == 1.0`; ANGLE (el traductor de
GL→Direct3D que usa Chrome/Edge en Windows) reporta un rango de `[1,1]`. Resultado: pongas
`linewidth: 8`, ves líneas de **1px**. En un grafo eso se ve pobre y titila. No hay workaround
del lado de `THREE.Line`.

### La solución real: aristas como GEOMETRÍA (ribbons en screen-space)

Se dibuja cada arista como un **quad/tira** cuyo grosor se expande en el vertex shader
perpendicular a la línea, **en espacio de pantalla**, para que el grosor sea constante en px
sin importar la distancia a cámara. Esto es exactamente lo que hace `meshline`, y drei lo
envuelve en `<Line>` (basado en `Line2`/`LineMaterial` de three-stdlib, que YA viene con
`@react-three/drei@9` — **cero deps nuevas**).

**Dos caminos, y cuándo cada uno:**

| Camino | Cuándo | Coste |
|---|---|---|
| **drei `<Line>` / `<Segments>`** | prototipo, o si NO necesitas el shader de pulso propio | trivial, pero el material es de drei → inyectar el pulso obliga a `onBeforeCompile` |
| **Geometría propia de ribbons + `ShaderMaterial`** | queremos el pulso viajando (el momento signature) con control total | ~1 buffer, control absoluto — **este es el que usamos** |

Elijo geometría propia porque **el efecto signature (§3) vive en el fragment shader de la
arista**, y quiero controlarlo sin pelear con el material de drei.

### 2.1 Construir la geometría de ribbons

Cada arista = un quad (2 triángulos, 4 vértices). Guardo por vértice: los **dos extremos** de
la arista (para poder morfear con los mismos 3 layouts que los nodos) y un `aSide` (±1) para
saber a qué lado expandir, y un `aT` (0/1) para saber si el vértice es el extremo A o B.

```ts
// src/components/three/graph/build-edges-geometry.ts
import * as THREE from "three";
import { edges, NODE_COUNT } from "./graph-data";
import { layoutNeural, layoutMicro, layoutConstellation } from "./layouts";

export function buildEdgeGeometry() {
  const A = layoutNeural(), B = layoutMicro(), C = layoutConstellation();
  const E = edges.length;

  // 4 vértices por arista, 6 índices (2 triángulos)
  const vCount = E * 4;
  // extremos en cada layout, para el morphing (idénticos a los de los nodos)
  const endA_A = new Float32Array(vCount * 3); // extremo "a" en layout A
  const endB_A = new Float32Array(vCount * 3); // extremo "b" en layout A
  const endA_B = new Float32Array(vCount * 3);
  const endB_B = new Float32Array(vCount * 3);
  const endA_C = new Float32Array(vCount * 3);
  const endB_C = new Float32Array(vCount * 3);
  const aSide = new Float32Array(vCount);   // -1 / +1  (lado del ribbon)
  const aT    = new Float32Array(vCount);   //  0 / 1   (extremo a o b)
  const aEdge = new Float32Array(vCount);   // índice de arista, para desfasar el pulso
  const index = new Uint32Array(E * 6);

  const set = (arr: Float32Array, i: number, v: THREE.Vector3) => v.toArray(arr, i * 3);

  for (let e = 0; e < E; e++) {
    const { a, b } = edges[e];
    const base = e * 4;
    // 4 vértices: [a-lado-, a-lado+, b-lado-, b-lado+]
    const layout = [
      { t: 0, side: -1 }, { t: 0, side: 1 },
      { t: 1, side: -1 }, { t: 1, side: 1 },
    ];
    layout.forEach((L, k) => {
      const vi = base + k;
      set(endA_A, vi, A[a]); set(endB_A, vi, A[b]);
      set(endA_B, vi, B[a]); set(endB_B, vi, B[b]);
      set(endA_C, vi, C[a]); set(endB_C, vi, C[b]);
      aSide[vi] = L.side;
      aT[vi] = L.t;
      aEdge[vi] = e;
    });
    const o = e * 6;
    // dos triángulos: (0,2,1) (2,3,1)
    index[o] = base; index[o + 1] = base + 2; index[o + 2] = base + 1;
    index[o + 3] = base + 2; index[o + 4] = base + 3; index[o + 5] = base + 1;
  }

  const g = new THREE.BufferGeometry();
  // 'position' dummy: el shader calcula la posición real desde los extremos morfeados.
  g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(vCount * 3), 3));
  g.setAttribute("endA_A", new THREE.BufferAttribute(endA_A, 3));
  g.setAttribute("endB_A", new THREE.BufferAttribute(endB_A, 3));
  g.setAttribute("endA_B", new THREE.BufferAttribute(endA_B, 3));
  g.setAttribute("endB_B", new THREE.BufferAttribute(endB_B, 3));
  g.setAttribute("endA_C", new THREE.BufferAttribute(endA_C, 3));
  g.setAttribute("endB_C", new THREE.BufferAttribute(endB_C, 3));
  g.setAttribute("aSide", new THREE.BufferAttribute(aSide, 1));
  g.setAttribute("aT", new THREE.BufferAttribute(aT, 1));
  g.setAttribute("aEdge", new THREE.BufferAttribute(aEdge, 1));
  g.setIndex(new THREE.BufferAttribute(index, 1));
  g.frustumCulled = false;
  return g;
}
```

---

## 3. EL EFECTO SIGNATURE — pulsos de datos viajando por las aristas

Aquí está el corazón. Un `ShaderMaterial` sobre la geometría de ribbons. El **vertex shader**
(a) morfea cada extremo con el mismo `uMorph` que los nodos, (b) expande el ribbon a grosor
constante en pantalla. El **fragment shader** dibuja la línea base tenue + un **highlight
gaussiano que se desplaza** a lo largo de la arista con `uTime` (el paquete de datos), con
`aEdge` desfasando cada arista para que no pulsen todas iguales.

### 3.1 Vertex shader (morphing + grosor en screen-space)

```glsl
// edge.vert
precision highp float;

attribute vec3 endA_A; attribute vec3 endB_A;
attribute vec3 endA_B; attribute vec3 endB_B;
attribute vec3 endA_C; attribute vec3 endB_C;
attribute float aSide;   // -1 / +1
attribute float aT;      //  0 / 1  (a lo largo de la arista)
attribute float aEdge;

uniform float uMorph;      // 0..2
uniform float uThickness;  // grosor en px
uniform vec2  uResolution;
uniform vec3  uPointer;
uniform float uPointerActive;

varying float vT;          // posición a lo largo de la arista 0..1 (para el pulso)
varying float vEdge;
varying float vSide;

vec3 morphPos(vec3 a, vec3 b, vec3 c, float m) {
  vec3 ab = mix(a, b, clamp(m, 0.0, 1.0));
  return mix(ab, c, clamp(m - 1.0, 0.0, 1.0));
}

void main() {
  vEdge = aEdge;
  vT = aT;
  vSide = aSide;

  // extremos morfeados (idénticos a como se mueven los nodos → las aristas los siguen)
  vec3 pa = morphPos(endA_A, endA_B, endA_C, uMorph);
  vec3 pb = morphPos(endB_A, endB_B, endB_C, uMorph);

  // repulsión del cursor aplicada al punto de este vértice (a o b) para que la arista
  // se doble con el nodo. Debe usar la MISMA fórmula que Nodes.tsx o se despegan.
  vec3 self = (aT < 0.5) ? pa : pb;
  vec3 toP = self - uPointer;
  float push = uPointerActive * smoothstep(2.4, 0.0, length(toP)) * 1.1;
  vec3 pushV = normalize(toP + 0.0001) * push;
  pa += (aT < 0.5) ? pushV : vec3(0.0);
  pb += (aT < 0.5) ? vec3(0.0) : pushV;

  vec3 worldSelf = (aT < 0.5) ? pa : pb;
  vec3 worldOther = (aT < 0.5) ? pb : pa;

  // proyectar ambos extremos a clip → NDC → pantalla, expandir perpendicular en px
  vec4 clipSelf  = projectionMatrix * modelViewMatrix * vec4(worldSelf, 1.0);
  vec4 clipOther = projectionMatrix * modelViewMatrix * vec4(worldOther, 1.0);

  vec2 ndcSelf  = clipSelf.xy  / clipSelf.w;
  vec2 ndcOther = clipOther.xy / clipOther.w;

  vec2 dir = normalize((ndcOther - ndcSelf) * uResolution);
  vec2 normal = vec2(-dir.y, dir.x);                 // perpendicular
  vec2 offset = normal * aSide * (uThickness / uResolution); // px → NDC

  clipSelf.xy += offset * clipSelf.w; // multiplicar por w para compensar la división de perspectiva
  gl_Position = clipSelf;
}
```

### 3.2 Fragment shader (línea base + PULSO viajero)

```glsl
// edge.frag
precision highp float;

uniform float uTime;
uniform vec3  uEdgeColor;   // color base tenue del cable
uniform vec3  uPulseColor;  // color del paquete (brillante)
uniform float uPulseSpeed;
uniform float uPulseWidth;  // ancho del gaussiano (0.04 = paquete corto)
uniform float uMorph;

varying float vT;    // 0..1 a lo largo de la arista
varying float vEdge;
varying float vSide;

void main() {
  // 1) línea base: más brillante en el centro del ribbon (borde suave = anti-alias barato)
  float edgeFall = smoothstep(1.0, 0.0, abs(vSide)); // vSide es -1/+1 interpolado → 0 en centro
  vec3 col = uEdgeColor;
  float alpha = 0.18 + 0.25 * edgeFall;

  // 2) EL PULSO: una gaussiana que recorre vT en 0..1, desfasada por arista.
  //    fract() la hace reaparecer (loop). offset por vEdge = cada cable pulsa en su tiempo.
  float head = fract(uTime * uPulseSpeed + vEdge * 0.137);
  float dist = abs(vT - head);
  // envolver el borde para que el pulso no "parpadee" al cruzar 0/1
  dist = min(dist, 1.0 - dist);
  float pulse = exp(-(dist * dist) / (uPulseWidth * uPulseWidth));

  // el pulso ilumina y ensancha (suma color brillante + sube alpha)
  col = mix(col, uPulseColor, pulse);
  alpha = clamp(alpha + pulse * 0.9, 0.0, 1.0);

  // durante el morphing, atenuar un poco las aristas para que dominen los nodos en movimiento
  float morphFade = 1.0 - 0.35 * smoothstep(0.0, 0.5, abs(fract(uMorph) - 0.5) * 2.0 - 0.0);
  alpha *= morphFade;

  gl_FragColor = vec4(col, alpha);
}
```

### 3.3 El material en R3F

```tsx
// src/components/three/graph/Edges.tsx
"use client";
import { useMemo, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { buildEdgeGeometry } from "./build-edges-geometry";
import { graphStore } from "./graph-store";
import edgeVert from "./edge.vert"; // ver nota de import de GLSL abajo
import edgeFrag from "./edge.frag";

export default function Edges() {
  const geo = useMemo(() => buildEdgeGeometry(), []);
  const mat = useRef<THREE.ShaderMaterial>(null);
  const { size, viewport } = useThree();

  const uniforms = useMemo(
    () => ({
      uTime:        { value: 0 },
      uMorph:       { value: 0 },
      uThickness:   { value: 2.4 },                 // px; 2.0–3.0 se ve "cable", no "hilo"
      uResolution:  { value: new THREE.Vector2(1, 1) },
      uPointer:     { value: new THREE.Vector3(999, 999, 999) },
      uPointerActive: { value: 0 },
      uEdgeColor:   { value: new THREE.Color(0.25, 0.45, 0.9) },
      uPulseColor:  { value: new THREE.Color(0.6, 1.0, 1.0) },
      uPulseSpeed:  { value: 0.35 },
      uPulseWidth:  { value: 0.05 },
    }),
    []
  );

  useFrame((state, dt) => {
    const u = mat.current!.uniforms;
    u.uTime.value = state.clock.elapsedTime;
    u.uMorph.value = THREE.MathUtils.damp(u.uMorph.value, graphStore.morph, 4, Math.min(dt, 0.1));
    // resolución en PÍXELES FÍSICOS (dpr incluido) — si no, el grosor varía entre pantallas
    u.uResolution.value.set(size.width * viewport.dpr, size.height * viewport.dpr);
    u.uPointer.value.copy(graphStore.pointer);
    u.uPointerActive.value = graphStore.pointerActive;
  });

  return (
    <mesh geometry={geo} frustumCulled={false}>
      <shaderMaterial
        ref={mat}
        vertexShader={edgeVert}
        fragmentShader={edgeFrag}
        uniforms={uniforms}
        transparent
        depthWrite={false}         // aristas translúcidas: no escriben depth → no se ocluyen feo
        blending={THREE.AdditiveBlending} // los cruces SUMAN luz → se ve "energía"
        toneMapped={false}         // imprescindible para que el Bloom agarre los pulsos
      />
    </mesh>
  );
}
```

**Import de GLSL sin CDN ni loader nuevo.** Next 14 no importa `.vert`/`.frag` como string por
defecto. Dos opciones **sin añadir deps de riesgo**:
1. **Inline** los shaders como template strings en el `.tsx` (lo más simple; cero config). Es lo
   que hace `Nodes.tsx` arriba. Recomendado para este proyecto.
2. Un `webpack` rule en `next.config.js` con `raw-loader`/`asset/source`. Añade config; sólo si
   los shaders crecen mucho. Por CSP no hay problema (es build-time, no runtime).

Para el portafolio: **inline**. Menos piezas, y el GLSL lo compila WebGL (no `eval`), así que la
CSP estricta ni se entera.

---

Sigo con la respiración/reacción al cursor (§4), el morphing por scroll (§5), bloom (§6) y perf.

## 4. Respiración y reacción al ratón

La **respiración** ya está en el vertex shader (`sin(uTime + aSeed)`): cada nodo orbita y
escala un pelín, desfasado, así el grafo nunca está "congelado". Cuesta 0 (una `sin` por
vértice).

La **reacción al cursor** necesita convertir el puntero 2D a un punto en el **plano del grafo**
en coordenadas de mundo, y meterlo en `graphStore.pointer`. Igual que en `webgl-craft.md`:
listener de `window`, **module-scope store, nunca setState**, y gate de `pointer: fine`.

```ts
// src/components/three/graph/graph-store.ts
import * as THREE from "three";
export const graphStore = {
  morph: 0,                         // 0..2, lo escribe ScrollTrigger (§5)
  pointer: new THREE.Vector3(999, 999, 999),
  pointerActive: 0,                 // 0/1
};
```

```tsx
// src/components/three/graph/PointerBridge.tsx  (componente vacío dentro del <Canvas>)
"use client";
import { useEffect } from "react";
import { useThree, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { graphStore } from "./graph-store";

// store 2D crudo alimentado por window (O(1), sin React)
const raw = { nx: 0, ny: 0, active: 0 };

export default function PointerBridge() {
  const { camera } = useThree();

  useEffect(() => {
    // touch / reduced-motion: ni registramos el listener
    if (!window.matchMedia("(pointer: fine)").matches) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const onMove = (e: PointerEvent) => {
      raw.nx = (e.clientX / window.innerWidth) * 2 - 1;
      raw.ny = -(e.clientY / window.innerHeight) * 2 + 1;
      raw.active = 1;
    };
    const onLeave = () => { raw.active = 0; };
    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("pointerout", onLeave, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerout", onLeave);
    };
  }, []);

  // cada frame: raycast del NDC al plano z=0 (el plano del grafo) → mundo
  const ray = useMemo(() => new THREE.Raycaster(), []);
  const plane = useMemo(() => new THREE.Plane(new THREE.Vector3(0, 0, 1), 0), []);
  const ndc = useMemo(() => new THREE.Vector2(), []);
  const hit = useMemo(() => new THREE.Vector3(), []);

  useFrame(() => {
    if (!raw.active) { graphStore.pointerActive = 0; return; }
    ray.setFromCamera(ndc.set(raw.nx, raw.ny), camera);
    if (ray.ray.intersectPlane(plane, hit)) {
      graphStore.pointer.copy(hit);
      graphStore.pointerActive = 1;
    }
  });
  return null;
}
```

> **Nota `useMemo` en cuerpo con hooks:** añade `import { useMemo } from "react";`. Están
> memoizados para no reasignar `Raycaster`/`Plane` cada frame.

La repulsión ya la aplican **tanto los nodos como las aristas** con la misma fórmula
(`smoothstep(2.4, 0.0, d) * 1.1`). Que sea **idéntica** en ambos shaders es lo que mantiene los
cables pegados a sus nodos cuando el cursor los empuja. Si las divergen, las aristas se
"despegan" — es el bug visual más común de este efecto.

**Atracción en vez de repulsión** (opción): invierte el signo (`-normalize(toP)`). Repulsión se
lee como "el sistema reacciona/se aparta"; atracción como "el cursor recoge datos". Para un
portafolio de arquitecto, **repulsión** comunica mejor "sistema vivo que responde". Elige una,
no ambas.

---

## 5. MORPHING por scroll — red neuronal → microservicios → constelación

La técnica ya está montada: las 3 posiciones están precomputadas en atributos, y el shader
lerpea con `uMorph ∈ [0,2]`. Sólo falta **atar `uMorph` al scroll** con el mismo patrón que ya
usa `Showcase3D.tsx` (ScrollTrigger `scrub` → store mutable, **nunca setState**).

```tsx
// src/components/portfolio/SystemSection.tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { graphStore } from "../three/graph/graph-store";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export default function SystemSection() {
  const section = useRef<HTMLElement>(null);

  useGSAP(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      graphStore.morph = 1; // layout de microservicios ESTÁTICO (el más legible) y se queda
      return;
    }
    ScrollTrigger.create({
      trigger: section.current,
      start: "top top",
      end: "bottom bottom",
      scrub: true,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        // progreso 0..1 → morph 0..2 (dos transiciones: A→B y B→C)
        graphStore.morph = self.progress * 2;
      },
    });
  }, []);

  // 3 "pantallas" de alto → 3 layouts. El grafo vive en el Canvas global de fondo;
  // aquí sólo van los TEXTOS que rotulan cada fase del morphing.
  return (
    <section ref={section} style={{ height: "300vh", position: "relative" }}>
      <div style={{ position: "sticky", top: 0, height: "100vh" }}>
        {/* textos por fase, revelados con el mismo patrón que Showcase3D */}
        <Caption at="0%"   title="Redes neuronales" sub="Modelos, embeddings, agentes LLM." />
        <Caption at="50%"  title="Microservicios"   sub=".NET · Node · colas · gateways · DBs." />
        <Caption at="100%" title="Sistemas vivos"   sub="Observables, desplegados, en producción." />
      </div>
    </section>
  );
}
```

**Por qué 3 layouts y no 5:** cada layout añade un `Float32Array` de posiciones (N×3 floats =
~1KB para 96 nodos — nada) pero **cada uno añade una decisión de diseño**. Tres cuentan una
narrativa clara (lo que ES la IA → lo que Cristian CONSTRUYE → el resultado). Cinco diluyen.
La escasez otra vez.

**Easing del morph:** el `damp` en `useFrame` (`damp(uMorph, graphStore.morph, 4, dt)`) ya
suaviza el scrub, así que aunque el usuario pegue un scroll violento, la transición no salta.
`scrub: true` + `damp` en el consumidor = el patrón correcto (lo mismo que hace `LaptopGLB`).

**Gotcha del lerp de layouts:** cuando dos nodos intercambian posiciones muy lejanas, el lerp
lineal los cruza por el centro y se ve un "colapso". Dos mitigaciones baratas:
- **Desfasar por nodo:** en el vertex, `float m = clamp(uMorph - aSeed*0.15, 0.0, 2.0);` — cada
  nodo llega un pelín después, y el colapso se vuelve una "ola" (se ve mejor, no peor).
- Para el layout intermedio (micro) usar posiciones que no estén todas en el origen evita el
  pinch. Ya está: `layoutMicro` reparte en anillos.

---

## 6. Emisivo + Bloom (que brille sin lavarse)

Todo lo que debe brillar va con `toneMapped={false}` (ya está en los tres materiales) y color
**> 1.0 en las zonas de pulso** (por eso `uExposure: 1.6` en nodos y el `uPulseColor` sumado en
aristas). El `Bloom` sólo agarra lo que supera su `luminanceThreshold`.

```tsx
// dentro del <Canvas>, después de la escena
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";

<EffectComposer multisampling={0}>
  <Bloom
    mipmapBlur                 // variante barata y moderna (ver webgl-craft.md §4)
    luminanceThreshold={0.6}   // SUBIR esto es lo que evita el "lavado": sólo pulsos/nodos brillan
    luminanceSmoothing={0.2}
    intensity={0.8}            // 0.6–1.0. Más de 1.2 y el grafo se vuelve una mancha
    radius={0.6}
  />
  <Vignette eskil={false} offset={0.25} darkness={0.7} /> {/* enfoca el ojo al centro del grafo */}
</EffectComposer>
```

**El error de lavado** viene de dos sitios, no del Bloom en sí:
1. **`luminanceThreshold` muy bajo** (0.2–0.3): entonces el Bloom agarra el color base tenue de
   las aristas y TODO florece → sopa. Súbelo a **0.55–0.65** para que sólo florezcan los pulsos
   y los núcleos de nodo.
2. **Fondo no negro.** Con `AdditiveBlending` en las aristas, si el fondo del canvas es claro,
   las sumas saturan a blanco. El grafo quiere fondo **oscuro** (`#05060a`–`#0a0b12`). Si el
   portafolio es claro, el grafo va en su propia sección de fondo oscuro, o las aristas usan
   `NormalBlending` (menos "energía", pero sobrevive fondo claro).

**Tono de color:** nodos y pulsos en la misma familia fría (teal/cian/azul) + un acento cálido
(ámbar en gateways) leen como "consola / telemetría de sistema". Evita el arcoíris: 2 colores
+ 1 acento, no 7.

---

## 7. Coste de perf honesto y degradación

### Coste real (estimaciones de ingeniería, NO medidas — mídelo con r3f-perf + un teléfono)

| Pieza | Desktop | Adreno gama media |
|---|---|---|
| 120 nodos (1 InstancedMesh, 42 verts c/u, shader trivial) | <0.3 ms | ~0.8 ms |
| 220 aristas ribbon + shader de pulso (fragment con 1 `exp`) | ~0.6 ms | ~2.5 ms |
| PointerBridge (1 raycast a un plano/frame) | ~0.02 ms | ~0.05 ms |
| Bloom mipmapBlur + Vignette | ~1.2 ms | ~2.5–4 ms |
| **Total escena** | **~2–3 ms** | **~6–9 ms** |

Margen sano en desktop; **ajustado en móvil** (presupuesto ~16 ms a 60fps, pero el navegador y
el compositing ya se comen parte). Por eso el ladder no es opcional.

### Ladder de degradación (drei `PerformanceMonitor`, igual que webgl-craft §6)

```tsx
import { PerformanceMonitor } from "@react-three/drei";
const [tier, setTier] = useState(2);

<PerformanceMonitor
  onDecline={() => setTier((t) => Math.max(0, t - 1))}
  onIncline={() => setTier((t) => Math.min(2, t + 1))}
>
  {/* tier 2: 120 nodos, todas las aristas con pulso, Bloom+Vignette, dpr 1.75 */}
  {/* tier 1: 80 nodos, pulso en 1 de cada 2 aristas, Bloom solo, dpr 1.25   */}
  {/* tier 0: 40 nodos, SIN pulso (aristas estáticas tenues), SIN Bloom, dpr 1 */}
</PerformanceMonitor>
```

**Cómo se aplica el tier sin recompilar shaders:** no cambies el número de instancias en runtime
(recrea buffers = jank). En su lugar:
- **Nodos:** deja los 120 instanciados siempre; en tier bajo, usa `mesh.count = 40` (three
  respeta `count < maxCount` y dibuja sólo las primeras) — **cero realloc**.
- **Pulso:** un uniform `uPulseEnabled` (1/0) y `uPulseDensity`; en el fragment, `if
  (mod(vEdge,2.0) > 0.5) pulse *= uPulseDensity;`.
- **dpr:** `<Canvas dpr={[1, tier >= 2 ? 1.75 : tier === 1 ? 1.25 : 1]}>` — pero cambiar dpr
  recrea el drawing buffer; hazlo sólo en saltos de tier, no cada frame.
- **Bloom:** condicional `{tier >= 1 && <Bloom .../>}`.

### Reduced motion / touch (congelar, no ocultar)

- `prefers-reduced-motion`: `graphStore.morph = 1` fijo (layout de microservicios, el más
  legible), `uTime` congelado (pasa `dt=0` o no actualices `uTime`), pulsos quietos. **El grafo
  estático sigue siendo bello** — es un diagrama de arquitectura limpio. No lo desmontes.
- Touch: `PointerBridge` ni registra listener (`pointer: fine` gate). El grafo respira y morfea
  con scroll, pero no hay repulsión (no hay cursor). Correcto: en móvil el dedo ES el scroll.
- **LCP:** el grafo va en `next/dynamic({ ssr: false })` dentro del Canvas de fondo que ya
  existe; el `<h1>` server-rendered sigue siendo el LCP. El grafo **nunca** debe ser el LCP.

---

## Integración en ESTE proyecto (portafolio-frontend)

- Reusa el **Canvas de fondo global** que ya existe (`Scene3DBackground.tsx`) — no montes un
  segundo `<Canvas>` (dos contextos WebGL = doble coste y peleas de memoria). Añade
  `<Nodes/>`, `<Edges/>`, `<PointerBridge/>` a esa escena, condicionados a que la sección
  `#system` esté en viewport (usa `graphStore.morph` sólo cuando esa sección manda).
- Reusa el **patrón de store** existente: `graph-store.ts` es hermano de `scroll-store.ts`, misma
  filosofía (module-scope mutable, leído en `useFrame`, escrito por ScrollTrigger).
- `SystemSection.tsx` es hermano de `Showcase3D.tsx`: misma mecánica de `ScrollTrigger` `scrub`.
- **El laptop puede convivir**: hero = laptop (acento personal), sección system = grafo (el
  argumento). O jubila el laptop si el grafo ya carga la narrativa. Decisión de diseño, no técnica.

---

## Honestidad obligatoria (REGLA #6)

- **No medido.** Todos los ms de arriba son estimaciones de ingeniería por conteo de
  draw-calls/vértices/fill-rate. Hay que correr `r3f-perf` y un **Android real con throttle** antes
  de cantar victoria. "Corre en mi máquina" no es evidencia (lo dice el propio SKILL.md).
- **GLSL sin compilar en navegador aquí.** El shader de pulso y el de grosor screen-space están
  escritos para compilar, pero **no los ejecuté en un WebGL real** en esta sesión. Riesgo típico:
  un `varying` mal interpolado (el `vSide` para el anti-alias) o el signo del offset perpendicular
  invertido (ribbon del lado equivocado → línea de 0px). Primer paso al integrar: un grafo de **3
  nodos y 2 aristas** para validar grosor y pulso antes de meter los 120.
- **El grosor screen-space tiene un caso feo:** aristas casi paralelas a la cámara (vistas de
  canto) donde `ndcOther - ndcSelf ≈ 0` → `normalize` de casi-cero → NaN → triángulo degenerado
  que parpadea. Mitigación: `if (length(d) < 1e-4) d = vec2(1.0, 0.0);` antes de normalizar. Lo
  omití arriba por brevedad; **añádelo**.
- **Lo que NO construí y por qué:** (a) *labels de texto por nodo* — texto en 3D (troika/drei
  `<Text>`) es caro y en móvil se vuelve sopa; mejor labels DOM sobre los 4-5 nodos clave,
  posicionados por proyección. (b) *Física real de fuerzas* (d3-force en runtime) — mata el frame
  en móvil y no aporta sobre los layouts precomputados. (c) *Aristas curvas (bezier)* — bonitas
  pero triplican vértices por arista; rectas + pulso ya leen "vivo".
- **Sobrevalorado en esta familia de efectos:** grafos de fuerza que "se acomodan solos" al
  cargar (se ve genérico, de librería, y cuesta CPU), y nodos con `MeshTransmissionMaterial`
  (glass) — refractan el fondo negro, o sea nada, y cuestan un render pass extra. Nodos emisivos
  planos + bloom se ven mejor y cuestan una fracción.

## Oportunidades de mejora

1. **Instancing también en las aristas.** Ahora mismo la geometría de ribbons es un solo
   `BufferGeometry` con todos los quads — funciona y es 1 draw call, pero reconstruirla al cambiar
   la topología obliga a recrear buffers. Si el grafo se vuelve dinámico (nodos que aparecen),
   migra a `InstancedMesh` de segmentos con matriz por arista. Para un grafo estático como este,
   no hace falta — sería sobre-ingeniería.
2. **Pulsos dirigidos por datos reales.** Hoy los pulsos son decorativos (fase por `aEdge`). El
   siguiente nivel: que un pulso "nazca" en un nodo input y llegue a un output siguiendo un
   camino real del grafo, disparado al hacer hover en un nodo. Es el salto de "bonito" a "cuenta
   una historia de flujo de datos" — pero cuesta un sistema de scheduling en JS. Evalúa si el ROI
   lo justifica antes de construirlo.
3. **Medir de verdad antes de subir a producción.** Es el punto #4/#5 del CLAUDE.md: nada se da
   por hecho sin verificar ejecutando. Grafo de 3 nodos → validar shaders → subir a 120 → medir en
   Android → ajustar el ladder. En ese orden.

# Cinematic Hero 2026 — receta canónica (ORO, aprobada 2026-07-15)

> **Este es el DEFAULT del frontend de Cristian para TODA página/landing/proyecto** (memoria
> `feedback-frontend-cinematic-standard`). Un héroe cinematográfico: UN objeto 3D
> art-directed + cámara que viaja con el scroll + video/persona integrado por luma-key,
> con **RESTA**. Implementación de referencia: repo `cdgutierrez6/portafolio-frontend`,
> tag `hero-cinematic-oro-v1`. Adaptar tema/paleta/objeto/video; el MÉTODO y la estructura
> no cambian.

## 0. La ley: RESTA. "Mucho ≠ bueno."
Un solo foco, muchísimo negative space, nada de apilar efectos additive (partículas + trazo
+ caústicas + piso-espejo = SOPA, rechazada). Igloo/Oryzo/Lusion/dgreenheck ganan por sustracción.
Si dudas, quita hasta que se rompa.

## 1. Stack (pineado, React 18)
`next@14` · `@react-three/fiber@8.18` · `@react-three/drei@9.x` · `three@0.171` ·
`@react-three/postprocessing@2.19` · `gsap` + `lenis`. NO subir a R3F v9 / drei v10 /
postprocessing v3 (exigen React 19). CSP estricta, $0.

## 2. Escena (Scene3DBackground) — la LUZ primero (80/20)
```tsx
<Canvas gl={{ antialias:false, alpha:true,
  toneMapping: THREE.ACESFilmicToneMapping,   // sin ACES los brillos clipean a blanco
  toneMappingExposure: 0.82,                   // bajo → ACES no empuja highlights a AMARILLO
  outputColorSpace: THREE.SRGBColorSpace }}>
  <PerspectiveCamera makeDefault fov={40} position={[0,0,6]} />
  <fog attach="fog" args={["#07080d", 5, 16]} />          {/* el AIRE */}
  <pointLight position={[-3.5,2.5,2]} intensity={90} color="#6E8BFF" />  {/* UNA luz de acento */}
  <CameraRig />                                            {/* la cámara VIAJA (ver §4) */}
  <Suspense fallback={null}>
    <HeroArtifact />                                       {/* el objeto (ver §3) */}
    <FaceReveal />                                         {/* video/persona (ver §5) */}
    <ContactShadows position={[obj.x,-1.25,0]} scale={7} blur={2.6} opacity={0.4} far={4.5} color="#000" />
    <EffectComposer>                                       {/* capa fotográfica = "cine" */}
      <DepthOfField target={dofTarget} focalLength={0.03} bokehScale={2.5} height={480} />
      <Bloom intensity={0.7} luminanceThreshold={0.9} luminanceSmoothing={0.2} mipmapBlur />
      <Noise premultiply blendFunction={BlendFunction.SOFT_LIGHT} opacity={0.05} />
      <Vignette eskil={false} offset={0.3} darkness={0.55} />
    </EffectComposer>
  </Suspense>
</Canvas>
```

## 3. El objeto héroe (HeroArtifact)
- Geometría: modelo Blender ($0, script Python → GLB **sin draco**) o primitiva. Cargar con
  `useGLTF("/models/x.glb")` (self-host, mismo origen).
- Material: `<MeshTransmissionMaterial>` con **rango disciplinado** — `chromaticAberration 0.04`
  (NUNCA 0.7), `distortion 0` (el wobble abarata), `ior 1.5`, `roughness 0.02`, `samples 10`,
  `resolution 512`, `backside`.
- **Entorno = Lightformers procedurales blanco-frío** (softboxes), NO HDRI de ciudad/dawn
  (tienen luces cálidas → hotspots que ACES vuelve amarillo). Intensidades DOMADAS (~1–1.5).
  Si usas HDRI: self-host como **archivo .exr** (`/public/hdri/x.exr`) — el data-URI base64
  de `@pmndrs/assets` ROMPE bajo CSP (EXRLoader hace `fetch(data:)` bloqueado).
- **Sobre negro el vidrio necesita algo que refractar/emitir** o desaparece: UNA brasa
  interior suave (esfera emissive additive pequeña), no una nube de puntos.
- Posición off-center (ej. derecha) para que el titular colosal respire al lado.

## 4. Cámara cinematográfica (el ALMA) — CameraRig
La cámara VIAJA por beats; progreso **relativo al viewport** (`scrollY/innerHeight`), NO
`scrollStore.page` (que abarca la página entera y mete los beats muy adentro).
```tsx
const hp = window.scrollY / (window.innerHeight || 1);
const a = smoothstep(clamp(hp/0.6));          // Beat 1: dolly-in al objeto (z 6→3.8)
const b = smoothstep(clamp((hp-0.6)/0.7));    // Beat 2: track lateral a la cara
// damp cada eje en useFrame; lookAt interpola objeto→cara; NUNCA setState en el loop.
dofTarget.lerpVectors(OBJETO, CARA, b);       // DoF enfoca el SUJETO ACTIVO
```
Micro-parallax al cursor como capa aditiva sutil (amplitud ~0.22), off bajo reduced-motion.
**PENDIENTE conocido:** para que no haya "hueco negro" en la transición y no pise el
contenido, el arco debe vivir en un CONTENEDOR dedicado ~300vh ANTES de las secciones
(patrón Codrops Cinematic3DScroll) — TODO del portafolio.

## 5. Video/persona INTEGRADO (FaceReveal) — no pegado
- Cristian graba/genera el clip **sobre fondo NEGRO plano** (Gemini/Veo: "pure black bg,
  soft frontal light, subtle head motion"). El negro permite **luma-key sin codec alfa**
  (imposible en Windows).
- ffmpeg → `yo.webm`(VP9) + `yo.mp4`(H.264) + `yo-poster.webp`, self-host en `/public/media`.
- Plano R3F con `useVideoTexture("/media/yo.mp4",{muted,loop,start:true,playsInline})` +
  shader: **luma-key** (`alpha = smoothstep(0.05,0.20,luma)`) + **duotono al acento** (piel
  atada al ambiente = escultura, no selfie) + reveal de abajo→arriba con dither.
- Comparte el MISMO EffectComposer → grade (DoF/grano/viñeta/ACES) automático. Ese pipeline
  compartido ES la diferencia integrado-vs-pegado. Gotcha iOS: `start:true` (si no, textura negra).

## 6. Método (obligatorio) y gotchas de verificación
1. **Investigar referencias PRIMERO** (las de Cristian + dgreenheck/Codrops/Lusion/Igloo/Oryzo),
   reference board mirado con OJOS. No construir sobre suposiciones.
2. **Una palanca a la vez + feedback VISUAL.** El objeto sobre negro puede parecer roto y ser
   solo falta de luz o un scale-a-0 por scroll — VERIFICAR antes de rediseñar.
3. **VERIFICACIÓN — el tab oculto pausa el rAF de R3F → falso-negro.** El Browser pane y el
   screenshot de la extensión sobre un tab de fondo dan negro. Usar **Chrome REAL al frente**
   (`computer-use open_application` + screenshot del monitor) para render continuo. Alternativa
   rápida: extensión screenshot cuando el tab YA está al frente.
4. Gates: LCP<2.5s / INP<200ms / 60fps + fallback móvil (bajar samples/quitar transmission+DoF)
   + reduced-motion (poster estático). Revisión adversarial + llm-judge antes de prod.

## 7. Adaptar a otras páginas
El objeto, la paleta (mantener 3 tokens: bg near-black + text off-white + 1 acento), el video
y el tema cambian por proyecto. La ESTRUCTURA (objeto art-directed + cámara-scroll + video
luma-key + RESTA + capa fotográfica) es el molde fijo. Web-design-pro-2026 orquesta esto como
default del hero de cualquier página.

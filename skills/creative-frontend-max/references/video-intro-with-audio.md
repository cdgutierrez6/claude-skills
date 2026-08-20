# Intro de video a pantalla completa CON AUDIO (autoplay sin bloqueo del navegador)

> Cómo hacer una **intro cinematográfica de video** que abre una página: se reproduce sola,
> lleva **audio**, y hace hand-off al hero. Patrón probado en **taller-ejemplo**
> (`apps/web/.../shared/ui/intro-screen`) y en **portafolio-frontend** (`components/portfolio/Preloader.tsx`).
> Aplica a cualquier landing/portafolio. Ver también [[cinematic-hero-2026]].

## La regla de oro del audio (por qué NO se bloquea)

Los navegadores **bloquean** el autoplay CON sonido sin un gesto del usuario, pero **permiten**
el autoplay **muted**. Solución (la que usa taller-ejemplo):

1. El `<video>` arranca **`muted autoplay playsinline`** → el navegador NUNCA bloquea el autoplay.
2. Un **botón de sonido** hace **`video.muted = false` IMPERATIVO** al hacer clic. Ese clic ES el
   "gesto de usuario" que habilita el audio que estaba bloqueado.
3. **CRÍTICO:** NO togglear el mute con la prop declarativa (`muted={state}` en React o `[muted]`
   en Angular) — rompe el autoplay. Se toca `videoEl.muted` **imperativamente** sobre el elemento.

```tsx
// React (portafolio): arranca muted, el botón lo activa.
const [muted, setMuted] = useState(true);
const toggleSound = () => { const v = video.current; if (!v) return; v.muted = !v.muted; setMuted(v.muted); };
// <video ref={video} muted autoPlay playsInline ...>  +  <button onClick={toggleSound}>🔊 Sonido</button>
```

## Hand-off que NUNCA corta el video ni atrapa al visitante

El cierre lo manda el **`onEnded` del propio video** (garantía de que se ve completo), NO un
cronómetro ciego desde el montaje (ese fue un bug real: si el video buffea y arranca tarde, un
`setTimeout(finish, 11500)` desde mount corta el final).

- `onPlaying` → arma un **safety** anclado al **inicio REAL**: `setTimeout(finish, duration*1000 + 2500)`.
  Solo dispara si `onEnded` no llega (video colgado). El buffering ya no come del final.
- **watchdog** (~7s desde mount): si el video NUNCA arranca (`currentTime < 0.1`) → hero, sin atrapar.
- `onError` → `finish()`. Nunca dejar el overlay colgado.
- `onVideoReady`/`loadeddata` → `v.play().catch(()=>{})` (refuerzo: a veces el autoplay no dispara
  en un `<video>` insertado dinámicamente).

## PERF CRÍTICO — apagar WebGL / escenas pesadas DURANTE la intro (el tropiezo #1)

Si la página tiene un **hero WebGL/R3F** (cristal `MeshTransmissionMaterial`, piso reflector,
`EffectComposer`…), ese canvas **NO debe renderizar mientras corre la intro de video**: aunque
esté DETRÁS del overlay opaco (invisible), renderiza a tope y **ahoga el decode del video
(stutter) + bloquea el main thread (los clicks no responden)**. Taller Ejemplo no tiene WebGL →
su intro es fluida; una página con WebGL se traba feo si no se apaga.

**Fix:** montar el 3D **sólo cuando la intro termina**, no antes. La escena escucha el mismo
`onIntroDone` que dispara `markIntroDone()`:

```tsx
// Scene3DBackgroundClient.tsx — NO montar el <Canvas> hasta el hand-off de la intro.
const unsub = onIntroDone(() => {
  timeoutId = window.setTimeout(() => setMount(true), 200); // LCP ya pasó → timeout simple y
});                                                          // fiable (rIC se throttlea en bg)
return () => { unsub(); clearTimeout(timeoutId); };
if (!mount) return null;
```

Durante la intro: `document.querySelectorAll('canvas').length === 0`. Tras el hand-off: monta.
(Alternativa si prefieres mantenerlo montado: R3F `frameloop="never"` durante la intro y
`"always"` tras `markIntroDone` — pero no-montar es más simple y evita el costo de compilar
shaders en plena intro.)

## ¿Siempre o una vez por sesión? (configurable — preguntarle a Cristian)

- **Una vez por sesión** (taller-ejemplo): `localStorage`/`sessionStorage` con una llave; si existe → skip.
- **Siempre al recargar** (portafolio, pedido explícito de Cristian): **sin** esa llave. Solo
  `prefers-reduced-motion` la salta (accesibilidad). "Siempre" = cada reload la muestra.

## Responsive "cuadra bien" en móvil (video 16:9 sobre pantalla portrait)

Un 16:9 full-screen en portrait con `cover` recorta ~74% del ancho. Patrón taller-ejemplo:

- **Desktop/landscape:** `.intro-video { object-fit: cover }` → full-bleed inmersivo.
- **Móvil/portrait:** `object-fit: contain` (composición 16:9 completa) + un **`.intro-fill`**
  detrás = el **poster ampliado y DESENFOCADO** (no franjas negras):

```css
.intro-video { object-fit: cover; object-position: center; }
.intro-fill { display: none; }
@media (orientation: portrait) {
  .intro-video { object-fit: contain; }
  .intro-fill {
    display: block;
    background: #050505 url("/media/intro-poster.webp") center center / cover no-repeat;
    filter: blur(26px) brightness(0.45) saturate(1.1);
    transform: scale(1.25);
  }
}
```

## Assets (transcode) — OJO con el audio

- **mp4** H.264 + **AAC** (Safari/iOS). Origen suele venir así (Veo/Gemini exporta con AAC).
- **webm** VP9 + **Opus** — `-c:a libopus -b:a 128k`. **NO usar `-an`** si el audio importa
  (error que cometí: la 1ª pasada con `-an` dejó el webm mudo → hubo que rehacerlo).
  `ffmpeg -y -i intro.mp4 -c:v libvpx-vp9 -b:v 0 -crf 34 -deadline good -cpu-used 2 -row-mt 1 -c:a libopus -b:a 128k intro.webm`
- **poster** webp (frame representativo oscuro) → sin flash blanco al cargar + es el fill móvil.
- Orden de `<source>`: webm primero (más liviano), mp4 de respaldo.

## Playbook de DEBUG (los 3 tropiezos que hay que evitar)

**1. NO se puede verificar playback/jank en pestaña de fondo o Browser pane.** Chrome (a) pausa el
video-only muted en background ("video-only background media was paused to save power" =
`AbortError` — el video avanza ~3s y se pausa) y (b) throttlea WebGL, `requestIdleCallback` y
timers. Resultado: el jank de WebGL **no se satura ahí** y "verificás" cosas que en foreground
están rotas. **La prueba real la hace el usuario en su navegador al frente** (o claude-in-chrome
con la pestaña activa). Con automatización sólo confirmá cosas deterministas: presencia de
`<canvas>`, hidratación (fibers), `getComputedStyle`, hit-test de botones (`elementFromPoint`).

**2. "Nada interactivo" (botones no responden + onEnded no dispara + no hay hand-off) = fallo de
HIDRATACIÓN, no un bug del handler.** Diagnóstico en orden:
   - ¿Los botones tienen fibers? `Object.keys(btn).some(k=>k.startsWith('__reactProps$'))` → `false` = React NO hidrató.
   - ¿Corrió algún `useEffect`? (p.ej. `document.body.style.overflow` debería ser `hidden`).
   - **Red:** `_next/static/chunks/*.js` → si dan **503/404**, React nunca arranca. Causa típica ↓.

**3. NUNCA corras `next build` (producción) mientras `next dev` está vivo.** Ambos escriben la
misma carpeta `.next` → la corrompés → el dev server sirve **503** en los chunks → hidratación
muerta → nada funciona (y "verificás" sobre eso sin saberlo). **Fix:** parar el dev, `rm -rf .next`,
re-arrancar. Si necesitás un build de prod, **pará el dev primero**. Tras arreglar, el navegador
del usuario quedó con la versión rota cacheada → decile **`Ctrl+Shift+R`** (hard reload).

Verificar render/encuadre/botones con screenshot en Chrome real; el playback completo + audio los
confirma el usuario en su navegador al frente.

## Layout base del overlay

`position:fixed; inset:0; z-index:9999; background:#050505`. Capas: `.intro-fill` (z0) → `<video>`
(z1) → viñeta radial `pointer-events:none` (z2, funde bordes a negro para el hand-off) → botones
Sonido (abajo-izq) / Saltar (abajo-der) (z3). Fade de salida: `opacity 1→0` + `scale 1→1.06`,
`markIntroDone()` al inicio del fade (el hero arranca su titular mientras el overlay se disuelve).
Bloquear `document.body.style.overflow='hidden'` durante la intro; liberar al cerrar.

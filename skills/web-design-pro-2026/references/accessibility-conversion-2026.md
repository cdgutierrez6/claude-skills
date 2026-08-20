# Accesibilidad + Conversión 2026 — Referencia senior

> Referencia operativa para landings y apps web en 2026. Dos partes: **A) Accesibilidad (WCAG 2.2 + EAA)** y **B) Conversión (incl. tráfico pagado/ads)**. Cierra con un **checklist combinado a11y + CRO**.
> Regla de oro: apunta a **WCAG 2.2 nivel AA**, no 2.1. Los números marcados como *ilustrativo* vienen de estudios de caso — úsalos como motivación, nunca como promesa a un cliente.

---

# PART A — Accesibilidad 2026

## A.0 — Qué cambió: WCAG 2.2 vs 2.1

WCAG 2.2 (recomendación W3C) **agrega 9 criterios de éxito** y **elimina 4.1.1 Parsing** por obsoleto. Certifica contra 2.2.

**Los 9 SC nuevos:**

| SC | Nombre | Nivel | Qué exige (resumen) |
|---|---|---|---|
| 3.2.6 | Consistent Help | **A** | Mecanismo de ayuda en la misma posición relativa entre páginas |
| 3.3.7 | Redundant Entry | **A** | No re-pedir datos ya ingresados en el mismo proceso |
| 2.4.11 | Focus Not Obscured (Min) | **AA** | El foco de teclado no queda totalmente oculto por overlays |
| 2.5.7 | Dragging Movements | **AA** | Toda interacción de arrastre necesita alternativa de un solo puntero |
| 2.5.8 | Target Size (Min) | **AA** | Targets de puntero ≥ 24×24 px CSS (o spacing equivalente) |
| 3.3.8 | Accessible Auth (Min) | **AA** | Sin test cognitivo sin asistencia en login/signup |
| 2.4.12 | Focus Not Obscured (Enhanced) | AAA | El foco no queda ni parcialmente oculto |
| 2.4.13 | Focus Appearance | AAA | Indicador de foco ≥ 2px de perímetro, ≥ 3:1 de contraste de área |
| 3.3.9 | Accessible Auth (Enhanced) | AAA | Sin excepción de reconocimiento de objetos |

**4.1.1 Parsing eliminado:** las tecnologías asistivas ya no parsean HTML directamente y los navegadores recuperan markup malformado. **No reportes IDs duplicados ni HTML inválido como falla WCAG.** (Siguen siendo mala higiene, pero no son un fallo de conformidad.) (W3C WAI, *What's New in WCAG 2.2* + *Understanding 4.1.1 Obsolete*, https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)

Objetivo práctico: **AA contra 2.2**. Los 6 SC de nivel A/AA nuevos (3.2.6, 3.3.7, 2.4.11, 2.5.7, 2.5.8, 3.3.8) son los que "muerden" en producción — los tres AAA son opcionales pero baratos si ya tienes buen foco.

---

## A.1 — Target Size (2.5.8, AA)

- **Piso WCAG:** cada target de puntero ≥ **24×24 px CSS**, o con **24px de offset** de separación entre centros si son más pequeños.
- **El padding cuenta** para el tamaño del target (no solo el contenido visible).
- **Excepciones:** enlaces inline dentro de una oración, y controles nativos del navegador (select, date picker).
- **Convención de diseño (más estricta):** apunta a **44×44 px en móvil** (Apple HIG 44pt). Es un "aim", no el piso WCAG.

```css
/* Botón/enlace táctil seguro */
.btn, .icon-link {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px; /* el padding cuenta hacia el target */
}
/* Si el visual debe ser pequeño, expande el área clickeable */
.small-toggle { position: relative; }
.small-toggle::before {
  content: ""; position: absolute; inset: -10px; /* llega a ~44px */
}
```

## A.2 — Focus Not Obscured (2.4.11, AA)

El foco de teclado **no puede quedar totalmente tapado** por headers sticky, barras de cookies o widgets de chat. Ofensor #1: overlays `position: sticky/fixed`.

**Fix estándar:** `scroll-padding-top` igual a la altura del header sticky.

```css
:root { --sticky-h: 64px; }
html { scroll-padding-top: var(--sticky-h); }
```

> Nota CRO: un CTA sticky en móvil puede tapar el foco → esto ata la sección B (CTA sticky) directamente a 2.4.11. Verifica tabulando hasta los campos cercanos al borde.

## A.3 — Dragging Movements (2.5.7, AA)

Toda interacción de **arrastre** necesita una alternativa de **un solo puntero (click/tap)**:

| Patrón con drag | Alternativa obligatoria |
|---|---|
| Range slider | Botones +/− o input numérico |
| Comparador antes/después | Botones o tap para alternar |
| Reordenar por drag | Botones subir/bajar |
| Carrusel por swipe | Botones prev/next |

**Excepción:** cuando el arrastre es esencial (dibujo, firma). No hay que dar alternativa ahí.

## A.4 — Accessible Authentication (3.3.8, AA)

**No** puedes exigir un **test de función cognitiva sin asistencia** en login/signup (recordar, transcribir, resolver puzzles).

**DO / DON'T:**

| DO | DON'T |
|---|---|
| Permitir **paste** en campos OTP y password | Bloquear pegar en OTP/password |
| `autocomplete` tokens → deja actuar al password manager | Deshabilitar autofill |
| Passkeys, magic-link, OAuth/SSO | CAPTCHA de **texto distorsionado** (falla) |
| — | Tests de **matemática/memoria** (fallan) |

**Matiz importante (corrige un error común):** los CAPTCHA de **reconocimiento de objetos** ("selecciona todos los autos") son una **EXCEPCIÓN explícita** a 3.3.8 Min — **pasan sin necesitar ruta alternativa**. Lo que **falla** es la transcripción de texto distorsionado y los tests de memoria/cálculo. No presentes "reconocer objetos" como violación. (W3C, *Understanding 3.3.8*, https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html)

```html
<input type="password" autocomplete="current-password" />
<input inputmode="numeric" autocomplete="one-time-code" /> <!-- OTP pegable -->
```

## A.5 — Redundant Entry (3.3.7, A) + Consistent Help (3.2.6, A)

Ambos son **nivel A** (la barra más baja — no tener esto es indefendible).

- **3.3.7:** no re-pedir datos ya ingresados en el mismo proceso. Auto-popula o da un "igual que facturación".
- **3.2.6:** el mecanismo de ayuda (contacto, chat, FAQ) va en la **misma posición relativa** en todas las páginas del flujo.

## A.6 — Contraste (1.4.3 texto / 1.4.11 no-texto)

| Elemento | Ratio mínimo |
|---|---|
| Texto de cuerpo | **4.5:1** |
| Texto grande (≥ 24px normal o ≥ 18.66px/14pt **bold**) | **3:1** |
| Componentes UI (bordes de input, íconos activos) | **3:1** |
| Indicador de foco | **3:1** |

Fallos frecuentes y reales: `#999` sobre `#fff` ≈ **2.8:1** (falla cuerpo). Placeholder gris como si fuera label. (WebAIM, *Contrast and Color Accessibility*, https://webaim.org/articles/contrast/)

## A.7 — Foco visible (`:focus-visible`) — 2.4.7 (AA) / 2.4.13 (AAA)

**Nunca** `outline: none` sin reemplazo → falla 2.4.7 AA. Usa `:focus-visible` para limitar el anillo al usuario de teclado (no dispara en click de mouse).

```css
:focus-visible {
  outline: 3px solid #1a73e8;   /* ≥2px, contraste ≥3:1 vs fondo */
  outline-offset: 2px;
  border-radius: 3px;
}
/* NO hagas esto sin reemplazo: */
/* button:focus { outline: none; } */
```

2.4.13 (AAA) especifica el objetivo de ≥2px de perímetro y ≥3:1 de área. (Sara Soueidan, *A guide to designing accessible focus indicators*.)

## A.8 — `prefers-reduced-motion` — seguridad vestibular, no polish

No es opcional. Ata a 2.3.3 (AAA, animación por interacción) y **2.2.2 (AA, movimiento automático > 5s debe poder pausarse)**. Reset base:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .001ms !important;
    scroll-behavior: auto !important;
  }
}
/* Y activa lo no-esencial solo con no-preference: */
@media (prefers-reduced-motion: no-preference) {
  .parallax { /* efecto opcional */ }
}
```

## A.9 — Formularios accesibles

| DO | DON'T |
|---|---|
| Label visible **persistente** | Placeholder como único label (falla 3.3.2) |
| Asociación programática (`for`/`id`) | Label suelto sin `for` |
| Error inline en **texto** + ícono | Error solo por color (falla 1.4.1) |
| `autocomplete` tokens (satisface 1.3.5, dispara autofill) | Campos sin `autocomplete` |
| `fieldset`/`legend` para grupos (radio/checkbox) | Grupos sin agrupar semánticamente |

```html
<label for="email">Correo</label>
<input id="email" type="email" autocomplete="email"
       aria-describedby="email-err" aria-invalid="true" />
<p id="email-err" role="alert">Ingresa un correo válido (ej: nombre@dominio.com).</p>
```

## A.10 — ARIA: errores comunes (First Rule of ARIA)

**"No ARIA is better than bad ARIA."** Prefiere HTML nativo.

| DON'T (ARIA roto) | DO (nativo) |
|---|---|
| `role="landmark"` (inválido) | `<header> <nav> <main> <footer>` |
| `<nav role="navigation">` (redundante) | Solo `<nav>` |
| `aria-label` en `<div>` no interactivo (ignorado) | `aria-label` solo en interactivos/landmarks |
| Varios `<main>` | **Un solo** `<main>` por página |
| Botón de ícono sin nombre | `<button aria-label="Cerrar">✕</button>` |
| Imagen decorativa con alt descriptivo | `alt=""` o `aria-hidden="true"` |

(MDN ARIA; W3C ARIA Authoring Practices.)

## A.11 — European Accessibility Act (EAA) — obligación legal 2026

| Ítem | Detalle |
|---|---|
| **Vigencia** | **28 de junio de 2025** (enforcement iniciado) |
| **A quién obliga** | Cualquier org que **venda a consumidores en la UE**, sin importar su ubicación (incluye US y LATAM). Un SaaS colombiano vendiendo a consumidores UE **está en scope**. |
| **Exención microempresa (servicios)** | < 10 empleados **Y** ≤ €2M de facturación |
| **Estándar técnico** | **EN 301 549** → mapea a **WCAG 2.1 AA** (2.2 es superset, por eso apuntar a 2.2 AA te cubre) |
| **Sanciones** | Fijadas por cada estado miembro; citadas hasta **€100k o 4% de ingresos** |

Relevante para productos EU-facing de Cristian: si vendes suscripción a consumidores en la UE, la exención por microempresa aplica solo si cumples **ambos** umbrales. (European Commission / AccessibleEU; Level Access.)

---

# PART B — Conversión de landing 2026 (incl. tráfico pagado)

## B.0 — Principio rector

Para tráfico pagado: **una página, un objetivo, un CTA, sin nav.** Cada peso de ad que llega a una página con fugas (nav global, footer cargado, CTAs que compiten) es peor Quality Score → mayor CPC.

## B.1 — Hero / propuesta de valor

El visitante juzga relevancia en **segundos** (heurística ~5–10s, *no* un límite duro — trátalo como dirección, no como ley; NN/g soporta un window de primera impresión, no un "5s" exacto).

**DO:**
- **H1 benefit-first** que diga **qué / para quién / beneficio**, visible sobre el fold en móvil (**fold de 375px**).
- Subhead que concrete el cómo.
- **Un** CTA sobre el fold.
- **Message-match** con el anuncio (ver B.5).

**DON'T:**
- Headline abstracto tipo "Reimaginamos el futuro".
- Hero de 3 CTAs compitiendo.
- Carrusel auto-rotante como hero (mata conversión + accesibilidad, ver B.8).

## B.2 — CTA: diseño y ubicación

**Consenso CRO (cualitativo, correcto):**

| DO | DON'T |
|---|---|
| **Un** CTA primario de alto **contraste** e isolación | "El color X siempre gana" (mito — manda el **contraste**, no el tono) |
| Repetir el CTA tras cada bloque persuasivo en páginas largas | Un solo CTA enterrado al fondo |
| Label **específico de acción** ("Pide tu cotización gratis") | "Enviar" / "Click aquí" |
| Copy en **primera persona** ("Quiero mi diagnóstico") | Copy genérico impersonal |
| CTA sticky en móvil **si no tapa contenido** | Sticky que oculta el foco (choca con 2.4.11) |

**Dato duro (verificado, Unbounce, 18.639 páginas):** páginas de **un solo CTA ~13.5%** de conversión vs **~11.9%** (dos CTAs) vs **~10.5%** (3+). (Foundry CRO 2026 citando dataset Unbounce.)

## B.3 — Social proof

**Dirección sólida y bien soportada:** la **especificidad gana**. Testimonios nombrados, con foto, rol y **resultado numérico**, ubicados **junto al CTA**, superan a "confiado por miles".

| DO | DON'T |
|---|---|
| Cliente nombrado + rol + resultado cuantificado | "Miles de clientes felices" |
| Proof **adyacente al botón**, no solo en el footer | Testimonios anónimos al fondo |
| Match del proof con la oferta específica | Logos genéricos sin contexto |
| LATAM SMB: screenshots de WhatsApp de clientes + conteo de reseñas Google | — |

> Los porcentajes de lift que circulan (ej. "+34% / +68% junto al botón") son **ilustrativos** — la dirección es firme, pero **no cites las cifras como hecho** a un cliente.

## B.4 — Reducción de fricción en formularios / checkout

**DO:**
- **Guest checkout** (sin crear cuenta obligatoria).
- **Mostrar todos los costos temprano** (nada de sorpresas al final).
- Cortar campos no esenciales.

**DON'T:**
- Forzar creación de cuenta.
- Revelar envío/impuestos recién en el último paso.
- Asumir "menos campos siempre gana" — **es un mito**. Un par de campos que califican el lead pueden subir la **calidad** aunque baje la tasa cruda.

**Cifras Baymard (verificadas 2025–26) — usa estas, no otras:**

| Causa de abandono de carrito | % |
|---|---|
| Costos extra/inesperados (envío, impuestos, fees) | **48%** |
| Forzar creación de cuenta | **26%** |
| Abandono promedio de carrito | **~70%** |
| Uplift de conversión por mejor diseño de checkout | **~35%** |

(Baymard Institute, *Cart & Checkout Abandonment*, https://baymard.com/lists/cart-abandonment-rate — **nota:** cifras viejas de 19%/21% que circulan están mal; usa 26%/48%.)

## B.5 — Message-match anuncio → landing

Palanca de conversión de primer orden. **Espeja el headline del anuncio como el H1 de la landing** y reutiliza el hero/oferta del ad.

**DO:**
- H1 con frase **idéntica o casi idéntica** al anuncio.
- Mismo producto/hero visual del ad.
- Misma oferta prometida, sobre el fold.
- **Una página por ángulo** de campaña (o una plantilla que hace swap de H1/hero/oferta por `utm`/keyword — evita mantener 6 archivos y preserva consistencia → mejor Quality Score → menor CPC).

**Caso real (verificado):** un fix centrado en message-match/relevancia produjo **+212%** de conversión (Moz / Conversion Rate Experts). Es **un** estudio de caso genuino — trátalo como referencia, no como expectativa universal.

## B.6 — Landing para tráfico pagado: quitar nav (attention ratio 1:1)

En landings **dedicadas de campaña**, quitar la nav global sube la conversión al forzar **attention ratio 1:1** (un solo destino).

- VWO: attention ratio de 13:1 → 3:1, reportó **+100%** de conversión. Unbounce reportó **>40%** y en otro caso **336%**. Son **casos únicos, altamente dependientes de contexto** — no una ley.
- **Caveat de a11y:** esto es para **landings de campaña dedicadas**. Los **homepages siguen necesitando nav** + un **skip-to-content link** para accesibilidad.

```html
<a href="#main" class="skip-link">Saltar al contenido</a>
<!-- ...header... -->
<main id="main">…</main>
```

## B.7 — Velocidad = conversión (y accesibilidad)

Core Web Vitals son palancas CRO, no solo métricas de ingeniería. Layout rápido y estable también ayuda a usuarios de baja visión/motores.

| Métrica | Objetivo |
|---|---|
| LCP | **< 2.5s** (autoritativo, web.dev) |
| Carga total LP | **< 1s** ideal, techo **~3s** |
| Regla de degradación | **≈ −7% conversiones por cada segundo extra** (benchmark linaje Akamai, aún citado 2026) |

**Tácticas concretas:**
- Imágenes **WebP/AVIF** con `width`/`height` explícitos (previene CLS).
- Lazy-load below-the-fold; hero eager.
- `defer` en JS no crítico; CSS crítico inline.
- Render **estático/edge** para una LP de objetivo único.
- **Especialmente crítico en redes móviles LATAM irregulares.**

> "1s convierte ~3x que 5s" es **direccionalmente** soportado (curvas observadas ~1.9% a 2.4s → ~0.6% a 5.7s ≈ 3x) pero no es un número controlado — úsalo como motivación.

```html
<img src="hero.avif" width="1200" height="675"
     fetchpriority="high" alt="Descripción real del producto" />
<img src="below.avif" width="800" height="600" loading="lazy" alt="…" />
```

## B.8 — Mitos CRO a rechazar en 2026

| Mito | Realidad |
|---|---|
| "Above-the-fold ya no importa" | El fold sigue decidiendo el bounce |
| "Un color de botón específico gana" | **Contraste e isolación** mandan, no el tono |
| "Menos campos siempre gana" | Trade-off real: campos que califican suben calidad de lead |
| "Los trust badges genéricos generan confianza" | Proof **específico** supera copy genérico |
| "Los carruseles suben engagement" | Auto-rotantes bajan conversión (CTR mínimo tras slide 1) y rompen a11y (2.2.2) |

## B.9 — Sin dark patterns (exposición legal, no solo ética)

Los dark patterns son **exposición legal UE** bajo DSA (Art. 25) / UCPD / GDPR + contexto EAA, no solo una elección ética. En una barrida CPC de la UE (~560 tiendas, 23+ estados), **~40%** fueron marcadas por diseño potencialmente engañoso.

**Prohibido / riesgoso:**
- Countdowns falsos.
- Drip pricing (costos que aparecen al final).
- Upsells pre-tildados.
- Cancelación tipo "roach motel" (fácil entrar, imposible salir).

**Consentimiento simétrico (guía EDPB/CNIL):** "Rechazar todo" debe ser **tan fácil como** "Aceptar todo" — mismo nivel, mismo peso visual.

---

## B.10 — Creative para ads (tráfico pagado)

### Especificaciones verificadas

**Meta — safe zones unificadas 9:16 (2026):**
- Master vertical **1080×1920 (9:16)** + cuadrado seguro centrado **1080×1080**.
- Mantén contenido crítico fuera de: **top 14%**, **bottom hasta 35%** (diseña al 35% de Reels — su UI come ~290px más que Stories), **laterales 6%**.
- Meta **desprioriza 1:1** hacia **4:5 (1080×1350)** y 9:16. Matiz: "cuadrado penalizado" es **exagerado** — 1:1 **pierde alcance/cobertura de placement**, no hay penalización algorítmica.
- (behaviour.digital, *Meta Reels Safe Zone 14/35/6 2026*; Billo; 1clickreport. **No** cites nombres de features de Ads Manager tipo "Smart Zoom" como oficiales sin verificar.)

**Google Responsive Display Ads (assets):**

| Formato | Tamaño | Mínimo |
|---|---|---|
| Landscape | 1200×628 | 600×314 |
| Square | 1200×1200 | 300×300 |
| Portrait (4:5, opcional) | 1200×1500 | 320×400 |

JPG/PNG ≤ **5MB**; **texto sobre imagen < 20%** (Google descuenta assets que lo superan). (DigitalApplied, CreativeOS 2026.)

**Google — banners subidos estándar (mayor fill IAB):**
`300×250`, `728×90`, `320×50`, `300×600`, `160×600`; PNG/JPG estático **≤ 150KB**.

### Hook rate — la palanca make-or-break

**Hook rate = views de 3s / impresiones.** La mayoría abandona antes del segundo 3.

| Tier | Hook rate |
|---|---|
| Falla (matar el creative) | **< 25%** |
| Mediana Meta 2026 | **~28%** |
| Bueno | 30%+ |
| Elite | **40%+** |

Ingeniería del primer **~1.5s**: claim audaz, movimiento en el frame 1, texto legible en mute, **sin intro de logo**. Mata rápido lo que va bajo 25%. (AdLibrary, AdManage.ai, Coinis 2026.) **Variación por categoría:** B2B / compra considerada corre aceptablemente en **15–25%**.

### Creative que gana en 2026

- **UGC-style + video vertical-native**: selfie UGC, talking-head de fundador de ~12s, screenshot de testimonio. Baja la ad-blindness, es lo más barato para un operador solo. Graba con teléfono, luz natural, **subtítulos quemados** (asume sound-off, pantalla chica, legible a ~150px). *(El "~70% del top-quartile es UGC" que circula **no** está sustanciado — usa la táctica, deja el número.)*
- **Layout de static que convierte:** hook/headline audaz → visual de beneficio claro → oferta explícita + CTA. Legible en mute y a escala de thumbnail.
- **Un ángulo = una página** (o plantilla campaign-aware que hace swap por `utm`/keyword).

### LATAM — Click-to-WhatsApp (CTWA): el formato de mayor fit

Para operador solo en LATAM, **CTWA es el funnel más fuerte** — esquiva la construcción/velocidad de LP por completo.

| Métrica (getkanal 2026, LATAM) | Rango |
|---|---|
| CPM LATAM | **€2–5** (vs €4–9 Europa Occidental) |
| Cost per opt-in (DTC) | **€0.40–1.20** |
| Cost per conversation started (métrica clave de eficiencia) | €1.50–8 |

Ad-to-chat con **mensaje de apertura pre-rellenado que espeja la promesa del anuncio** + respuesta rápida. (getkanal, *CTWA Benchmarks 2026*.)

### Estética (guardrail, no directiva)

No-flat (gradientes sutiles, falso 3D suave, glassmorphism) **puede** funcionar en 2026 si es **barato y sutil** y **no pelea con la jerarquía del CTA ni frena la página** (usa CSS GPU-accelerated, no JS). Para herramientas profesionales/productividad, **flat o gradiente simple suele ganar** sobre 3D pesado. *(El "+70% de tiempo de interacción por 3D interactivo" es un stat inventado — ignóralo. Glassmorphism es tendencia reciclada 2020–22.)* Trata esto como "que no dañe la conversión", no como orden de añadir 3D.

---

# Checklist combinado — a11y + Conversión

## Accesibilidad (WCAG 2.2 AA)
- [ ] Certificando contra **2.2 AA** (no 2.1). No reportar HTML inválido/IDs duplicados como falla.
- [ ] Targets de puntero **≥ 24px** (aim 44px móvil); padding cuenta.
- [ ] Foco de teclado **nunca oculto** por sticky/cookie/chat (`scroll-padding-top`).
- [ ] Toda interacción de **drag** tiene alternativa de un solo puntero.
- [ ] Login/signup: **paste permitido**, `autocomplete` tokens, passkey/magic-link/OAuth. Sin texto-CAPTCHA ni tests de memoria.
- [ ] No re-pedir datos (3.3.7); ayuda en posición consistente (3.2.6).
- [ ] Contraste **4.5:1** cuerpo / **3:1** grande / **3:1** UI y foco. Sin `#999` sobre blanco.
- [ ] `:focus-visible` ≥ 2px, ≥ 3:1. **Nunca** `outline:none` sin reemplazo.
- [ ] `prefers-reduced-motion: reduce` honrado; movimiento auto > 5s pausable.
- [ ] Formularios: label visible persistente + asociación programática + error en **texto** + `autocomplete` + `fieldset/legend`.
- [ ] HTML nativo sobre ARIA. Un `<main>`, botones de ícono con `aria-label`, decorativas `alt=""`.
- [ ] **EAA:** si vendes a consumidores UE y no calificas microempresa (< 10 empleados **Y** ≤ €2M), estás en scope.
- [ ] Homepage con `skip-to-content` link.

## Conversión
- [ ] H1 benefit-first (qué/para quién/beneficio) sobre el fold de **375px**, un CTA.
- [ ] **Message-match:** H1 espeja el anuncio; mismo hero/oferta; una página por ángulo.
- [ ] **Un** CTA primario de alto contraste (no por tono), repetido en páginas largas, label de acción en 1ª persona.
- [ ] Landing de campaña **sin nav** (attention ratio 1:1); homepage conserva nav.
- [ ] Social proof **específico** (nombre/rol/resultado) **junto al CTA**, no solo footer.
- [ ] Guest checkout; costos totales temprano; sin forzar cuenta. No asumir "menos campos siempre gana".
- [ ] LCP < 2.5s; LP < 1s ideal / ~3s techo; WebP/AVIF con `width`/`height`; JS diferido.
- [ ] **Sin dark patterns:** consentimiento simétrico (rechazar = aceptar), sin countdowns falsos / drip pricing / pre-tildados / roach-motel.
- [ ] Purgar mitos: fold vivo, contraste>color, trade-off de campos, proof específico, sin carruseles auto-rotantes.

## Ads / tráfico pagado
- [ ] Master **9:16 1080×1920** + cuadrado seguro 1080×1080; safe zones **14% top / 35% bottom / 6% lados**; priorizar 4:5/9:16 sobre 1:1.
- [ ] Google RDA: 1200×628 + 1200×1200 (+1200×1500), ≤5MB, texto <20%. Banners: 300×250/728×90/320×50/300×600/160×600, ≤150KB.
- [ ] **Hook rate** medido; matar creative < 25%; ingeniería del primer ~1.5s; subtítulos quemados, legible a 150px, mute-first.
- [ ] Creative **UGC vertical-native** por defecto.
- [ ] **LATAM: CTWA** como funnel primario — mensaje pre-rellenado que espeja el ad + respuesta rápida.

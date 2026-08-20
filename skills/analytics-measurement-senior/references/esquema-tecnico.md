# Esquema técnico — eventos, consent-gating Ley 1581 y lectura del embudo

> Detalle de implementación de `analytics-measurement-senior`. Stack-agnóstico (los ejemplos usan GA4
> `gtag` + un wrapper; el mismo esquema se emite a PostHog cambiando solo el sink). Contrato:
> `SKILL.md` (Regla #0: clic ≠ conversación) · Taxonomía `Ref:` y wa.me: [[landing]] · Codeword: [[medicion]].

## 1. Taxonomía de eventos (versionada, agnóstica)

Convención: `snake_case`, nombres estables. Límites GA4 (respetar aunque cambie el proveedor): nombre
≤40 chars, ≤25 params/evento, clave ≤40, valor ≤100. **Ningún param puede llevar PII** (lista blanca abajo).

### `page_view`
Vista de página. GA4 lo emite auto; se augmenta para no depender del auto-tracking.
| Param | Tipo | Ejemplo | Nota |
|---|---|---|---|
| `page` | string | `/servicios` | **pathname SIN query ni hash** (privacidad) |
| `title` | string | `Servicios` | título de la vista |
| `ref_channel` | string? | `IG` | solo si la URL de entrada trae `?ref=IG` de un canal externo; se lee y se descarta de la URL |

### `whatsapp_click`  ← el evento propio, corazón de la capa CLIC
Se dispara al tocar CUALQUIER CTA `wa.me`. Mide **intención (clic), no conversación** (Regla #0).
| Param | Tipo | Ejemplo | Nota |
|---|---|---|---|
| `ref` | string | `WEB-HERO` | **el mismo código `Ref:` del codeword** — clave de reconciliación. Enum de [[landing]]: `WEB-*`, `FB`, `IG`, `EST`, `GBP`, `QR`… |
| `section` | string | `hero` | sección lógica: `nav`,`hero`,`servicios`,`catalogo`,`faq`,`cierre`,`fab` |
| `page` | string | `/` | pathname sin query/hash |
| `channel` | string | `web` | medio on-site (siempre `web`; el canal de origen externo lo lleva `ref`) |
| `placement` | string? | `sticky-nav` | ubicación física: `sticky-nav`,`fab`,`inline` |

**Prohibido en este evento:** el número `wa`, el `text=` pre-cargado, cualquier fragmento del mensaje.
El link `wa.me` lleva PII potencial en `text=`; el evento SOLO manda el `ref`, nunca el href completo.

### `scroll_depth`
Proxy de lectura. Se activa su LECTURA solo a tráfico alto; a bajo se instrumenta pero no se analiza.
| Param | Tipo | Ejemplo | Nota |
|---|---|---|---|
| `percent` | int | `50` | hitos `25/50/75/90`, una vez por hito por página (dedupe) |
| `page` | string | `/` | pathname sin query/hash |

### Opcional a tráfico alto
`cta_view` (impresión del CTA vía IntersectionObserver) → denominador para CTR real por sección.

### Lista blanca de params (el wrapper descarta todo lo demás)
`page, title, ref, section, channel, placement, percent, ref_channel`. Cualquier clave fuera de esta
lista **no se envía** (defensa por código contra fugas de PII).

---

## 2. Wrapper agnóstico + consent-gating Ley 1581 (esquema, no código de producción)

Objetivo: (a) un solo punto de emisión que sobrevive a cambio de proveedor; (b) **nada se dispara antes
del consentimiento**; (c) scrub de PII por lista blanca. Secuencia:

```
0) HARD NO-LOAD GATE (decisión del must-fix del juez — la vía correcta bajo Ley 1581 estricta):
   NO se inyecta gtag.js ni PostHog en el <head>. NINGÚN script de terceros carga en el primer render.
   Estado inicial en memoria: consent = 'denied'.
   → Cero requests de analytics ANTES del consentimiento — ni siquiera los pings cookieless con IP
     que Consent Mode v2 default-denied SÍ enviaría (eso ya sería transmitir dato personal a un
     tercero sin consentimiento). Costo aceptado y declarado: se PIERDEN los clics que ocurran antes
     de que el usuario decida el banner (privacidad > completitud). Se dice de frente, no se esconde.

1) BANNER HABEAS DATA (ya vive en el footer — Ley 1581 CO)
   - Botón "Aceptar" → onConsentGranted()
   - Botón "Rechazar"/cerrar → queda 'denied' (elección más privada por defecto, coherente con Privacy)
   - Enlace a la Política de Tratamiento de Datos.
   - La decisión se persiste DESPUÉS de decidir: localStorage 'consent_analytics' = 'granted' | 'denied'.
     Nada se guarda antes de decidir.

2) onConsentGranted()  ← RECIÉN AQUÍ carga el tercero (no antes)
   // STUB SÍNCRONO antes de descargar gtag.js: define window.gtag YA (encola en dataLayer), para que
   // un whatsapp_click inmediato tras el 'granted' NO se pierda en la ventana de carga async del script.
   window.dataLayer = window.dataLayer || []; window.gtag = function(){ dataLayer.push(arguments); };
   injectGtagJs(GA4_ID)                                       // descarga gtag.js (async); el stub ya encola
   gtag('js', new Date())
   gtag('config', GA4_ID, { anonymize_ip:true, allow_google_signals:false, send_page_view:false })
   // send_page_view:false = NO page_view automático: GA4 mandaría page_location = href COMPLETO
   // (con query/hash = posible PII). Emitimos page_view propio con solo pathname saneado.
   posthog?.init(POSTHOG_KEY, {...}); posthog?.opt_in_capturing()             // solo si PostHog activo (tráfico alto)

3) trackEvent(name, params)  ← ÚNICO punto de emisión
   if (consent !== 'granted') return;               // gate duro: sin consent, no-op (se DESCARTA, no se encola con PII)
   const clean = whitelist(params);                 // descarta claves fuera de la lista blanca
   clean.page = stripQuery(location.pathname);      // jamás query/hash (pueden traer PII)
   assertNoPII(clean);                              // regex: sin dígitos-teléfono, sin 'wa.me', sin 'text='
   gtag('event', name, clean);                      // sink 1 (el stub garantiza que gtag existe tras el granted)
   posthog?.capture(name, clean);                   // sink 2 (opcional, mismo payload)

4) revokeConsent()  ← Art. 8 Ley 1581: el consentimiento es REVOCABLE (no solo opt-in)
   consent = 'denied'                               // deja de emitir de inmediato (el gate de (3) lo corta)
   gtag?.('consent','update',{ analytics_storage:'denied' })
   borrarCookiesGA()                                // expira _ga, _ga_*, _gid en el dominio (dejar de identificar)
   localStorage['consent_analytics_v1'] = 'denied'  // persistido y VERSIONADO: si sube _vN (cambio de política) → re-preguntar
```

**Invariantes que se PRUEBAN (van al DoD, no se comentan):**
- [ ] Ningún request a GA4/PostHog en la pestaña Network **antes** de aceptar el banner.
- [ ] Ningún `whatsapp_click` lleva el número `wa` ni el `text=` (scanner regex sobre el payload).
- [ ] `page` nunca contiene `?` ni `#`.
- [ ] Al rechazar, no se setea cookie de analytics ni se emite evento.
- [ ] `assertNoPII` rechaza un valor que matchee `\d{7,}` o contenga `wa.me`/`text=`.

**Config GA4 extra:** IP anonimizada (default), **Google Signals OFF** (cross-device = más PII), sin
User-ID. Estos ajustes son parte del entregable, no opcionales.

---

## 3. Embudo, reconciliación y umbral de tráfico → viven en `SKILL.md`

Para no duplicar la fuente de verdad (REGLA #9), el **embudo → dueño de la acción**, la **tabla de
diagnóstico**, la **reconciliación clic↔codeword** y el **umbral bajo↔alto (A/B)** viven ÚNICAMENTE en
`SKILL.md` (secciones "Leer el embudo", "Método operativo" y "Qué se mide a tráfico BAJO vs ALTO").
Este archivo guarda solo el detalle TÉCNICO: taxonomía de eventos (§1) y wrapper consent-gated (§2).

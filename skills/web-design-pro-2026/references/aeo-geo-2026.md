# AEO/GEO 2026 — Playbook para ser citado por motores de respuesta con IA

> **Qué es esto:** cómo lograr que tu sitio sea **citado dentro de la respuesta sintetizada** de Google AI Overviews / AI Mode, ChatGPT, Perplexity y Claude — no cómo rankear un enlace azul. Es una disciplina adyacente al SEO clásico, no un reemplazo.
>
> **Honestidad de entrada (REGLA #6):** buena parte del mercado GEO revende fundamentos de SEO con nombre nuevo. La postura de Google es que esto "sigue siendo SEO". Este documento separa **lo probado** (evidencia experimental o multi-fuente) de **lo vendor/hype** (una sola fuente comercial, direccionalmente plausible pero no verificado). Donde una cifra viene de un solo vendor, lo digo.

---

## 1. Qué es AEO/GEO y por qué importa ahora

**AEO** (Answer Engine Optimization) / **GEO** (Generative Engine Optimization) = optimizar para que tu contenido sea **extraído y citado** dentro de una respuesta generada, en vez de competir por una posición en la SERP.

### El cambio de fondo (datos ancla verificados)

| Señal | Dato | Implicación |
|---|---|---|
| **Conversión del tráfico IA** | El tráfico referido por IA convierte ~**4.4x** mejor que el orgánico (rango 4x–23x según sitio; Semrush/Seer/Ahrefs corroboran el múltipliplo) | Menos volumen, intención mucho más alta. Vale la pena aunque el clic total baje. |
| **Colapso del "top-10 = cita"** | La cuota de citas de AI Overviews que venían del top-10 orgánico cayó de **76% (jul 2025) a 38% (mar 2026)** | Rankear ya **no garantiza** ser citado. Ser citable es un juego distinto. |

Fuentes: cifra 76%→38% aparece verbatim en múltiples fuentes 2026; el múltiplo 4.4x es el consenso (Semrush/Seer/Ahrefs).

### DO / DON'T de encuadre

| DO | DON'T |
|---|---|
| Tratar AEO como capa **encima** del SEO técnico | Abandonar el SEO: crawlability + indexación son el **ticket de entrada**. Si el bot no te rastrea, no te cita. |
| Optimizar para ser **extraíble y citable** | Optimizar solo para posición #1 y asumir que la cita viene sola (ya no) |
| Medir tráfico y conversión de IA por separado | Meter todo en "orgánico" y no ver el canal IA |

> **Regla mental (síntesis honesta):** *si algo no ayudaría a un humano a confiar en la página, tampoco hará que un LLM la cite.* Casi todo lo demás es táctica sobre esa base.

---

## 2. La evidencia dura: el paper GEO (Princeton / Georgia Tech)

El único estudio **experimental** serio de referencia. Es lo más cercano a "probado" que hay.

- **Aggarwal et al., "GEO: Generative Engine Optimization", KDD '24.**
- **arXiv real: `2311.09735`** — DOI ACM SIGKDD `10.1145/3637528.3671900`.
- Método: **GEO-bench**, ~**10.000 queries**, **9 métodos** de optimización evaluados.

> ⚠️ **Cuidado con IDs falsos:** circula un supuesto "companion" `arXiv:2606.20065` — **no existe**, es fabricado. La cita correcta es **arXiv:2311.09735**.

### Qué funcionó vs qué no (dirección plenamente soportada)

| Táctica | Efecto | Veredicto |
|---|---|---|
| **Cite Sources** (agregar fuentes citables) | Top performer | ✅ Funciona |
| **Quotation Addition** (citas textuales de expertos/fuentes) | Top performer | ✅ Funciona |
| **Statistics Addition** (estadísticas concretas con número) | Top performer | ✅ Funciona |
| Fluency / autoridad de lenguaje | Mejora | ✅ Ayuda |
| **Keyword stuffing** | Nulo o negativo | ❌ No hagas |
| Simplificación superficial del texto | No ayuda | ❌ No sirve |

### Magnitudes — la versión honesta

- Los números **de titular del paper** son: **"hasta 40%"** de mejora de visibilidad, **+22% Position-Adjusted Word Count** y **+37% Subjective Impression** a nivel global.
- Cifras como **"+30–40% por cada táctica"** o **"+115% para páginas en rank-5"** son **restatements de vendors**, no cifras verbatim del paper. Úsalas como ilustrativas.
- **Caveat temporal:** las magnitudes son de **motores era-2024**. La dirección se sostiene; los números exactos probablemente ya cambiaron.

**Traducción accionable:** cada afirmación importante debería venir acompañada de **un número, una cita o una fuente**. Esa es la palanca con respaldo experimental más fuerte que existe.

---

## 3. Estructura de contenido citable (answer-first)

Los LLM extraen **bloques auto-contenidos**. El contenido tiene que estar escrito para ser cortado y pegado dentro de una respuesta sin contexto adicional.

### 3.1 Answer-first: respuesta directa arriba

**Dato verificado:** ~**44.2%** de las citas de LLM vienen del **primer 30%** de la página; 31.1% del medio; 24.7% de la conclusión (Digital Applied, getpassionfruit, 2026).

| DO | DON'T |
|---|---|
| Abrir cada sección con una **respuesta directa auto-contenida de 40–80 palabras** | Enterrar la respuesta tras 4 párrafos de intro |
| Poner la conclusión **antes** del desarrollo (pirámide invertida) | Estilo "build-up" que reserva el payoff para el final |
| Repetir el sujeto explícito ("Bre-B es…") en vez de pronombres | "Esto/eso permite…" — el chunk pierde el referente al extraerse |

**Bloque de respuesta directa (patrón copiable):**

```html
<section id="que-es-aeo">
  <h2>¿Qué es AEO?</h2>
  <p class="tldr"><strong>Respuesta directa:</strong> AEO (Answer Engine
  Optimization) es la práctica de estructurar contenido para que los motores
  de respuesta con IA lo citen dentro de su respuesta generada, en lugar de
  rankearlo como enlace. Se diferencia del SEO clásico en que el objetivo es
  la <em>extracción y cita</em>, no la posición.</p>
  <!-- desarrollo debajo -->
</section>
```

> Nota honesta: el "~4.2x para pasajes auto-contenidos de 134–167 palabras" y "~40% más probable con formato Q&A" son **cifras vendor**, direccionalmente consistentes pero no peer-reviewed. La recomendación de abrir con 1–2 frases de respuesta directa sí es consenso.

### 3.2 Formatos extraíbles

- **TL;DR / caja de definición** al inicio de guías largas.
- **Pares Q&A** con la pregunta como `H2`/`H3` y la respuesta inmediata debajo.
- **Definiciones canónicas**: "X es …" en una sola frase, sin subordinadas.
- **Tablas** para comparaciones (los LLM las parsean muy bien y las citan como unidad).

```css
.tldr {
  border-left: 3px solid var(--accent);
  padding: .75rem 1rem;
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  font-size: 1rem;
  margin: 0 0 1.25rem;
}
```

---

## 4. Estructura para parsing RAG (jerarquía, listas, listicles)

Los motores fragmentan (chunk) la página. Una jerarquía limpia = chunks limpios.

### DO / DON'T de estructura

| DO | DON'T |
|---|---|
| `H2`/`H3` semánticos, un tema por sección | Saltar de `H2` a `H4`, o `H`s decorativos |
| Listas numeradas y bullets para pasos/criterios | Párrafos-muro con la lógica embebida en prosa |
| Tablas para comparación y specs | Comparaciones descritas solo en texto corrido |
| Páginas profundas de **un solo tema** | Homepages genéricas que tocan todo superficialmente |

### Listicles / Top-N dominan las citas (verificado contra dataset)

- Sobre ~**400M citas / 25.000 URLs**: los **listicles = 63%** de las citas de LLM; de esas, **71–86%** son listas ranqueadas **Top-N** (Search Engine Land, Wellows, 2026).
- **Matiz por intención** (importante, no lo ignores):
  - **Informacional** → favorece **artículos** (~45%) sobre listicles (~22%).
  - **Comercial** → favorece **listicles** (~41%).

**Accionable:** para queries comerciales/comparativas, produce "Top N [categoría] en [contexto]" con entradas numeradas y auto-contenidas. Para informacional, artículo profundo con answer-first. No fuerces listicle donde la intención es explicativa.

> "~156% más selección para mixed media" es cifra **vendor** — direccional, no la trates como establecida.

---

## 5. Autoridad de entidad y autoridad temática

**Dirección soportada por consenso 2026:** para la cita de IA, la **autoridad temática** pesa más que la **autoridad de dominio (DA)**. Páginas en **posición 6–10** con cobertura temática fuerte **sí** se citan. La **claridad de entidad** (que el motor sepa qué/quién eres y cómo te conectas al Knowledge Graph) es una señal de selección de primer orden.

### DO / DON'T

| DO | DON'T |
|---|---|
| Construir **clusters temáticos** densos en entidades alrededor de un tema | Un post suelto por keyword sin cobertura de vecindad |
| **Nombrar las cosas explícitamente** (productos, conceptos, personas) | Referencias vagas ("nuestra solución", "la plataforma") |
| Página-home de entidad para **Organization / Person** con `sameAs` | Dejar la identidad implícita y desconectada del grafo |
| Alinear con **Wikidata / Wikipedia / LinkedIn / Crunchbase** vía `sameAs` | Asumir que el DA alto por sí solo te hace citable |

**`sameAs` de entidad (copiable):**

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Tu Empresa",
  "url": "https://tu-dominio.com",
  "sameAs": [
    "https://www.wikidata.org/wiki/Qxxxxxxx",
    "https://www.linkedin.com/company/tu-empresa",
    "https://www.crunchbase.com/organization/tu-empresa"
  ]
}
```

> **Honestidad sobre cifras:** los múltiplos tipo "17% de la varianza de cita vs <4% para DA", "2.3x", "4.8x para 15+ entidades conectadas" son **de un solo vendor** (estilo Frase) y **no los pude corroborar** de forma independiente. La **táctica** es sólida; los **multiplicadores exactos** son ilustrativos, no establecidos.

---

## 6. Presencia ganada en fuentes que los LLM confían (off-site)

A menudo mueve más la aguja que el trabajo on-site. Los motores citan desproporcionadamente un puñado de dominios de terceros.

### Datos verificados (2026)

| Dominio | Dato | Fuente |
|---|---|---|
| **Reddit** | Dominio **más citado** entre motores combinados (~30M citas, mar 2026) | Peec |
| **Wikipedia + Reddit** | ~**12–13% cada uno** de las citas de ChatGPT | Similarweb/Statista/Contently |
| **LinkedIn** | En alza; top domain para queries **profesionales** (1.4M citas) | Profound |
| **YouTube** | Fuente citada de alto valor para how-to/demostración | — |

### DO / DON'T

| DO | DON'T |
|---|---|
| Presencia **auténtica** en Reddit (responder de verdad, aportar) | Spam/astroturfing — Google **marca menciones inauténticas** (mythbusting explícito) |
| Página/menciones en **Wikipedia** solo si cumples notabilidad real | Crear tu propia entrada promocional (se revierte y quema reputación) |
| **LinkedIn** para temas profesionales/B2B; contenido citable ahí | Depender de un solo canal |
| Reviews de terceros, listados, YouTube explicativo | Comprar menciones — riesgo de penalización y cero durabilidad |

> **Matiz de las cifras:** el encuadre "ningún dominio supera ~5%" es un **promedio cross-plataforma** y está en tensión leve con los **12–13% single-platform** de Reddit/Wikipedia. Ambos son ciertos: depende de si mides por plataforma o promediado. Es un **portfolio play**: reparte presencia, no apuestes a un dominio.

---

## 7. Frescura (freshness) como señal

**Dirección corroborada** en múltiples fuentes 2026: la recencia es una señal genuina de selección para motores de IA.

- Las URLs que la IA superficie son ~**25.7% más frescas** (estudio de 17M citas).
- Páginas actualizadas con frecuencia capturan múltiplos más de citas (se reporta "4–10x con refresh ~cada 2 semanas").

> **Honestidad:** el "25.7% (17M citas)" y el "4–10x en ~2 semanas" son **cifras vendor/single-study**, no peer-reviewed. La señal de frescura es real; la **magnitud** trátala como direccional.

### DO / DON'T (bajo riesgo, alto sentido)

| DO | DON'T |
|---|---|
| Fecha **"Última actualización" honesta** y visible | Cambiar la fecha sin tocar el contenido (fake freshness → riesgo) |
| Revisión rodante de stats, ejemplos y años | Dejar "en 2024…" congelado en una guía de 2026 |
| **Re-verificar números** cuando actualizas | Actualizar cosmético sin re-chequear los datos citados |

```html
<p class="updated">
  <time datetime="2026-07-10">Actualizado: 10 jul 2026</time>
  — cifras re-verificadas contra fuentes primarias.
</p>
```

---

## 8. `llms.txt` / `llms-full.txt` — la toma honesta

**Formato** (propuesta estilo `llms.txt`): Markdown en la raíz del sitio con enlaces curados a tu documentación en texto plano. `llms-full.txt` = versión expandida con el contenido inline.

```markdown
# Tu Producto

> Descripción de una línea de qué hace el producto.

## Docs
- [Quickstart](https://tu-dominio.com/docs/quickstart.md): arrancar en 5 min
- [API Reference](https://tu-dominio.com/docs/api.md): endpoints y auth
- [Guías](https://tu-dominio.com/docs/guides.md): casos de uso

## Opcional
- [Changelog](https://tu-dominio.com/changelog.md)
```

### Veredicto: mayormente hype para visibilidad en AI-search

- **A 2026, ningún vendor mayor de IA se compromete a leer `llms.txt`.** El análisis de logs muestra fetches **negligibles** a `/llms.txt` por los crawlers de IA.
- **Google, en su propio mythbusting de AI-search, dice explícitamente que NO necesitas archivos machine-readable / AI-text / Markdown** para aparecer en AI search (Search Engine Journal).

### Pero sí tiene un caso de uso real

- **Alimentar agentes de coding** (Cursor, Claude Code, Copilot, etc.) con tus docs de API/producto. Este es el uso genuino: dev-experience, estilo Stripe / Vercel / Anthropic.

| DO | DON'T |
|---|---|
| Publicar `llms.txt` si tienes **docs de producto/API** que agentes consumirán | Esperar que `llms.txt` te haga **citar** en ChatGPT/Perplexity |
| Tratarlo como **DX**, no como palanca de AEO | Priorizarlo por encima de contenido citable y SEO técnico |

---

## 9. Schema markup — la toma CONTESTADA

Aquí las dos partes están verificadas y **en conflicto**. Sé equilibrado.

### El caso a favor (vendors)
- Datos vendor afirman **2–2.5x** de lift de cita con schema.

### El caso en contra (evidencia más dura)
- **Estudio Ahrefs (real):** 1.885 páginas que **añadieron JSON-LD** (ago 2025–mar 2026) vs ~4.000 controles →
  - **AI Overviews: −4.6%**
  - **AI Mode: +2.4%**
  - **ChatGPT: +2.2%** (los dos últimos dentro del ruido) → **sin efecto significativo**.
  - La correlación **3x** (sobre 6M URLs) es real, pero es **correlación, no causa** (las páginas con schema tienden a ser de sitios más cuidados).
- **Google mythbusting:** no hay **tratamiento generativo especial** por tener schema.
- **HowTo y FAQ rich results están deprecados** en Google Search — no esperes el rich result clásico.

### Postura recomendada (equilibrada)

| Implementa schema PARA… | NO lo implementes esperando… |
|---|---|
| Parsing y desambiguación de entidad | Un lift de **cita** garantizado (no probado) |
| Elegibilidad de rich results donde aún existen (`Article`, `Product`, `Breadcrumb`) | Que `FAQ`/`HowTo` te den rich result (deprecados) |
| Claridad `Organization`/`Person` + `sameAs` | Que el schema compense contenido débil |

**Schema base defendible (`Article`):**

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "AEO/GEO 2026: cómo ser citado por motores de IA",
  "datePublished": "2026-07-10",
  "dateModified": "2026-07-10",
  "author": { "@type": "Person", "name": "Cristian Gutierrez" },
  "publisher": {
    "@type": "Organization",
    "name": "Tu Empresa",
    "url": "https://tu-dominio.com"
  }
}
```

> Puedes seguir marcando `FAQPage` para **parsing/entidad**, sabiendo que **no** rendirá el rich result clásico. Hazlo por claridad de máquina, no por el snippet.

---

## 10. Medir tráfico de referencia de IA (GA4 híbrido)

**Setup recomendado.** El problema central: **35–70%** de las referencias de IA llegan **sin referrer** y se esconden en **Direct**.

### 10.1 Canal nativo "AI Assistant" de GA4
- Canal nativo para tráfico de asistentes IA, reportado en 2026 (**verifica disponibilidad y fechas en tu propiedad GA4** antes de confiar en él).
- Marca `medium = ai-assistant`. **No es retroactivo.**
- **Limitaciones reales:**
  - La lista reconocida **cambió**: agregó Deepseek/Copilot/Grok; **Claude cayó** de la definición publicada.
  - **Omite Perplexity.**
  - Los clics desde **AI Overviews** se mezclan en **organic**, no se aíslan.

### 10.2 Canal custom por regex (el workaround correcto)
Crear un **channel group custom** con una regla **por encima de Referral** que capture source/referrer de IA.

Patrón regex para `Source` (ajústalo a tu realidad):

```
chatgpt|openai|perplexity|claude|anthropic|gemini|bard|copilot|
deepseek|grok|you\.com|poe\.com|phind
```

### DO / DON'T de medición

| DO | DON'T |
|---|---|
| Correr **ambos**: canal nativo **+** regex custom | Confiar solo en "AI Assistant" (omite Perplexity, no retroactivo) |
| Regla custom **por encima** de Referral en el channel group | Dejar que las referencias caigan a Direct/Referral |
| Segmentar conversión del canal IA aparte (recuerda el ~4.4x) | Diluir el tráfico IA dentro de "orgánico" |
| Aceptar que AI Overviews-clicks quedan en organic (límite conocido) | Asumir cobertura 100% — hay un piso de "no-referrer" irreducible |

Fuentes (2026, revalidar antes de confiar): Digital Applied, Semrush, AIVO, madx — `medium=ai-assistant`, no-retroactivo, Perplexity ausente, Claude fuera de la lista publicada.

---

## 11. Bottom line honesto (anti-slop)

- **Google lo dice literal:** AEO/GEO "**sigue siendo SEO**". Su guía 2026 tiene una sección **"Mythbusting generative AI search"** que nombra como **innecesarios**: `llms.txt`, chunking manual, menciones inauténticas, y archivos de markup dedicados AEO/GEO.
- Buena parte del mercado GEO **repackagea fundamentos de SEO**. Desconfía de dashboards que prometen "citas garantizadas".

### La lista corta de palancas con respaldo

1. **E-E-A-T real** (experiencia, autoridad, confianza demostrables).
2. **Bloques answer-first** auto-contenidos, arriba de la página.
3. **Estadísticas + citas textuales + fuentes** en cada afirmación (la palanca del paper GEO).
4. **Autoridad temática + claridad de entidad** (clusters densos, `sameAs`).
5. **Presencia ganada de terceros** (Reddit/Wikipedia/LinkedIn/YouTube), auténtica.
6. **Frescura honesta** (actualizar de verdad, re-verificar números).
7. **SEO técnico sólido** (crawlability/indexación = ticket de entrada).

> **Heurística de cierre:** *si no ayudaría a un humano a confiar en la página, no hará que un LLM la cite.* Todo lo demás es táctica sobre eso — y las tácticas con número exacto de un solo vendor son sospechosas hasta que se corroboren.

---

## 12. Checklist AEO (accionable)

### Contenido
- [ ] Cada sección abre con **respuesta directa auto-contenida de 40–80 palabras**.
- [ ] **TL;DR / caja de definición** al inicio de guías largas.
- [ ] Sujetos **nombrados explícitamente** en los chunks (sin pronombres colgantes).
- [ ] Toda afirmación importante trae **estadística, cita o fuente** (palanca GEO probada).
- [ ] Formato **Q&A** con la pregunta en `H2`/`H3`.
- [ ] **Tablas** para comparaciones y specs.
- [ ] **Listicle Top-N** para queries comerciales/comparativas; **artículo profundo** para informacional.

### Estructura / técnico
- [ ] Jerarquía `H2`/`H3` semántica, un tema por sección.
- [ ] Página **profunda de un solo tema** (no homepage genérica).
- [ ] Crawlability + indexación verificadas (**ticket de entrada**).
- [ ] Schema base (`Article`/`Product`/`Breadcrumb`) **para parsing/rich-results**, sin esperar lift de cita.
- [ ] `Organization`/`Person` con **`sameAs`** a Wikidata/LinkedIn/Crunchbase.
- [ ] `llms.txt` **solo si** tienes docs de API/producto para agentes de coding (no como palanca de cita).

### Autoridad / off-site
- [ ] **Clusters temáticos** densos en entidades.
- [ ] Presencia **auténtica** en Reddit/LinkedIn/YouTube; Wikipedia solo si hay notabilidad real.
- [ ] Cero menciones inauténticas/compradas (Google las marca).

### Frescura
- [ ] Fecha **"Última actualización" honesta** y visible.
- [ ] Calendario de revisión rodante de stats/ejemplos.
- [ ] Números **re-verificados** en cada actualización.

### Medición
- [ ] Canal **nativo "AI Assistant"** de GA4 activo (`medium=ai-assistant`).
- [ ] **Canal regex custom** por encima de Referral (incluye **Perplexity** y **Claude**, que el nativo omite).
- [ ] Conversión del canal IA **segmentada aparte** (recuerda el ~4.4x).
- [ ] Consciencia de límites: no-referrer→Direct, AI Overviews-clicks→organic, nativo no retroactivo.

---

### Apéndice: proven vs hype (referencia rápida)

| Afirmación | Estatus |
|---|---|
| Statistics/Quotations/Cite-Sources suben visibilidad; keyword stuffing no | **Probado** (paper GEO, arXiv:2311.09735, KDD '24) |
| 44.2%/31.1%/24.7% de citas por posición en la página | **Verificado** (multi-fuente 2026) |
| Listicles = 63% de citas; 71–86% Top-N; split por intención | **Verificado** (dataset ~400M citas / 25k URLs) |
| Reddit dominio más citado; Wikipedia/Reddit ~12–13% ChatGPT; LinkedIn en alza | **Verificado** (Peec/Similarweb/Profound) |
| 76%→38% colapso top-10; 4.4x conversión IA | **Verificado** (multi-fuente 2026) |
| GA4 canal "AI Assistant" (`medium=ai-assistant`), omite Perplexity | Reportado 2026 — revalidar disponibilidad |
| `llms.txt` casi no se fetchea; no es palanca de cita | **Verificado** (Google mythbusting + log analysis) |
| Schema da 2–2.5x de cita | **Contestado** — Ahrefs (1.885 vs ~4.000) no halla efecto significativo; correlación ≠ causa |
| Entidad: "17% varianza vs <4% DA", "4.8x 15+ entidades" | **Vendor/no corroborado** — táctica sí, múltiplos ilustrativos |
| Frescura "25.7% más fresco", "4–10x en 2 semanas" | **Vendor/single-study** — señal real, magnitud direccional |
| "+30–40% por táctica", "+115% rank-5", "4.2x pasajes 134–167 palabras", "+156% mixed media" | **Restatements vendor** — no verbatim del paper |

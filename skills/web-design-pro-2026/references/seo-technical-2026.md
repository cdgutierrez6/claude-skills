# SEO Técnico 2026 — Next.js App Router + Angular SSR

Checklist técnico accionable, calibrado para los dos stacks del proyecto: **Next.js (App Router)** y **Angular con SSR/hydration**. Cada sección trae specs concretas, tablas DO/DON'T y snippets copy-paste. Al final: checklist pass/fail pre-ship.

> **Regla mental de 2026:** Google indexa **mobile-first** y evalúa Core Web Vitals sobre **datos de campo reales (p75)**, no sobre tu Lighthouse local. Además, la mayoría de crawlers de IA (GPTBot, ClaudeBot, PerplexityBot) **no ejecutan JavaScript** — si tu contenido solo existe tras hidratar en el cliente, para ellos no existe. SSR/SSG deja de ser opcional.

---

## ⛔ Antes de nada: qué está OBSOLETO en 2026 (no lo hagas)

| Práctica muerta | Por qué | Qué hacer en su lugar |
|---|---|---|
| Optimizar para **FID** | INP reemplazó a FID como Core Web Vital en **marzo 2024** (Google Search Central). Cualquier guía 2026 que hable de FID está caducada. | Optimizar **INP** (mide la latencia peor de *todas* las interacciones, no solo la primera). |
| **AMP** para ranking | Irrelevante para posicionamiento hoy. No da ventaja de ranking. | SSR/SSG normal con buenos CWV. |
| **FAQPage** rich result | Restringido a sitios gov/salud desde 2023 y en efecto retirado para el resto (se reportó eliminación total en 2026 — **revalida fecha/estado en Search Central antes de decidir**). | Sigues pudiendo usar `FAQPage` para IA/estructura, pero **no esperes rich result**. No inviertas en ello por SEO. |
| **HowTo** (retirado por Google en 2023) y varios tipos de nicho (Course, ClaimReview, Estimated Salary, etc.) retirados progresivamente | El markup existente no se penaliza, pero no genera rich result. **Revalida la lista vigente** en Search Central; las fechas exactas cambian. | Concentrarse en los tipos que SÍ rinden (abajo). |
| **Keyword stuffing** / texto oculto / anchor repetido | Riesgo de acción manual; los LLM-crawlers penalizan densidad artificial en extracción. | Contenido para humanos; keyword en H1 y primer párrafo, natural. |
| **llms.txt** como entregable SEO obligatorio | Google **no lo soporta** y no tiene planes (Illyes); Mueller lo llamó especulativo; Ahrefs midió ~97% de archivos `llms.txt` con **cero** requests. | Opcional. No lo vendas como deliverable de SEO 2026. |
| `rel=canonical` + `noindex` juntos | Señales contradictorias; Google los ignora o hace algo impredecible. | Elige una: canonical para consolidar, noindex para des-indexar. |
| Canonical de páginas paginadas → page 1 | Pierdes indexación de las páginas profundas. | Cada página paginada self-canonical. |

---

## 1. Core Web Vitals — umbrales y cómo alcanzarlos

### Umbrales oficiales 2026 (sin cambios respecto a 2024-2025)

Medidos en **p75 de usuarios reales de campo (CrUX)**, mobile y desktop **por separado**.

| Métrica | Good (pass) | Needs improvement | Poor |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | **< 2.5 s** | 2.5 – 4.0 s | > 4.0 s |
| **INP** (Interaction to Next Paint) | **< 200 ms** | 200 – 500 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | **< 0.1** | 0.1 – 0.25 | > 0.25 |

Fuente: Google Search Central, Core Web Vitals (https://web.dev/articles/vitals). "Pass" del sitio = las tres en Good, en p75, **en móvil** (suele ser el perfil más débil → presupuestá contra móvil).

> **INP es el vital más incumplido.** Las tasas de fallo varían por dataset (~28-47% según fuente; CrUX top-1000 más alto), así que trata "la mayoría falla INP" como dirección, no como constante. El punto operativo: **INP es donde está el trabajo en 2026.**

### 1.1 LCP — atacar sus 4 subpartes

LCP se descompone en: **TTFB → resource load delay → resource load duration → element render delay**. No optimices a ciegas; mide cuál subparte domina (Chrome DevTools > Performance > LCP breakdown).

| DO | DON'T |
|---|---|
| `fetchpriority="high"` en **exactamente una** imagen (la del LCP) | Dejar el navegador adivinar la prioridad del hero |
| `preload` para recursos de **descubrimiento tardío** (imágenes vía CSS `background`, fuentes) | Precargar 10 cosas — diluye la prioridad |
| Reducir TTFB con SSG/ISR o cache CDN | SSR sin cache en cada request para contenido estático |
| Servir el hero en AVIF/WebP dimensionado al viewport | Servir un JPEG 3000px para un contenedor de 800px |

**Distinción clave:** `preload` arregla el **descubrimiento** (el navegador encuentra el recurso antes); `fetchpriority` arregla la **prioridad** (lo sube en la cola). Son complementarios.

**Caso real:** Google Flights añadió `fetchpriority="high"` a la imagen LCP y bajó LCP de **2.6 s a 1.9 s (~700 ms)** sin cambiar nada más (web.dev, Fetch Priority API case study, https://web.dev/articles/fetch-priority).

```html
<!-- Imagen LCP: prioridad alta, NUNCA lazy -->
<img src="/hero.avif" width="1200" height="630"
     fetchpriority="high" alt="..." />
<!-- Opción con preload para descubrimiento aún más temprano -->
<link rel="preload" as="image" href="/hero.avif"
      imagesrcset="/hero-800.avif 800w, /hero-1200.avif 1200w"
      imagesizes="100vw" fetchpriority="high">
```

**Next.js** — `priority` en el `<Image>` del hero pone `fetchpriority="high"` + `loading="eager"` + preload automáticamente:

```tsx
import Image from "next/image";
<Image src="/hero.avif" alt="..." width={1200} height={630} priority />
```

### 1.2 INP — romper long tasks y ceder el main thread

La palanca #1: ninguna tarea del main thread debe bloquear **> 50 ms**. Cuando un handler/loop es largo, **cede** al main thread para que el navegador pinte la respuesta a la interacción.

| DO | DON'T |
|---|---|
| Ceder con `scheduler.yield()` (fallback `setTimeout(0)`) **solo pasado un deadline** dentro del loop | Ceder en cada iteración (mata throughput) |
| `scheduler.postTask()` para priorizar trabajo | `isInputPending()` — web.dev **deprecó** esta recomendación |
| Diferir trabajo no urgente post-interacción (`requestIdleCallback`) | Ejecutar analytics/render pesado síncronos en el click handler |
| Code-splitting + reducir hydration (ver §5) | Hidratar toda la página de golpe |

Soporte de `scheduler.yield()`: Chrome/Edge **129+**, Firefox **142+**, Safari usa el fallback `setTimeout`. **No es Baseline todavía** (MDN / chromestatus) → siempre con fallback.

```js
// Yield solo cuando ya llevas > 50ms en el bucle
async function processChunks(items) {
  let deadline = performance.now() + 50;
  for (const item of items) {
    doWork(item);
    if (performance.now() >= deadline) {
      await (window.scheduler?.yield?.() ??
             new Promise(r => setTimeout(r, 0)));
      deadline = performance.now() + 50;
    }
  }
}
```

### 1.3 CLS — reservar el espacio por adelantado

CLS se controla **antes** de que el contenido cargue, no después.

| DO | DON'T |
|---|---|
| `width`/`height` o `aspect-ratio` en **toda** imagen, video, iframe, ad | Dejar que la imagen "empuje" el layout al cargar |
| Fuentes self-hosted con `font-display: optional` o `size-adjust`/`ascent-override` | `font-display: swap` sin métrica ajustada → reflow al cargar |
| Reservar espacio para contenido async/hidratado (skeletons con altura fija) | Inyectar banners/cookie bars **encima** de contenido existente |
| Animar con `transform`/`opacity` | Animar `top`/`left`/`height` (dispara layout) |
| `next/font` (auto size-adjust) | `<link>` a Google Fonts sin fallback métrico |

```css
/* Reserva de espacio para media.
   OJO: NO uses aspect-ratio: attr(width)/attr(height) — attr() en aspect-ratio
   solo lo soporta Chrome 133+ y se IGNORA en Safari/Firefox. Los browsers YA
   derivan el ratio de los atributos HTML width/height; ponlos siempre en el <img>. */
img, video, iframe { height: auto; }     /* preserva el ratio dado por width/height del HTML */
.hero { aspect-ratio: 16 / 9; }          /* si necesitas forzarlo, ratio literal en el contenedor */
/* Cookie bar / toast: overlay fijo, NO empuja el flujo */
.cookie-bar { position: fixed; bottom: 0; inset-inline: 0; }
```

> **Angular:** la hidratación destructiva (sin `provideClientHydration`) re-renderiza el DOM y provoca CLS + flicker. Ver §6.

---

## 2. Metadata, Open Graph, canonical, hreflang

### 2.1 Title / description / OG — server-rendered SIEMPRE

Deben venir en el HTML inicial del servidor, no inyectados por JS (los AI-crawlers no los verían).

**Next.js App Router** — objeto `metadata` estático o `generateMetadata` dinámico:

```tsx
// app/layout.tsx  (o page.tsx para overrides por ruta)
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://taller-ejemplo.com"),
  title: { default: "Taller Ejemplo", template: "%s | Taller Ejemplo" },
  description: "Catálogo de taller-ejemplo y repuestos en Manizales. Cotiza por WhatsApp.",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url: "https://taller-ejemplo.com",
    title: "Taller Ejemplo",
    description: "Catálogo de taller-ejemplo y repuestos.",
    images: [{ url: "/og.jpg", width: 1200, height: 630 }],
    locale: "es_CO",
  },
  twitter: { card: "summary_large_image", images: ["/og.jpg"] },
};
```

```tsx
// Dinámico por producto — app/producto/[slug]/page.tsx
export async function generateMetadata({ params }): Promise<Metadata> {
  const p = await getProduct(params.slug);
  return {
    title: p.name,
    description: p.summary,
    alternates: { canonical: `/producto/${p.slug}` },
    openGraph: { images: [{ url: p.ogImage, width: 1200, height: 630 }] },
  };
}
```

O `app/opengraph-image.tsx` / `app/twitter-image.tsx` para generar la imagen OG en el edge.

**Angular SSR** — `Title` y `Meta` services por ruta (en el resolver o el componente, con SSR activo):

```ts
import { Title, Meta } from "@angular/platform-browser";

constructor(private title: Title, private meta: Meta) {}
ngOnInit() {
  this.title.setTitle("Taller Ejemplo");
  this.meta.updateTag({ name: "description", content: "Catálogo..." });
  this.meta.updateTag({ property: "og:image", content: "https://.../og.jpg" });
  this.meta.updateTag({ rel: "canonical", href: "https://.../ruta" }); // o via <link> en index
}
```

### 2.2 Open Graph + Twitter Cards — una imagen para todo

| Spec | Valor |
|---|---|
| Dimensiones | **1200 × 630** (ratio 1.91:1) |
| Peso | **< 1 MB** |
| Composición | Contenido importante en el **80% central** (crops varían por plataforma) |
| Twitter card | `summary_large_image` para la tarjeta grande |

X (Twitter) lee OG como fallback, así que técnicamente solo necesitas `twitter:card` para forzar `summary_large_image`; el resto lo toma de OG. Una sola imagen 1200×630 funciona en todos lados (Facebook, LinkedIn, WhatsApp, X, Slack).

### 2.3 rel=canonical — es una PISTA, no una directiva

Google trata canonical como **una** de varias señales de consolidación (no obligatoria). Reglas:

| DO | DON'T |
|---|---|
| Self-referencing, **URL absoluta** | Canonical relativo |
| Consistente con sitemap, hreflang e internal links | Canonical que contradice el sitemap |
| Cada página paginada → self-canonical | Paginadas → canonical a page 1 |
| Una sola señal de indexación | `canonical` + `noindex` juntos |

En Next.js: `alternates.canonical`. En Angular: `<link rel="canonical">` server-rendered en el `index.html` por ruta (o vía `Meta`/`DOCUMENT`).

### 2.4 hreflang — reciprocidad bidireccional o no funciona

Relevante para EfiziAI/Volanta/VIVO si sirven varios idiomas o países LATAM.

Reglas canónicas (Google localized-versions docs):

- **Cada versión lista TODAS las versiones, incluida a sí misma** (self-reference).
- **URLs absolutas.**
- Códigos **ISO 639-1** (idioma) + opcional **ISO 3166-1 alpha-2** (región): `es`, `es-CO`, `es-MX`.
- Incluir **`x-default`** para el fallback.
- Cada URL objetivo de hreflang debe ser **self-canonical** (no apuntar canonical a otra).
- **Reciprocidad:** si A enlaza a B, B debe enlazar a A. Un return-link faltante **rompe el clúster entero**.

Entrega vía `<link>` en `<head>`, sitemap, o header HTTP. En Next.js:

```tsx
export const metadata = {
  alternates: {
    canonical: "https://volanta.com/co",
    languages: {
      "es-CO": "https://volanta.com/co",
      "es-MX": "https://volanta.com/mx",
      "x-default": "https://volanta.com",
    },
  },
};
```

---

## 3. JSON-LD structured data (copy-paste)

**JSON-LD es el formato preferido de Google.** Reglas transversales:

- Los datos **deben coincidir con el contenido visible** (mismatch = riesgo de acción manual).
- Usa `@graph` + `@id` para enlazar entidades (Organization ← LocalBusiness ← Breadcrumb).
- **Valida antes de publicar** con Rich Results Test (https://search.google.com/test/rich-results) y Schema Markup Validator.

**Tipos que SÍ ganan rich result en 2026:** `Organization`, `Article`/`BlogPosting`, `Product`, `LocalBusiness`, `BreadcrumbList`, `Video`, `Event`. (FAQ ya no da rich result — ver §obsoleto — pero el markup sigue siendo válido para IA/estructura.)

### 3.1 Organization

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://taller-ejemplo.com/#org",
  "name": "Taller Ejemplo",
  "url": "https://taller-ejemplo.com",
  "logo": "https://taller-ejemplo.com/logo.png",
  "sameAs": [
    "https://www.facebook.com/taller-ejemplo",
    "https://www.instagram.com/taller-ejemplo"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+57-300-000-0000",
    "contactType": "sales",
    "areaServed": "CO",
    "availableLanguage": ["Spanish"]
  }
}
</script>
```

### 3.2 LocalBusiness

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://taller-ejemplo.com/#local",
  "name": "Taller Ejemplo",
  "image": "https://taller-ejemplo.com/local.jpg",
  "url": "https://taller-ejemplo.com",
  "telephone": "+57-300-000-0000",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Cra 00 #00-00",
    "addressLocality": "Manizales",
    "addressRegion": "Caldas",
    "postalCode": "170001",
    "addressCountry": "CO"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": 5.0703, "longitude": -75.5138 },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
    "opens": "08:00", "closes": "18:00"
  }]
}
</script>
```

### 3.3 FAQPage (⚠️ ya NO da rich result — solo estructura/IA)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "¿Hacen envíos a toda Colombia?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Sí, enviamos a todo el país por transportadora. Cotiza por WhatsApp."
    }
  }, {
    "@type": "Question",
    "name": "¿Manejan garantía en los taller-ejemplo?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Todos nuestros taller-ejemplo tienen garantía de 6 meses."
    }
  }]
}
</script>
```

### 3.4 BreadcrumbList

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Inicio",
      "item": "https://taller-ejemplo.com" },
    { "@type": "ListItem", "position": 2, "name": "Catálogo",
      "item": "https://taller-ejemplo.com/catalogo" },
    { "@type": "ListItem", "position": 3, "name": "Silenciador Deportivo",
      "item": "https://taller-ejemplo.com/producto/silenciador-deportivo" }
  ]
}
</script>
```

> **Next.js:** inyecta el JSON-LD como `<script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(data)}} />` dentro del componente server (queda en el HTML inicial). **Angular:** insértalo server-side en el template o vía `DOCUMENT` durante SSR, no en `ngOnInit` puro de cliente.

---

## 4. Sitemaps y robots

### 4.1 XML sitemap

| Límite | Valor |
|---|---|
| URLs por archivo | **≤ 50,000** |
| Tamaño sin comprimir | **≤ 50 MB** |
| Por encima del límite | Usar **sitemap index** que apunte a varios sitemaps |

Reglas: listar **solo URLs canónicas, indexables y que devuelven 200**. `<lastmod>` **verídico** (Google lo usa para priorizar re-crawl; si mientes, lo ignora). Referenciar en `robots.txt` con `Sitemap:` y enviar en Search Console.

**Next.js** — `app/sitemap.ts` (file-based):

```ts
import type { MetadataRoute } from "next";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const products = await getProducts();
  return [
    { url: "https://taller-ejemplo.com", lastModified: new Date(), priority: 1 },
    ...products.map(p => ({
      url: `https://taller-ejemplo.com/producto/${p.slug}`,
      lastModified: p.updatedAt,
    })),
  ];
}
```

**Angular** — generar en build (script que escribe `sitemap.xml`) o server route en el SSR server; servirlo estático desde `/sitemap.xml`.

### 4.2 robots.txt — controla CRAWL, no INDEX

Punto crítico mal entendido: **robots.txt bloquea el rastreo, no la indexación.** Una URL bloqueada por robots puede **seguir indexada** (como URL desnuda, sin snippet) si otros la enlazan. Para des-indexar: **permitir el crawl** y poner `<meta name="robots" content="noindex">` (Google debe poder rastrear la página para ver el noindex).

| DO | DON'T |
|---|---|
| `noindex` (meta/header) para des-indexar, permitiendo crawl | `Disallow` en robots esperando que des-indexe |
| Permitir el rastreo de CSS/JS de render | Bloquear `/_next/` o assets críticos de render |
| Referenciar el sitemap | Dejar el sitemap huérfano |
| Decidir conscientemente si permites AI-crawlers (GPTBot, ClaudeBot, etc.) | Bloquearlos sin querer y perder visibilidad en respuestas de IA |

**Next.js** — `app/robots.ts`:

```ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: "*", allow: "/", disallow: ["/admin", "/api"] }],
    sitemap: "https://taller-ejemplo.com/sitemap.xml",
  };
}
```

Permitir/denegar AI-crawlers es una **decisión de negocio**, no técnica: `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`. Decláralo explícito.

---

## 5. Estrategia de rendering (SSR/SSG/ISR) y crawlability

**El hecho duro de 2026:** análisis de Vercel/MERJ sobre **500M+ fetches de GPTBot** encontró **cero ejecución de JS**. ClaudeBot y PerplexityBot tampoco renderizan JS. Solo Googlebot (WRS) y Gemini ejecutan JS — y Googlebot lo hace en una **segunda ola diferida** de renderizado. Conclusión: **contenido solo-CSR es invisible** para la mayoría de crawlers de IA y llega tarde/parcial a Google.

| Estrategia | Cuándo | CWV / Crawl |
|---|---|---|
| **SSG** (estático en build) | Contenido que no cambia por request (landing, docs, blog) | Mejor TTFB, HTML completo para todos los crawlers |
| **ISR** (revalidate) | Catálogo/productos que cambian pero no en cada request | Casi-SSG con frescura; excelente para e-commerce |
| **SSR** (por request) | Contenido personalizado/tiempo-real | HTML completo, pero cachea o TTFB sufre |
| **CSR-only** | Dashboards tras login, apps internas | ❌ Nunca para páginas que deben rankear/indexar |

**Regla:** todo lo que debe indexarse o aparecer en respuestas de IA → **SSR/SSG/ISR**. CSR solo para lo que va detrás de autenticación.

**Cómo verificar** que el crawler ve tu contenido:
1. Search Console → URL Inspection → **"View crawled page"** (el HTML que Google realmente recibió).
2. `curl https://tu-url` (sin JS) — ¿está el contenido en la respuesta?
3. DevTools con JS desactivado — ¿se ve el contenido?

**Next.js App Router:** Server Components por defecto (0 JS al cliente). `export const revalidate = 3600` para ISR; `generateStaticParams` para SSG de rutas dinámicas. Marca `'use client'` solo en las islas interactivas.

### 5.1 Reducir hydration (palanca directa de INP)

La hidratación es de los mayores contribuyentes a INP. Estrategia RSC + islands:

| DO | DON'T |
|---|---|
| Server-render lo estático (RSC = 0 JS de cliente, 0 hydration) | Hidratar toda la página como un solo árbol |
| `'use client'` solo en componentes interactivos (islas) | `'use client'` en el layout raíz |
| Streaming SSR + Suspense para trocear | Bloquear todo hasta que todo esté listo |
| Code-splitting / lazy de lo below-the-fold | Cargar el bundle entero upfront |

Presupuesto JS orientativo: **≤ 300-400 KB gzipped** para páginas interactivas (convención, no ley oficial). Recorta third-party scripts agresivamente.

---

## 6. Angular SSR + hydration (específico)

Sin hidratación no-destructiva, Angular **destruye y re-renderiza** el DOM que vino del servidor → flicker, hit de LCP y CLS. El fix documentado:

```ts
// app.config.ts
import { provideClientHydration } from "@angular/platform-browser";

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(),   // hidratación no-destructiva
    // ...
  ],
};
```

| DO | DON'T |
|---|---|
| `provideClientHydration()` (no-destructive hydration) | SSR sin hydration → re-render + flicker |
| **Prerender** de rutas estáticas (SSG en Angular) | SSR por request para páginas estáticas |
| `Title`/`Meta` services por ruta (server-side) | Setear meta solo en cliente |
| Routing **HTML5** (no hash `#`) | `useHash: true` → URLs no rastreables limpiamente |
| Reservar espacio para evitar reflow de hidratación | Contenido que cambia de tamaño al hidratar → CLS |

---

## 7. Image SEO

| DO | DON'T |
|---|---|
| Servir **AVIF → WebP → JPEG** vía `<picture>` (o `next/image` que negocia solo) | Servir solo JPEG pesado |
| Siempre `width`/`height` (o `aspect-ratio`) | Omitir dimensiones → CLS |
| `loading="lazy"` en below-the-fold | Lazy-load del hero/logo/LCP |
| `fetchpriority="high"` en la **única** imagen LCP | Varias imágenes con prioridad alta |
| `srcset` con 3-5 variantes + `sizes` preciso | Una sola resolución para todos los viewports |
| `alt` descriptivo (keyword natural) | `alt=""` en imágenes de contenido o alt stuffing |

Soporte de formato (early-2026, caniuse): **WebP ~96.4%**, **AVIF ~94.9%** (Safari 16+). AVIF ~50% más liviano que JPEG; WebP ~25-35%. Las imágenes suelen ser la palanca #1 de LCP.

```html
<picture>
  <source srcset="/foto.avif" type="image/avif">
  <source srcset="/foto.webp" type="image/webp">
  <img src="/foto.jpg" width="1200" height="800" loading="lazy"
       decoding="async" alt="Silenciador deportivo cromado">
</picture>
```

LQIP: reserva el espacio con `width`/`height` y muestra un placeholder (blur base64 / color dominante) que se cambia por el AVIF/WebP real → CLS ≈ 0 y mejor percepción. En Next.js: `placeholder="blur"`.

---

## 8. Font SEO / performance

| DO | DON'T |
|---|---|
| **Self-host WOFF2** subsetteado | `<link>` a Google Fonts (cache cross-site ya no ayuda: los navegadores **particionan el HTTP cache** por top-level site) |
| `font-display: swap` (o `optional` si CLS crítico) | Bloquear render esperando la fuente (FOIT largo) |
| `preload` de 1-2 fuentes críticas | Precargar 6 fuentes |
| **Variable font** si usas ≥ 3 pesos | Cargar 5 archivos de peso distintos |
| `size-adjust` / `ascent-override` en el fallback (evita CLS al swap) | `swap` sin métrica ajustada → reflow visible |

Subset agresivo: Roboto TTF ~168 KB → **~12 KB** subset WOFF2. Cache partitioning (documentado en navegadores modernos) hace que self-hosting sea net win vs CDN de fuentes.

**Next.js** — `next/font` self-hostea, subsettea y aplica `size-adjust` automáticamente (elimina CLS de fuentes):

```tsx
import { Inter } from "next/font/google"; // se self-hostea en build, no llama a Google en runtime
const inter = Inter({ subsets: ["latin"], display: "swap" });
```

```css
/* Fallback métrico manual (si no usas next/font) */
@font-face {
  font-family: "Inter Fallback";
  src: local("Arial");
  size-adjust: 107%;
  ascent-override: 90%;
}
```

---

## 9. HTML semántico

Ayuda a crawling, accesibilidad y **extracción por IA**.

| DO | DON'T |
|---|---|
| **Un H1 lógico primario** por página | Varios H1 compitiendo (tolerado por spec, pero un H1 es lo seguro) |
| Jerarquía ordenada H2 → H3 (sin saltar niveles) | H1 → H4 saltándose H2/H3 |
| Landmarks: `<header> <nav> <main> <article> <aside> <footer>` | Todo en `<div>` sopa |
| Keyword en H1 y primer párrafo, natural | Keyword stuffing en headings |
| Enlaces reales `<a href>` (los crawlers siguen `href`, no `onClick`) | Navegación solo-JS (`<div onClick>`) |
| Anchor text descriptivo | "clic aquí", "leer más" |

> "Exactamente un H1" es convención fuerte, no requisito de ranking (el HTML spec y Mueller toleran varios). Default seguro: **un H1 primario**.

### 9.1 Internal linking

Distribuye crawl equity con `<a href>` reales. Sin huérfanos; ~3 clics desde home; topical hub/cluster linking. En SPAs, asegúrate de emitir `href` real: **Next.js `<Link>`** y **Angular `routerLink`** ya lo hacen (el navegador ve el `href`), pero verifica que no lo rompes con handlers custom.

---

## 10. Mobile-first (transversal, no opcional)

Google indexa y rankea el **render móvil**. Consecuencias:

- El HTML móvil debe contener el **mismo contenido, structured data, links y metadata** que desktop. Contenido desktop-only es **invisible**.
- Responsive **single-URL** preferido sobre `m.dot`.
- CWV se juzga por separado en móvil (perfil normalmente más débil) → **presupuestá contra móvil**.
- Testea con **CPU throttle** (Lighthouse mid-tier ~4x, rango válido 2-10x; 6x es defendible pero es opinión, no estándar) y red Slow 4G. El reporte móvil es el que manda.

---

## ✅ Checklist pre-ship (pass/fail)

Marca cada uno antes de desplegar. Un fail = no shippear hasta resolver o justificar.

**Core Web Vitals (campo, p75, móvil)**
- [ ] LCP < 2.5 s — hero con `fetchpriority="high"`, no lazy, dimensionado
- [ ] INP < 200 ms — sin long tasks > 50 ms; `scheduler.yield()` con fallback en loops
- [ ] CLS < 0.1 — toda media/ads/iframes con `width`/`height` o `aspect-ratio`
- [ ] Verificado en **datos de campo** (CrUX/Search Console), no solo Lighthouse local
- [ ] Presupuestado contra **móvil throttled**, no desktop

**Rendering / crawlability**
- [ ] Contenido indexable renderizado en **SSR/SSG/ISR** (no CSR-only)
- [ ] `curl` sin JS / "View crawled page" muestra el contenido real
- [ ] Angular: `provideClientHydration()` activo; sin flicker de re-render
- [ ] Next: `'use client'` solo en islas; layout raíz es Server Component

**Metadata**
- [ ] `title` + `description` server-rendered, únicos por página
- [ ] Canonical self-referencing, absoluto, consistente con sitemap
- [ ] **Sin** `canonical` + `noindex` juntos
- [ ] OG image 1200×630 < 1 MB; `twitter:card = summary_large_image`
- [ ] hreflang recíproco + self-ref + `x-default` (si multi-idioma)

**Structured data**
- [ ] JSON-LD para los tipos que rinden (Organization / LocalBusiness / Product / Article / Breadcrumb)
- [ ] Datos **coinciden con el contenido visible**
- [ ] Validado en Rich Results Test **antes** de publicar
- [ ] **No** invertido en FAQ/HowTo esperando rich result (retirados)

**Sitemaps / robots**
- [ ] `sitemap.xml` con solo URLs canónicas, indexables, 200; `<lastmod>` verídico
- [ ] ≤ 50k URLs / ≤ 50 MB por archivo (o sitemap index)
- [ ] `robots.txt` referencia el sitemap; **no** bloquea CSS/JS de render
- [ ] Des-indexación vía `noindex` (crawl permitido), no vía `Disallow`
- [ ] Decisión explícita sobre AI-crawlers (GPTBot/ClaudeBot/…)

**Imágenes / fuentes**
- [ ] AVIF/WebP con fallback; dimensiones explícitas
- [ ] Solo el LCP con prioridad alta; below-the-fold lazy
- [ ] Fuentes self-hosted, subset, WOFF2, `font-display` + métrica de fallback

**HTML / links**
- [ ] Un H1 primario + jerarquía ordenada; landmarks semánticos
- [ ] Navegación con `<a href>`/`<Link>`/`routerLink` reales; sin huérfanos
- [ ] Anchor text descriptivo

**Mobile-first**
- [ ] Paridad total de contenido/metadata/structured data móvil ↔ desktop

**No-hacer (verificar ausencia)**
- [ ] ❌ Sin FID, AMP, keyword stuffing, texto oculto
- [ ] ❌ Sin markup esperando rich result de FAQ/HowTo/tipos retirados 2025-2026
- [ ] ❌ `llms.txt` no vendido como deliverable SEO obligatorio

---

### Fuentes clave
- Core Web Vitals / umbrales: Google Search Central — web.dev/articles/vitals
- Fetch Priority (caso 2.6s→1.9s): web.dev/articles/fetch-priority · MDN "Fixing image LCP"
- Long tasks / `scheduler.yield()`: web.dev "Optimize long tasks" · MDN scheduler.yield (Chrome 129/Firefox 142, no Baseline)
- AI-crawlers no ejecutan JS (500M fetches): estudio Vercel/MERJ
- Retiros de schema (FAQ, HowTo y tipos de nicho) — Search Engine Land / SEJ; revalidar fechas exactas en Google Search Central
- llms.txt sin soporte Google: SEJ / Search Engine Roundtable (Mueller, Illyes) · Ahrefs (~97% cero requests)
- Next.js Metadata API / `sitemap.ts` / `robots.ts` / `next/font`: docs Next.js
- Angular hydration: angular.dev SSR/hydration guidance

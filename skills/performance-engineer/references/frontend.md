# Frontend Performance

Leer cuando haya que analizar bundle size, optimizar Angular/React/Next.js, o mejorar Core Web Vitals (LCP/INP/CLS).

## Angular 21 — Optimizaciones clave

```bash
# Analizar bundle size
npx nx build mfe-fleet --stats-json
npx webpack-bundle-analyzer dist/mfe-fleet/stats.json

# Source map explorer
npx source-map-explorer dist/mfe-fleet/main.*.js
```

**Checklist Angular performance:**
- [ ] `ChangeDetectionStrategy.OnPush` en TODOS los componentes
- [ ] `trackBy` en todos los `@for`
- [ ] `@defer` para componentes below-the-fold
- [ ] Lazy loading de MFEs (ya implementado en Telemetria)
- [ ] `takeUntilDestroyed()` en subscriptions (evita leaks)
- [ ] `preconnect` en `index.html` para APIs externas
- [ ] Bundle size budget en `angular.json`

## Core Web Vitals Targets

| Métrica | Bueno | Necesita mejora | Malo |
|---------|-------|-----------------|------|
| LCP | < 2.5s | 2.5s–4s | > 4s |
| INP | < 200ms | 200–500ms | > 500ms |
| CLS | < 0.1 | 0.1–0.25 | > 0.25 |

**Quick wins para LCP:**
- `<img loading="eager" fetchpriority="high">` en imagen hero
- Preload de fuentes: `<link rel="preload" as="font">`
- SSR / SSG para contenido crítico (Next.js)
- Optimizar imagen hero: WebP + srcset + width/height explícitos

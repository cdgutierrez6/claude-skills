---
name: ui-ux-pro-max
description: "UI/UX design intelligence. 67 styles, 96 palettes, 57 font pairings, 25 charts, 13 stacks (React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui). Actions: plan, build, create, design, implement, review, fix, improve, optimize, enhance, refactor, check UI/UX code. Projects: website, landing page, dashboard, admin panel, e-commerce, SaaS, portfolio, blog, mobile app, .html, .tsx, .vue, .svelte. Elements: button, modal, navbar, sidebar, card, table, form, chart. Styles: glassmorphism, claymorphism, minimalism, brutalism, neumorphism, bento grid, dark mode, responsive, skeuomorphism, flat design. Topics: color palette, accessibility, animation, layout, typography, font pairing, spacing, hover, shadow, gradient. Integrations: shadcn/ui MCP for component search and examples."
---
# UI/UX Pro Max - Design Intelligence

Comprehensive design guide for web and mobile applications. Contains 67 styles, 96 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 13 technology stacks. Searchable database with priority-based recommendations.

The knowledge lives in `data/*.csv` (styles, colors, typography, products, landing, charts, ux-guidelines, react-performance, web-interface, icons, ui-reasoning + `data/stacks/`) and is queried through the Python CLI in `scripts/search.py` — never reproduce those tables inline; run the CLI.

## When to Apply

Reference these guidelines when:
- Designing new UI components or pages
- Choosing color palettes and typography
- Reviewing code for UX issues
- Building landing pages or dashboards
- Implementing accessibility requirements

## Operating Workflow (read first)

When the user requests UI/UX work (design, build, create, implement, review, fix, improve):

1. **Analyze** the request → product type, style keywords, industry, and target stack.
2. **Generate the design system first (REQUIRED).** Run `scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]`. It searches 5 domains in parallel (product, style, color, landing, typography), applies the reasoning rules in `ui-reasoning.csv`, and returns a complete system (pattern, style, colors, typography, effects) plus anti-patterns to avoid. Add `--persist` to save a `design-system/MASTER.md` + page-overrides tree for cross-session retrieval.
3. **Supplement** with `--domain <domain>` searches for extra detail (`style`, `chart`, `ux`, `typography`, `landing`, …).
4. **Apply stack guidelines** with `--stack <stack>`. If the user names no stack, **default to `html-tailwind`**.

Then synthesize the design system + detailed searches and implement. Exact commands, the `--persist` Master+overrides pattern, output formats, tips, a worked example, and Python prerequisites/install are in `references/workflow.md`; the full `--domain` / `--stack` catalogs are in `references/cli-reference.md`.

## Rule Categories by Priority

| Priority | Category | Impact | Domain |
|----------|----------|--------|--------|
| 1 | Accessibility | CRITICAL | `ux` |
| 2 | Touch & Interaction | CRITICAL | `ux` |
| 3 | Performance | HIGH | `ux` |
| 4 | Layout & Responsive | HIGH | `ux` |
| 5 | Typography & Color | MEDIUM | `typography`, `color` |
| 6 | Animation | MEDIUM | `ux` |
| 7 | Style Selection | MEDIUM | `style`, `product` |
| 8 | Charts & Data | LOW | `chart` |

## Quick Reference — Non-Negotiable Rules

### 1. Accessibility (CRITICAL)

- `color-contrast` - Minimum 4.5:1 ratio for normal text
- `focus-states` - Visible focus rings on interactive elements
- `alt-text` - Descriptive alt text for meaningful images
- `aria-labels` - aria-label for icon-only buttons
- `keyboard-nav` - Tab order matches visual order
- `form-labels` - Use label with for attribute

### 2. Touch & Interaction (CRITICAL)

- `touch-target-size` - Minimum 44x44px touch targets
- `hover-vs-tap` - Use click/tap for primary interactions
- `loading-buttons` - Disable button during async operations
- `error-feedback` - Clear error messages near problem
- `cursor-pointer` - Add cursor-pointer to clickable elements

### 3. Performance (HIGH)

- `image-optimization` - Use WebP, srcset, lazy loading
- `reduced-motion` - Check prefers-reduced-motion
- `content-jumping` - Reserve space for async content

### 4. Layout & Responsive (HIGH)

- `viewport-meta` - width=device-width initial-scale=1
- `readable-font-size` - Minimum 16px body text on mobile
- `horizontal-scroll` - Ensure content fits viewport width
- `z-index-management` - Define z-index scale (10, 20, 30, 50)

### 5. Typography & Color (MEDIUM)

- `line-height` - Use 1.5-1.75 for body text
- `line-length` - Limit to 65-75 characters per line
- `font-pairing` - Match heading/body font personalities

### 6. Animation (MEDIUM)

- `duration-timing` - Use 150-300ms for micro-interactions
- `transform-performance` - Use transform/opacity, not width/height
- `loading-states` - Skeleton screens or spinners

### 7. Style Selection (MEDIUM)

- `style-match` - Match style to product type
- `consistency` - Use same style across all pages
- `no-emoji-icons` - Use SVG icons, not emojis

### 8. Charts & Data (LOW)

- `chart-type` - Match chart type to data type
- `color-guidance` - Use accessible color palettes
- `data-table` - Provide table alternative for accessibility

## Referencias

- `references/workflow.md` — read when you need the full operating procedure: the 4 steps in detail, `--design-system` generation, the `--persist` Master + page-overrides pattern, output formats, tips, a worked example, and Python prerequisites/install.
- `references/cli-reference.md` — read when you need the exact search surface: the Available Domains and Available Stacks tables for `--domain` / `--stack`.
- `references/professional-rules.md` — read before delivering UI: the "Common Rules for Professional UI" Do/Don't tables (icons, cursor/hover, light/dark contrast, layout) and the full Pre-Delivery Checklist.

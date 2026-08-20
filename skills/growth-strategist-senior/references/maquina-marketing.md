# La Máquina de Marketing con IA — arquitectura y flujo

> **Léeme para entender la máquina completa.** Es un EQUIPO integrado de marketing que se enciende con un
> comando en CADA negocio nuevo: **entrevista** al dueño, **construye** los entregables (landing nivel
> taller-ejemplo.com o mejor + copy + kit + medición) y los pasa por un **gate de calidad** antes de
> que el humano publique. Entrypoint: el comando `/lanzar-negocio`. Contrato de reglas: [[reglas-duras]].

## Principio rector (arquitectura)
Clean Architecture aplicada a una máquina de prompts: **el equipo vive UNA sola vez en `~/.claude`; cada
negocio solo aporta DATOS.** La dependencia apunta hacia adentro: el dominio (reglas duras + esquema del
Contexto) no depende de ningún negocio; los negocios dependen de la máquina, nunca al revés.

```
~/.claude/                                    # GLOBAL — la máquina (única fuente de verdad)
├── skills/
│   ├── growth-strategist-senior/  SKILL.md   # DIRECTOR / front-door que orquesta
│   │   └── references/ reglas-duras · maquina-marketing (este) · landing
│   ├── copywriter-senior/         SKILL.md   # COPY (headlines, CTAs, mensajes wa.me)
│   │   └── references/ copy-kit
│   ├── po-senior/                             # DISCOVERY (ya existía)
│   ├── web-design-pro-2026/                   # ARTE + LANDING + SEO/AEO (ya existía, se reusa)
│   └── llm-judge/                             # JUEZ / GATE (ya existía)
├── commands/   lanzar-negocio.md              # ENTRYPOINT — se corre en CADA negocio
├── templates/marketing/                       # esquemas de dato y de salida
│   ├── contexto-brief.md      ★ esquema de intake (el "modelo de datos")
│   ├── kit-publicacion.md       skeleton del kit de salida
│   └── medicion.md              skeleton del plan de medición
└── workflows/  lanzamiento-marketing.js       # MOTOR runtime multi-agente (Fases 2–8 + gate)

<negocio>/marketing/                           # POR NEGOCIO — SOLO datos, CERO máquina copiada
├── contexto/contexto.md                       # brief LLENO = único input variable
└── resultados/
    ├── _runs/<runId>/  ...                     # cada corrida aislada (idempotencia)
    ├── estrategia.md · discovery.md · copy/ · landing/ · kit-publicacion/ · medicion.md
    └── veredicto-juez.md
```

## El flujo — 8 fases + gate del Juez
Invariante: **cada fase lee [[reglas-duras]] + el `contexto.md`** antes de producir. La salida de una fase
es la entrada de la siguiente; nunca se salta un artefacto.

| # | Fase | Dueño (skill invocada por nombre) | Salida | Humano |
|---|---|---|---|---|
| 1 | **Intake / Entrevista** | `growth-strategist-senior` (esquema = [[contexto-brief]]) | `contexto/contexto.md` validado | **SÍ** responde |
| 2 | **Estrategia** | `growth-strategist-senior` | `estrategia.md`: ICP, valor, ángulos, mapa de canales (un wa.me por canal), métrica | — |
| 3 | **Discovery** | `po-senior` | `discovery.md`: JTBD, objeciones, voice-of-customer, prueba social real | — |
| 4 | **Copy** | `copywriter-senior` | `copy/`: landing/anuncios/WhatsApp/Estados; wa.me con texto por canal | — |
| 5 | **Arte + Landing** | `web-design-pro-2026` → ui-ux/ux/frontend/creative | `landing/`: landing pro, barra = taller-ejemplo **o mejor** | — |
| 6 | **SEO / AEO** | `web-design-pro-2026` (gate técnico) | landing con metadata/JSON-LD/CWV | — |
| 7 | **Kit de publicación** | `growth-strategist-senior` (+ kit-publicacion.md) | `kit-publicacion/`: grilla, posts, links por canal | **SÍ publica** |
| 8 | **Medición** | `growth-strategist-senior` (+ medicion.md) | `medicion.md`: conteo por canal + ritual | **SÍ mide** |
| — | **GATE — Juez** | `llm-judge` | `veredicto-juez.md`: APROBADO/RECHAZADO por regla | Escala si el auto-fix se agota |

**El juez corre dos veces:** (a) **gate temprano y barato** sobre el copy de Fase 4 — atrapar violaciones
ANTES de construir la landing cara (*fail cheap first*); (b) **gate final** sobre el bundle completo, antes
de publicar. Ambas leen el MISMO `reglas-duras.md`. Fases 5 y 6 comparten dueño (una invocación de skill).

**Paralelismo (REGLA #8):** Fase 2 ∥ Fase 3 (solo dependen del Contexto) · canales de copy en paralelo
dentro de Fase 4 · Fase 5-6 ∥ Fase 8 (medición solo necesita el mapa de canales, listo tras Fase 2).

**Bucle de corrección** (patrón de `/sdd`): juez RECHAZADO → el fix vuelve SOLO a la fase dueña del
entregable señalado → se regenera → se re-juzga. Acotado a **2 iteraciones**; luego escala al humano con
las violaciones concretas. **Nunca se descarta trabajo** (REGLA #6.0).

## Una sola fuente de verdad
- Todo aguas abajo es **función de `(contexto.md, reglas-duras.md, playbooks)`**. El único parámetro que
  varía entre negocios es `contexto.md` (+ el `cwd`). Misma máquina + mismo contexto → misma clase de salida.
- `reglas-duras.md` = **contrato único**; ninguna skill re-enuncia las reglas en su prompt (derivarían).
- `contexto-brief.md` = **esquema del dato**; los consumidores validan campos obligatorios (fail-fast en Fase 1).
- Frontera **copy↔landing = el copy deck**: `copywriter-senior` es dueño de las PALABRAS; `web-design-pro-2026`
  de lo VISUAL + SEO. La landing consume el deck, no inventa copy.

## Checkpoints humanos (la máquina nunca actúa irreversible)
Intake (respuestas del dueño) · **publicación** (el dueño da el clic — la máquina jamás postea sola) ·
escalación del juez (si el auto-fix se agota). Verificación renderizada real (`/gstack-qa`) antes de entregar.

## Riesgos conocidos (mitigación)
1. **GIGO — Contexto pobre → salida genérica** (riesgo #1). *Mit.:* campos obligatorios + fail-fast; Discovery exige voice-of-customer real; el juez marca "genérico/plantilla" como hallazgo.
2. **"taller-ejemplo o mejor" NO es binario** → el juez no gatea gusto. *Mit.:* la barra se traduce a lo objetivable (anti-flat + CWV + a11y + reglas duras + render real). El juez garantiza **"no viola reglas + cumple gates técnicos", NO "premium"**.
3. **Bucle de corrección infinito.** *Mit.:* máx 2 iteraciones → escala; gate temprano barato sobre copy antes de construir.
4. **Deriva máquina↔negocio** (copiar el workflow en un negocio o meter reglas de un negocio en lo global). *Mit.:* invariante duro (nada de negocio en `~/.claude`); cualquier `if (negocio === ...)` es violación.
5. **wa.me mal instrumentado → se pierde la métrica.** *Mit.:* Fase 2 genera los links distintos; el juez verifica un link por canal; ver [[medicion]].
6. **El último eslabón es humano y falla en la práctica.** Por seguridad (regla 5) la máquina no publica ni mide sola → produce pero el dueño no ejecuta → cero resultado. *Mit.:* checklist de lanzamiento paso a paso + ritual explícito. **Nombrarlo sin maquillar: la máquina es asistencia de marketing, no un growth-team autónomo; no cierra el loop de negocio sola.**

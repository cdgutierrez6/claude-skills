# Compatibilidad — lo que las skills asumen y tú quizá no tengas

> **EN:** These skills were written inside a specific Claude Code setup. They cite a few commands,
> rules and notes that live outside this repo. Nothing here breaks them — but this file spells out
> every external reference so you are not left guessing. Read it once after installing.

Las 37 skills salieron de una instalación real, con su propio `CLAUDE.md`, sus comandos y sus notas.
Al publicarlas, esas referencias externas quedaron dentro del texto. **Ninguna rompe una skill**
(Claude las lee como prosa), pero sin contexto son huecos. Aquí está el contexto.

---

## 1. Comandos que las skills mencionan y que no vienen en este repo

| Comando | Qué hace en el setup original | Qué usar en su lugar |
|---|---|---|
| `/gstack-qa` | QA de una web en Chromium real | El **browser preview** de Claude Code, o Playwright. Lo que importa es el concepto: **verificar mirando el render**, no dar por bueno un "compila". Varias skills ya lo nombran así ("Chromium real / `/gstack-qa`"). |
| `/gstack-cso` | Auditoría de seguridad ejecutable sobre el diff | La skill **`security-review`** (viene incluida en Claude Code) como pasada ejecutable, después de `senior-security-auditor` que es la canónica de amenaza/OWASP. |
| `/sdd` | Pipeline de 7 fases sobre OpenSpec para trabajo grande o irreversible | La cadena del README: `senior-project-planner` → `arquitecto-senior` → build → review en paralelo → `llm-judge`. Es el mismo backbone sin la capa de specs versionadas. |
| `/lanzar-negocio` | Orquesta la máquina de marketing de punta a punta | `growth-strategist-senior` + `copywriter-senior` + `analytics-measurement-senior`, alimentados por los archivos de [`templates/marketing/`](templates/marketing). |
| `/graphify` | Convierte un repo en un grafo de conocimiento navegable | Herramienta de terceros, no redistribuida aquí. Se puede ignorar: ninguna skill depende de ella para funcionar. |

`gstack` es de **Garry Tan** (MIT) y `graphify` también es de terceros: por eso no están en este repo.
Consíguelos de sus autores si los quieres.

**No son comandos, aunque lo parezcan.** Estas dos aparecen entre backticks pero son rutas URL
dentro de ejemplos de código, no algo que se invoque: `/servicios` (valor de ejemplo del campo
`page` en el esquema de analítica) y `/public` (carpeta de assets estáticos). Se declaran aquí
porque el validador exige que **toda** cadena con esa forma esté explicada — si algo no es una
referencia real, se dice, y así el documento sigue siendo un registro completo.

---

## 2. Las "REGLA #N" que citan las skills

Vienen del `CLAUDE.md` personal del autor, que no se publica. Las skills las citan como autoridad
("por REGLA #6.0, no borres el core"). Esto es lo que dice cada una, para que la cita signifique algo:

| Regla | Qué dice |
|---|---|
| **#1 — Proceso proporcional al riesgo** | No toda tarea merece la misma ceremonia. **T0** (typo, rename, bug en 1–2 archivos): directo + verificar. **T1** (feature acotada): planner → build → review. **T2** (proyecto nuevo, cambio de schema, pagos): pipeline completo. Correr el pipeline entero para un typo es tan malo como no correrlo para un cambio de schema. |
| **#3 — Un solo pipeline** | Es la regla que invoca la frase "un solo pipeline". Todo trabajo de desarrollo va por **un único pipeline multi-agente donde los agentes invocan las skills reales y estas dialogan entre sí** — ni skills sueltas sin orquestación, ni orquestación con agentes genéricos: `senior-project-planner` → `backend-senior`/`frontend-senior` → **`tech-lead-senior` + `senior-security-auditor` + `senior-qa-engineer` en PARALELO** → `llm-judge`. Ese review en paralelo se lanza **siempre**. Única excepción: la edición mecánica de una o dos líneas, y se anuncia antes de hacerla. Cuando la tarea toca pantallas o producto, entran también `ux-senior`/`ui-ux-pro-max` y `po-senior` dentro del mismo pipeline. |
| **#4 — Verificación y juez** | Nada se da por "hecho" sin **ejecutarlo**. "Compila" ≠ "funciona". `llm-judge` actúa como auditor externo porque el mismo modelo no ve sus propios puntos ciegos, y se gradúa por riesgo: **obligatorio** en trabajo pesado, **recomendado** en una feature acotada, **no aplica** a una edición trivial. |
| **#6 — Socio crítico, no asistente complaciente** | Evaluar antes de obedecer: si la propuesta tiene un defecto, decirlo **antes** de implementarla. Sin adulación de relleno. Reporte honesto de qué se hizo, qué **no**, y qué falló. No inventar certeza: "no sé" es una respuesta válida. La severidad va por delante de la cortesía: un riesgo de seguridad o de pérdida de datos se dice directo y primero. Cerrar todo trabajo sustancial con oportunidades de mejora concretas. **Calibración, y no es opcional:** esto **no** es llevar la contraria por deporte — el contrarianismo es tan inútil como la adulación. Cuando el humano tiene razón, se dice rápido y se sigue. |
| **#6.0 — Nunca borrar el core sin confirmación** | La más citada (13 veces). Si un cambio **elimina, reemplaza o reduce el alcance** de algo existente, eso **no es pulido: es una decisión de producto**. Se para y se explica qué se quita, por qué, **qué se pierde**, y cuál es la alternativa de dejarlo igual — y se exigen **tres confirmaciones en intercambios distintos**. "Optimización", "buenas prácticas", "deuda técnica" o "deprecado" **no son licencia** para borrar: basta un TODO. **Preferir AÑADIR sobre QUITAR**, y ante la duda, no se toca. |
| **#7 — Precedencia de skills** | Estas skills custom son la **fuente de verdad** de su dominio. Los plugins que se solapan (`engineering:code-review`, `design:*`, etc.) son **segunda opinión**, solo si el humano la pide. Sin esta regla, decenas de skills compiten por el mismo trigger y diluyen el pipeline. |
| **#8 — Hooks y paralelismo** | Dos mitades. Lo repetible y verificable (formato, lint, tests, escaneo de secretos) va en **hooks**, no en prosa que el modelo deba recordar: el modelo piensa, los hooks vigilan. Y por defecto, **lo independiente se paraleliza** en vez de encadenarlo — es la mitad que invocan las skills cuando escriben "Paralelismo (REGLA #8): Fase 2 ∥ Fase 3". |
| **#9 — Arquitectura y código mantenible** | Es un **gate, no un deseo**: si el código funciona pero no se entiende, no está listo. El entregable no es "compila" ni "pasa los tests", es código que un humano cualquiera abra en un año y entienda. Nombres que revelan intención, funciones cortas de una sola responsabilidad, **una sola fuente de verdad por dato**, sin duplicación silenciosa ni estado global oculto, errores explícitos. SOLID y los patrones se aplican **con criterio, no por cargo cult**. **Los comentarios explican el PORQUÉ**, y un comentario que miente es peor que ninguno: si el código cambia, el comentario cambia en el mismo commit. **Un invariante frágil se prueba, no se comenta.** Ante dos soluciones correctas gana la que se entiende sin explicación. Y mantenibilidad **nunca** es licencia para borrar: se mejora añadiendo (ver #6.0). |

> **`REGLA #0` es distinta:** esa **sí** está definida dentro de `analytics-measurement-senior`
> («CLIC ≠ CONVERSACIÓN»). No es una referencia externa, no hay nada que buscar.

---

## 3. Notas privadas citadas

Tres wikilinks apuntan a notas personales del autor. Son **citas de apoyo**, no infraestructura:
lo esencial de cada una se resume aquí, así que no falta nada.

| Wikilink | Dónde aparece | Lo que aportaba |
|---|---|---|
| `[[reference-3d-scroll-r3f-blender]]` | `creative-frontend-max/references/kinetic-type.md` | React Three Fiber **v9 exige React 19**: en un proyecto con React 18 hay que fijar R3F v8 y drei v9. Y **`overflow-x` en `<body>` rompe `position: sticky`** — va en `<html>`. |
| `[[project-vision-frontier-partlens]]` | `growth-strategist-senior/references/reglas-duras.md` | La línea roja de privacidad: **identificar personas sin su consentimiento está vetado**, sin importar lo fácil que sea técnicamente. |
| `[[feedback-nextjs-csp-dev-hydration]]` | `web-design-pro-2026/references/scroll-3d-depth-2026.md` | Una **CSP sin `'unsafe-eval'` rompe la hidratación de Next.js en desarrollo**. La CSP se aplica condicionada por `NODE_ENV`, estricta solo en producción. La propia skill ya lo dice en esa línea. |

Los demás wikilinks (`[[medicion]]`, `[[contexto-brief]]`, `[[landing]]`, `[[reglas-duras]]`,
`[[maquina-marketing]]`, `[[kit-publicacion]]`) **sí resuelven dentro de este repo**: están en
[`templates/marketing/`](templates/marketing) y en `skills/growth-strategist-senior/references/`.

---

## 4. Qué NO necesitas

Nada de lo anterior es un requisito de instalación. Las skills funcionan recién clonadas:
`senior-project-planner`, `arquitecto-senior`, `backend-senior`, `frontend-senior`,
`tech-lead-senior`, `senior-security-auditor`, `senior-qa-engineer` y `llm-judge` no dependen de
ningún comando externo. Este documento existe para que, cuando una skill cite algo que no tienes,
sepas exactamente qué era y con qué sustituirlo.

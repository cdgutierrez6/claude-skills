# Rúbricas de Evaluación — LLM Judge

Última actualización: 2026-06-02
Versión: 1.0

---

## Rúbrica: Código Backend (Node.js/Express)

### Correctitud Técnica (peso 30%)
| Score | Criterio |
|-------|----------|
| 5 | Código correcto, maneja todos los casos, no hay lógica errónea |
| 4 | Correcto en happy path, 1-2 edge cases menores sin manejar |
| 3 | Funciona pero con supuestos frágiles o lógica cuestionable |
| 2 | Bugs evidentes que causarían fallas en condiciones normales |
| 1 | Código incorrecto, no funcionaría ni en happy path |

### Seguridad (peso 25%)
| Score | Criterio |
|-------|----------|
| 5 | Input sanitizado, auth verificada, no secrets expuestos, SQL parametrizado, rate limiting considerado |
| 4 | Seguridad sólida con 1 gap menor no crítico |
| 3 | Protecciones básicas presentes pero hay superficie de ataque no abordada |
| 2 | Vulnerabilidad evidente (SQL injection posible, secrets hardcoded, auth bypasseable) |
| 1 | Múltiples vulnerabilidades críticas |

### Completitud (peso 20%)
| Score | Criterio |
|-------|----------|
| 5 | Maneja éxito, errores, edge cases, logging, rollback si aplica |
| 4 | Completo con 1-2 casos no críticos sin manejar |
| 3 | Funcionalidad core presente, error handling básico |
| 2 | Solo happy path, sin manejo de errores |
| 1 | Fragmento incompleto, no ejecutable |

### Mantenibilidad (peso 15%)
| Score | Criterio |
|-------|----------|
| 5 | Código limpio, nombres descriptivos, funciones pequeñas, sin duplicación |
| 4 | Buena estructura con 1-2 áreas mejorables |
| 3 | Funcional pero mezclando responsabilidades o nombres poco claros |
| 2 | Difícil de entender, alto acoplamiento |
| 1 | Código espagueti, imposible de mantener |

### Consistencia con Codebase (peso 10%)
| Score | Criterio |
|-------|----------|
| 5 | Sigue exactamente las convenciones del proyecto (naming, estructura, imports) |
| 4 | Consistente con variaciones menores justificadas |
| 3 | Mezcla estilos, algunos imports o patrones inconsistentes |
| 2 | Introduce patrones nuevos sin justificación |
| 1 | Completamente inconsistente con el stack existente |

---

## Rúbrica: Código Frontend (React/Vite)

### Correctitud Técnica (peso 30%)
- 5: Hooks correctos, no hay memory leaks, efectos con deps correctas
- 4: Funcional con 1-2 optimizaciones menores pendientes
- 3: Funciona pero con re-renders innecesarios o deps incompletas
- 2: Hooks mal usados (useEffect sin deps, state mutation directa)
- 1: No funcionaría (import incorrecto, JSX inválido, etc.)

### Seguridad Frontend (peso 25%)
- 5: No dangerouslySetInnerHTML sin sanitizar, no secrets en JS bundle, CORS correcto
- 4: Seguro con gap menor
- 3: Básicamente seguro pero con XSS potencial no crítico
- 2: XSS evidente o secrets expuestos en bundle
- 1: Múltiples vulnerabilidades client-side

---

## Rúbrica: Decisiones de Arquitectura

### Correctitud de la Decisión (peso 40%)
- 5: La decisión resuelve el problema real, no el síntoma
- 4: Resuelve el problema con trade-offs aceptables
- 3: Solución funcional pero no óptima para el contexto
- 2: Resuelve el síntoma pero no la causa raíz
- 1: Introduce más problemas de los que resuelve

### Escalabilidad (peso 30%)
- 5: Escala a 10x sin rediseño
- 4: Escala a 10x con ajustes menores
- 3: Escala a 3x, necesita refactor para más
- 2: Solución que no escala más allá del caso actual
- 1: Crea deuda técnica estructural

### Reversibilidad (peso 30%)
- 5: Fácilmente reversible o modificable
- 4: Reversible con esfuerzo razonable
- 3: Cambiar requeriría refactor significativo
- 2: Crea dependencias difíciles de romper
- 1: Lock-in irreversible

---

## Umbrales de veredicto

| Score Final | Veredicto |
|-------------|-----------|
| 4.5 - 5.0 | ✅ CONFIRMA APROBADO |
| 3.5 - 4.4 | ⚠️ APROBADO CON OBSERVACIONES |
| 2.5 - 3.4 | ❌ RECHAZA — requiere correcciones importantes |
| < 2.5 | 🔴 RECHAZA CATEGÓRICO — volver al inicio del pipeline |

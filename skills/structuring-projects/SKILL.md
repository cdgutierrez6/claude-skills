---
name: structuring-projects
description: >
  Convierte las mejores oportunidades analizadas en propuestas ejecutables con una
  plantilla fija: Qué es | Por qué es buen proyecto (según los 4 marcos) | Modelo de
  monetización | Implementación por fases con inversión estimada en COP | Nivel de
  confiabilidad /10 con justificación. Es el Paso 6 del innovation-pipeline. Se usa cuando
  una oportunidad ya pasó el filtrado y el análisis y necesita convertirse en un plan
  vendible, realista y por fases con números. Output: las propuestas completas, cada una
  con su plantilla diligenciada.
---

# Structuring Projects — Paso 6 del innovation-pipeline

Rol: **product strategist senior + fractional CTO** con olfato de negocio. Tomas las
oportunidades analizadas (Paso 5) y las conviertes en **propuestas ejecutables y
vendibles**. Es donde la idea se vuelve un plan con fases y números reales en COP.

## Disciplina senior de estructuración (lo que un veterano no se salta)

- **Riesgo más alto primero (de-risking).** La F0 no es "lo más fácil de programar": es **lo que prueba la suposición más riesgosa al menor costo**. Si la apuesta es "la gente pagará por esto", la F0 debe cobrarle a alguien — no construir infraestructura.
- **Cada fase entrega valor cobrable por sí sola.** Nada de "Fase 1 = backend sin cliente". Si una fase no se puede vender o validar, no es una fase, es una excusa.
- **Unit economics desde el día 1.** Precio, CAC (cómo y cuánto cuesta conseguir un cliente), margen y **costo por uso** (tokens de LLM, mensajes de WhatsApp, fee de pago). Un SaaS que cuesta más operar que lo que cobra no es negocio.
- **Build vs. buy.** No construyas lo que un SaaS de bajo costo ya resuelve; integra y enfoca el esfuerzo en lo diferencial. Construir de más es la forma más común de quemar plata.
- **Costeo realista CO** (ver método en `reference/project-template.md`): estima en COP con tarifas reales del mercado colombiano de desarrollo + infra + costos por transacción. Da rangos, no falsa precisión.
- **Honestidad en la confiabilidad /10.** Descuenta por suposiciones no validadas. Un 9/10 sin demanda probada es un 5/10 con maquillaje.

## Cómo estructurar
1. Para cada oportunidad, diligencia **toda** la plantilla de `reference/project-template.md`. Sin campos vacíos.
2. **"Por qué es buen proyecto"** se ancla en los 4 marcos del Paso 5 (Ackoff, UCD, agentic commerce, interoperabilidad financiera) — no inventes razones nuevas.
3. **Monetización SaaS:** si la oportunidad es producto/SaaS, apóyate en `saas-monetization-expert` para pricing/tiers/métricas — opcional, no obligatorio (responsabilidad única).

## Handoff a construcción (REGLA #1)
Esta skill **NO escribe código**: entrega el plan. Cuando Cristian decida construir, el
siguiente paso es `/sdd <descripción>` (o `/senior-project-planner` para el PRD técnico).
Déjalo explícito al final de cada propuesta de PRODUCTO.

## Output
Las propuestas completas, cada una con la plantilla de `reference/project-template.md`
diligenciada. Pásalas al Paso 7 (`reporting-daily-brief`).

---
name: filtering-opportunities
description: >
  Puntúa de 0 a 10 cada señal de tecnología y de demanda con un rubro de viabilidad
  ponderado (tamaño/dolor de mercado CO-LATAM 20%, baja fricción sobre infra Bre-B/WhatsApp
  15%, claridad de monetización con ruta <6 meses 20%, madurez técnica 15%,
  defensibilidad/timing 15%, demanda verificada con presupuesto 15%) y descarta todo lo
  que quede por debajo de 6.5. Es el Paso 4 del innovation-pipeline. Se usa para rankear,
  priorizar y eliminar oportunidades antes del análisis profundo. Output: lista ordenada
  por score con justificación de 1 línea por finalista y motivo de descarte de las
  eliminadas.
---

# Filtering Opportunities — Paso 4 del innovation-pipeline

Rol: **analista de inversión / VC con criterio de fundador.** Tomas las señales de tech
(`T*`) y de demanda (`D*`) y las **conviertes en oportunidades puntuadas**. Aquí sí se
opina y se descarta: tu trabajo es **separar el grano de la paja** antes del análisis
profundo (Paso 5). Un veterano descarta sin culpa: la disciplina de decir "no" es el 80%
del valor.

## Cómo puntuar

1. Para cada oportunidad, aplica el rubro de `reference/scoring-rubric.md`: 6 dimensiones ponderadas, score 0-10.
2. **Combina cuando tenga sentido:** una señal tech (T) + una demanda (D) que la pide suele ser una oportunidad más fuerte que cualquiera por separado. Nómbrala como oportunidad nueva (`O1`, `O2`, …) citando sus IDs origen.
3. **Demanda verificada sube el score:** explícita > con presupuesto > pedida por muchos > parche manual ya existente.
4. **Umbral:** descarta todo con score **< 6.5**.
5. **Gate del pipeline:** si quedan menos de 3 finalistas, avisa al orquestador para volver a los Pasos 1-2 con criterios más amplios.

## Criterio senior por encima del rubro (lo que el número no captura)

El rubro es un **piso, no un techo**: ordena y elimina la basura, pero el juicio manda en
los bordes. Antes de dejar pasar un finalista, contesta las **3 preguntas que matan o
salvan**:

1. **¿Por qué ahora?** ¿Qué catalizador de este año la hace posible/urgente hoy y no hace dos años? Sin "why now", baja. Y ojo: el catalizador debe estar **disponible hoy** (infra/estándares existentes), no solo anunciado — un decreto sin estándares publicados es "why-now prematuro" y se descarta.
2. **¿Cuál es la ventaja injusta?** ¿Por qué Cristian y no cualquiera con un fin de semana libre? (Conocimiento de dominio, stack ya montado —pgvector, n8n, WhatsApp—, acceso a clientes, timing.)
3. **¿Cómo llega al cliente?** Si no hay canal de distribución claro y barato, el mejor producto muere. En CO/LATAM: WhatsApp, comunidades, boca a boca, marketplaces.

**El mayor riesgo casi nunca es técnico: es "a nadie le importa".** Pondera demanda
verificada por encima de elegancia técnica. Detalle de falsos positivos y desempates en
`reference/scoring-rubric.md`.

## Output

**Finalistas (≥ 6.5), ordenados por score desc:**

| Oportunidad | IDs origen | Score | Tipo (producto/servicio) | Why now / ventaja (1 línea) |
|-------------|-----------|-------|--------------------------|------------------------------|
| O1 — … | T3+D2 | 8.4 | producto | … |

**Descartadas (< 6.5):** lista corta con `oportunidad — score — motivo de descarte en 1 línea`.

Pasa solo los finalistas al Paso 5.

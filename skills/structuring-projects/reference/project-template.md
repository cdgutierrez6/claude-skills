# Plantilla de propuesta ejecutable — structuring-projects

Diligenciar completa, una por oportunidad. Sin campos vacíos.

---

## [Nombre del proyecto]
**Tipo:** PRODUCTO (SaaS escalable) | SERVICIO (caja inmediata)
**Oportunidad origen:** [IDs O*/T*/D* del pipeline]

### 1. Qué es
Descripción en 2-3 líneas: qué hace, para quién, en qué canal (web / móvil / WhatsApp).
Y el **job-to-be-done** que resuelve (el progreso real del cliente).

### 2. Por qué es buen proyecto (según los 4 marcos)
- **Ackoff (sistémico):** qué restricción autoimpuesta disuelve / qué interacción mejora.
- **UCD (usuario):** por qué lo adopta (carga cognitiva, palanca de comportamiento, valor inmediato, confianza).
- **Agentic commerce:** rol del agente conversacional / WhatsApp + RAG (si aplica).
- **Interoperabilidad financiera:** cómo cobra sin fricción (Bre-B/QR/billeteras/Open Finance) (si aplica).

### 3. Modelo de monetización + unit economics
- **Cómo cobra:** suscripción mensual / fee por transacción / setup + retainer / pago único.
- **Precio sugerido (COP):** rango concreto.
- **Quién paga y por qué:** apóyate en la demanda verificada del Paso 2 (ideal: alguien que ya paga por un parche peor).
- **Unit economics:** margen estimado, **costo por uso** (tokens LLM, mensajes WhatsApp, fee de pago), y CAC aproximado (cómo se consigue el cliente).

### 4. Implementación por fases (riesgo más alto primero, inversión en COP)

| Fase | Suposición que prueba / valor cobrable | Entregable | Duración | Inversión estimada (COP) |
|------|----------------------------------------|-----------|----------|--------------------------|
| F0 — MVP cobrable | la apuesta más riesgosa | … | p.ej. 2-3 sem | $ |
| F1 — … | … | … | … | $ |
| F2 — … | … | … | … | $ |

**Inversión total estimada:** $ COP. **Stack sugerido:** [breve; reusa lo de Cristian — Node/React/PostgreSQL/pgvector/n8n/WhatsApp API].

### 5. Nivel de confiabilidad /10
**Score: X/10.** Justificación honesta: madurez técnica + demanda verificada + riesgos abiertos.
Qué bajaría / subiría el número, y cuál es la suposición que más urge validar.

### 6. Siguiente paso para construir (solo PRODUCTO)
`/sdd [descripción de una línea]` — handoff al pipeline de construcción (REGLA #1).

---

## Método de costeo realista en COP (no usar precios fijos — estimar y verificar)
La inversión se estima, no se adivina. Construye el número con estas piezas y **verifica
las tarifas vigentes** (cambian con el tiempo y por perfil):
- **Esfuerzo de desarrollo:** horas × tarifa de mercado CO del rol (junior/semi/senior difieren mucho). Si lo hace Cristian, el costo es tiempo de oportunidad.
- **Infra mensual:** VPS/hosting (Cristian ya usa Hostinger), base de datos, dominios, certificados.
- **Costos por transacción/uso:** tokens de LLM por conversación (estimar mensajes × tokens × precio del modelo elegido), mensajes/plantillas de WhatsApp API, comisión de la pasarela/Bre-B.
- **Terceros:** APIs de pago, correo, SMS, almacenamiento.
- **Regla:** da **rangos** (mín–máx), no falsa precisión. Marca cada cifra como "estimado, verificar".

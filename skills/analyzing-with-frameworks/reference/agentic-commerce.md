# Marco 3 — Agentic commerce (mobile-first, WhatsApp + RAG)

## Idea central
En LATAM el comercio vive en el **móvil y en WhatsApp**: para muchas pymes WhatsApp es a
la vez la vitrina, el CRM y la caja. Un **agente de IA conversacional** —con arquitectura
RAG sobre el catálogo, precios e inventario del negocio— puede **vender, recomendar,
cotizar, agendar y atender en lenguaje natural** dentro del mismo chat donde el cliente ya
está, sin apps nuevas ni formularios. Sustituye trabajo manual de atención/ventas y
atiende 24/7.

## Arquitectura de referencia (lo que un ingeniero senior monta)
- **Canal:** WhatsApp Business Platform (Cloud API o vía BSP). Respeta ventana de servicio de 24h y **plantillas (HSM) pre-aprobadas** para mensajes proactivos; el usuario debe dar **opt-in**.
- **Cerebro:** LLM (Claude) como agente con **tool use** (consultar stock, crear pedido, generar link de pago, agendar). Selección de modelo por costo/latencia: modelo rápido para enrutar/clasificar, modelo fuerte para conversación compleja.
- **Conocimiento (RAG):** recuperación sobre catálogo, inventario, FAQ y políticas. Vector DB → **pgvector** (ya en el stack de Cristian). Chunking del catálogo por producto/variante; re-indexar cuando cambie el inventario para no responder con datos viejos.
- **Estado/sesión:** memoria de conversación e idempotencia en la creación de pedidos (un "sí" no debe generar dos órdenes).
- **Guardrails:** el LLM **nunca inventa precio ni stock** — esos vienen de un tool call a la fuente de verdad. Validar y confirmar antes de cobrar.
- **Handoff humano:** escalar a una persona cuando hay duda, queja o monto alto.
- **Costo:** prompt caching del catálogo/políticas para bajar tokens; medir costo por conversación contra el ticket.

## Por qué gana en LATAM
- Cero fricción de instalación (ya tienen WhatsApp).
- Lenguaje natural > navegar una UI para usuarios no-técnicos.
- Combina perfecto con el **Marco 4**: vender *y cobrar* dentro del mismo chat (link Bre-B / QR), sin redirecciones.

## Riesgos a vigilar
- Alucinación de precios/disponibilidad (mitiga con tool use, no con prompt).
- Políticas de WhatsApp (bloqueo por spam si abusas de plantillas o sin opt-in).
- Latencia y costo si todo va al modelo más caro.

## Cómo escribir el párrafo
¿Puede esta oportunidad vivir (total o parcial) como agente conversacional en WhatsApp?
¿El RAG sobre los datos del negocio reemplaza trabajo manual? ¿Dónde están los guardrails
de precio/stock y el handoff humano?

## Pregunta guía
*"¿Cómo se materializa esta oportunidad como un agente conversacional RAG en WhatsApp que vende o atiende, qué trabajo manual reemplaza, y cómo evita alucinar precios/stock?"*

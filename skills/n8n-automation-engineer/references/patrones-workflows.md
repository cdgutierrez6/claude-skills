# Patrones de workflows n8n

Diagramas de flujo de nodos (FASE 3 de la metodología) para los tres workflows que aparecen en casi
todo proyecto. Reproduce el patrón; sustituye rutas, campos y servicios por los de tu contexto
(`<repo>/.claude/contexto/n8n-workflows.md`).

---

## 1. Pago externo → activar plan

El más delicado: mueve dinero y otorga acceso.

```
Node: Webhook (POST /webhook/<pasarela>-payment)
  ↓
Node: IF (verifica la firma HMAC del proveedor)   ← OBLIGATORIO, primero
  ↓ válida
Node: IF (estado del pago == "aprobado")
  ↓ sí
Node: HTTP Request
  POST <api>/admin/activate-plan
  Headers: X-Internal-Key: {{$env.INTERNAL_API_KEY}}
  Body: { email: {{$json["data"]["buyer"]["email"]}}, plan: "<plan>" }
  ↓
Node: HTTP Request (email de bienvenida)
  ↓
Node: IF (status == 200)
  ↓ no
Node: Set (log del error) + Stop
```

**La verificación HMAC va antes que cualquier otra cosa**, incluso antes de mirar el estado del
pago — ver [`hmac-y-comandos-ops.md`](hmac-y-comandos-ops.md). Sin ella, cualquiera que conozca la
URL del webhook activa planes de pago enviando un JSON con el estado "aprobado". Es la diferencia
entre un webhook y un endpoint de regalos.

**Idempotencia:** las pasarelas reintentan. Si el mismo pago llega dos veces, no debe activar dos
veces ni cobrar dos veces. Guarda el id de transacción del proveedor y descarta los repetidos: es
una comprobación de tres líneas que evita la incidencia más embarazosa que hay.

---

## 2. Webhook → capturar lead

```
Node: Webhook (POST /webhook/nuevo-lead)
  ↓
Node: HTTP Request
  POST <api>/webhooks/lead-capture
  Body: { <campos exactos del contrato> }
  ↓
Node: IF (res.body.success == true)
  ↓ sí                  ↓ no
Node: Notificar equipo  Node: Email de error
```

Este webhook suele nacer **público** porque lo llama una landing sin sesión. Público no es lo mismo
que sin defensa: ponle rate limiting por IP, un captcha o un token de origen, y valida el esquema
antes de escribir en la base. Si no, tu tabla de leads es un formulario de spam abierto a internet.

---

## 3. Cron → reporte periódico con LLM

```
Node: Schedule Trigger (<día y hora>)
  ↓
Node: HTTP Request (GET <api>/stats, autenticado)
  ↓
Node: HTTP Request (API del LLM — análisis)
  ↓
Node: Email (enviar el reporte al equipo)
```

Dos cosas que fallan siempre en este patrón:

- **La zona horaria del Schedule Trigger** es la del servidor, no la tuya. Un reporte "de los
  lunes a las 9" puede salir el domingo por la noche. Fíjala explícitamente en la configuración
  de n8n.
- **Si el paso del LLM falla, el reporte no se envía y nadie se entera.** Configura el "On Error"
  del workflow para que avise: un cron silencioso puede llevar meses roto.

---

## Aplican a los tres

- **1 workflow = 1 responsabilidad.** Un workflow que hace tres cosas falla de tres maneras y no se
  puede reintentar por partes.
- **Nunca pongas credenciales en el JSON del workflow** — usa `{{$env.NOMBRE}}` o las credenciales
  de n8n. El JSON se exporta, se comparte y acaba commiteado.
- **Prueba con un `curl` real antes de darlo por hecho.** n8n falla en ejecución, no al guardar:
  un campo mal nombrado se descubre cuando el flujo ya corrió contra producción.

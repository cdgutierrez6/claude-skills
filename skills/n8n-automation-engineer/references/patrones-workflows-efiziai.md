# Patrones de workflows n8n — EfiziAI

Diagramas de flujo de nodos (FASE 3 de la metodología) para los 3 workflows canónicos de EfiziAI. Reproduce estos patrones tal cual al diseñar el JSON del workflow.

---

## Hotmart Payment → Activar plan (correcto)

```
Node: Webhook (POST /webhook/hotmart-payment)
  ↓
Node: IF (verifica hottok HMAC-SHA256) ← OBLIGATORIO
  ↓ válido
Node: IF (event.data.purchase.status == 'APPROVED')
  ↓ sí
Node: HTTP Request
  POST https://api.efiziai.com/api/admin/activate-plan
  Headers: Authorization: Bearer <ADMIN_JWT>
  Body: { email: {{$json["data"]["buyer"]["email"]}}, plan: "premium" }
  ↓
Node: HTTP Request (Resend — welcome email)
  ↓
Node: IF (verificar que res.status == 200)
  ↓ error
Node: Set (log error) + Stop

```

La validación HMAC del hottok es obligatoria antes de procesar — ver `hmac-y-comandos-ops.md`.

---

## Webhook → Capturar lead de landing

```
Node: Webhook (POST /webhook/nuevo-lead)
  ↓
Node: HTTP Request
  POST https://api.efiziai.com/api/webhooks/lead-capture
  Body: { company_name, email, niche, phone, ... }
  ↓
Node: IF (res.body.success == true)
  ↓ sí                ↓ no
Node: Notify team   Node: Email error
```

---

## Cron → Reporte semanal AI

```
Node: Schedule Trigger (lunes 9am)
  ↓
Node: HTTP Request (GET /api/leads/stats con JWT)
  ↓
Node: HTTP Request (Claude API — análisis)
  ↓
Node: Gmail/Resend (enviar reporte a Cristian)
```

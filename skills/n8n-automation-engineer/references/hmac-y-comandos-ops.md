# Validación HMAC (Hotmart) y comandos de operación n8n

Código de validación de firma y comandos Docker para operar el contenedor `root-n8n-1`.

---

## Validación HMAC — Hotmart (OBLIGATORIO antes de procesar)

```javascript
// Implementar en n8n con Code node:
const crypto = require('crypto');
const payload = JSON.stringify($input.item.json.body);
const signature = $input.item.json.headers['x-hotmart-signature'];
const HOTMART_TOKEN = $env.HOTMART_WEBHOOK_TOKEN;

const expected = crypto.createHmac('sha256', HOTMART_TOKEN)
  .update(payload).digest('hex');

if (signature !== `sha256=${expected}`) {
  throw new Error('Firma Hotmart inválida — posible ataque');
}

return $input.item;
```

---

## Comandos de Gestión n8n

```bash
# Ver logs de n8n
docker logs root-n8n-1 --tail 50 -f

# Backup de workflows
docker exec root-n8n-1 n8n export:workflow --all --output=/backup/workflows.json

# Restaurar workflows
docker exec root-n8n-1 n8n import:workflow --input=/backup/workflows.json

# Reiniciar n8n
docker compose restart root-n8n-1
```

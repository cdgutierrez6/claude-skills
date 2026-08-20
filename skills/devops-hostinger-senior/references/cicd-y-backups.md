# CI/CD y backups — EfiziAI

## GitHub Actions CI/CD — Auto-deploy en push a main

```yaml
# .github/workflows/deploy.yml
name: Deploy to Hostinger VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/efiziai-platform
            git pull origin main
            cd /root
            docker compose build root-backend-1 root-crm-frontend-1
            docker compose up -d --no-deps root-backend-1 root-crm-frontend-1
            echo "✅ Deploy completado $(date)"
```

**Secrets en GitHub** (`Settings → Secrets → Actions`):
- `VPS_HOST` → IP del VPS Hostinger
- `VPS_USER` → root
- `VPS_SSH_KEY` → clave SSH privada (PEM)

## Script de Backup Automático

```bash
#!/bin/bash
# /opt/efiziai-platform/deploy/backup-db.sh
# Cron: 0 2 * * * /opt/efiziai-platform/deploy/backup-db.sh

BACKUP_DIR="/opt/efiziai-platform/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"
docker exec root-postgres-1 pg_dump -U agency_user -Fc b2b_agency > "$BACKUP_DIR/b2b_agency_$DATE.dump"
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
echo "✅ Backup creado: b2b_agency_$DATE.dump"
```

# Comandos de operación — EfiziAI VPS

Comandos exactos para operar la infraestructura de EfiziAI en el VPS Hostinger. Verifica siempre el nombre real del contenedor y de la DB antes de ejecutar.

## Contenido

- [PostgreSQL (DB EfiziAI)](#postgresql-db-efiziai)
- [Migraciones DB — Proceso estándar](#migraciones-db--proceso-estándar)
- [Verificar Variables de Entorno del Backend](#verificar-variables-de-entorno-del-backend)
- [Deploy / Actualización](#deploy--actualización)
- [Traefik (SSL / Routing)](#traefik-ssl--routing)
- [Monitoring y Salud](#monitoring-y-salud)

## PostgreSQL (DB EfiziAI)
```bash
# Conectar a la DB
docker exec -it root-postgres-1 psql -U agency_user -d b2b_agency

# Backup completo (binario)
docker exec root-postgres-1 pg_dump -U agency_user -Fc b2b_agency > backup_$(date +%Y%m%d_%H%M%S).dump

# Backup SQL plano (legible, para migraciones)
docker exec root-postgres-1 pg_dump -U agency_user --no-owner b2b_agency > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar desde dump binario
docker exec -i root-postgres-1 pg_restore -U agency_user -d b2b_agency < backup.dump

# Ver qué tablas y VIEWs existen
docker exec root-postgres-1 psql -U agency_user -d b2b_agency -c "\dt"
docker exec root-postgres-1 psql -U agency_user -d b2b_agency -c "\dv"

# Verificar columnas de una tabla
docker exec root-postgres-1 psql -U agency_user -d b2b_agency -c "\d+ leads"

# Ver logs de postgres
docker logs root-postgres-1 --tail 50
```

## Migraciones DB — Proceso estándar
```bash
# 1. Copiar migración al container
docker cp /opt/efiziai-platform/backend/migrations/00X_descripcion.sql \
  root-postgres-1:/tmp/00X_descripcion.sql

# 2. Ejecutar migración
docker exec root-postgres-1 psql -U agency_user -d b2b_agency \
  -f /tmp/00X_descripcion.sql

# 3. Verificar resultado
docker exec root-postgres-1 psql -U agency_user -d b2b_agency \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"

# Ejecutar run-migrations.sh (script completo)
cd /opt/efiziai-platform && git pull && bash backend/migrations/run-migrations.sh
```

## Verificar Variables de Entorno del Backend
```bash
# Verificar JWT_SECRET (debe tener ≥ 32 chars)
docker exec root-backend-1 printenv JWT_SECRET | wc -c

# Ver todas las env vars del backend (sin mostrar values)
docker exec root-backend-1 printenv | cut -d= -f1 | sort

# Ver logs del backend en tiempo real
docker logs root-backend-1 --tail 50 -f
```

## Deploy / Actualización
```bash
# Actualizar un servicio específico
cd /opt/efiziai-platform && git pull origin main
cd /root && docker compose build root-backend-1 && docker compose up -d root-backend-1

# Deploy completo
cd /opt/efiziai-platform && git pull origin main
cd /root && docker compose build && docker compose up -d

# Ver estado de todos los servicios
docker compose ps

# Logs en tiempo real (múltiples servicios)
docker compose logs -f root-backend-1 root-n8n-1

# Reiniciar sin rebuild
docker compose restart root-backend-1
```

## Traefik (SSL / Routing)
```bash
# Ver logs de Traefik
docker logs traefik --tail 50

# Verificar que los routers están activos
docker exec traefik wget -q -O - http://localhost:8080/api/http/routers | python3 -m json.tool

# Forzar renovación de certificados Let's Encrypt
docker exec traefik rm /letsencrypt/acme.json
docker restart traefik
```

## Monitoring y Salud
```bash
# Ver uso de recursos por contenedor
docker stats --no-stream

# Espacio en disco
df -h && docker system df

# Health check manual del backend
curl -s https://api.efiziai.com/api/health | python3 -m json.tool

# Health check de la DB
docker exec root-postgres-1 pg_isready -U agency_user -d b2b_agency

# Limpiar imágenes/contenedores viejos
docker system prune -f --volumes
```

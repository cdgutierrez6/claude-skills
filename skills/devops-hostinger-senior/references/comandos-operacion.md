# Comandos de operación — VPS con Docker Compose

Comandos exactos para operar un stack de Docker Compose en un VPS propio.

> **Los marcadores `<...>` son obligatorios de sustituir.** El mapa con los nombres reales de este
> servidor está en `<repo>/.claude/contexto/infraestructura-vps.md`, no aquí. **Confirma siempre el
> nombre real del contenedor y de la base de datos antes de ejecutar** — estos comandos actúan sobre
> datos de producción y varios no tienen vuelta atrás.

## Contenido

- [PostgreSQL](#postgresql)
- [Migraciones DB — proceso estándar](#migraciones-db--proceso-estándar)
- [Variables de entorno](#variables-de-entorno)
- [Deploy / actualización](#deploy--actualización)
- [Traefik (SSL / routing)](#traefik-ssl--routing)
- [Monitoring y salud](#monitoring-y-salud)

## PostgreSQL

```bash
# Conectar a la DB
docker exec -it <contenedor-db> psql -U <usuario> -d <basededatos>

# Backup completo (binario, para restaurar)
docker exec <contenedor-db> pg_dump -U <usuario> -Fc <basededatos> > backup_$(date +%Y%m%d_%H%M%S).dump

# Backup SQL plano (legible, para inspeccionar o migrar de motor)
docker exec <contenedor-db> pg_dump -U <usuario> --no-owner <basededatos> > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar desde dump binario  -- SOBRESCRIBE datos: verifica la base destino
docker exec -i <contenedor-db> pg_restore -U <usuario> -d <basededatos> < backup.dump

# Qué tablas y VIEWs existen
docker exec <contenedor-db> psql -U <usuario> -d <basededatos> -c "\dt"
docker exec <contenedor-db> psql -U <usuario> -d <basededatos> -c "\dv"

# Columnas reales de una tabla (antes de escribir una query o una migración)
docker exec <contenedor-db> psql -U <usuario> -d <basededatos> -c "\d+ <tabla>"

# Logs de postgres
docker logs <contenedor-db> --tail 50
```

**`-Fc` frente a SQL plano:** el binario restaura selectivamente y comprime; el plano se lee con un
editor. Para el backup automático usa binario; para revisar qué cambió, plano.

## Migraciones DB — proceso estándar

```bash
# 1. Copiar la migración al contenedor
docker cp <ruta-deploy>/migrations/00X_descripcion.sql \
  <contenedor-db>:/tmp/00X_descripcion.sql

# 2. Ejecutar
docker exec <contenedor-db> psql -U <usuario> -d <basededatos> \
  -f /tmp/00X_descripcion.sql

# 3. Verificar el resultado
docker exec <contenedor-db> psql -U <usuario> -d <basededatos> \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
```

**Haz un backup antes del paso 2, siempre.** Una migración con un `DROP` mal escrito no avisa, y en
un VPS sin réplica el dump es la única vuelta atrás.

Verifica el esquema real (`\d+`) antes de escribir la migración: asumir la forma de una tabla es la
causa más común de migración fallida a mitad, que es el peor sitio donde fallar.

## Variables de entorno

```bash
# Listar los NOMBRES de las variables, sin exponer los valores
docker exec <contenedor> printenv | cut -d= -f1 | sort

# Comprobar que un secreto cumple la longitud mínima, sin imprimirlo
docker exec <contenedor> printenv <NOMBRE_DEL_SECRETO> | wc -c

# Logs en tiempo real
docker logs <contenedor> --tail 50 -f
```

**Nunca imprimas el valor de un secreto en una terminal.** Queda en el historial del shell, en el
scrollback y en cualquier captura. Para comprobarlo, mide su longitud o compara su hash.

## Deploy / actualización

```bash
# Actualizar un servicio concreto (el resto sigue corriendo)
cd <ruta-deploy> && git pull origin <rama>
cd <ruta-compose> && docker compose build <servicio> && docker compose up -d --no-deps <servicio>

# Deploy completo
cd <ruta-deploy> && git pull origin <rama>
cd <ruta-compose> && docker compose build && docker compose up -d

# Estado de todos los servicios
docker compose ps

# Logs en tiempo real de varios servicios
docker compose logs -f <servicio-a> <servicio-b>

# Reiniciar sin reconstruir (para recoger un cambio de variable de entorno)
docker compose restart <servicio>
```

**`--no-deps` es lo que evita el downtime ajeno:** sin él, Compose recrea también las dependencias
del servicio, y tumbas la base de datos por actualizar el frontend.

## Traefik (SSL / routing)

```bash
# Logs
docker logs traefik --tail 50

# Routers activos (confirma que tu servicio está realmente enrutado)
docker exec traefik wget -q -O - http://localhost:8080/api/http/routers | python3 -m json.tool

# Forzar renovación de certificados  -- ULTIMO RECURSO
docker exec traefik rm /letsencrypt/acme.json
docker restart traefik
```

⚠️ Borrar `acme.json` tira **todos** los certificados y los pide de nuevo. Let's Encrypt limita a
unas pocas emisiones por dominio y semana: si el fallo real era de DNS, te quedas sin certificado y
sin poder reemitir. Antes de borrarlo, confirma en los logs que el problema es el fichero y no la
resolución del dominio o el puerto 80 cerrado.

## Monitoring y salud

```bash
# Recursos por contenedor
docker stats --no-stream

# Disco -- el "todo se cayó" más frecuente
df -h && docker system df

# Health check de la API
curl -s https://<subdominio-api>/api/health | python3 -m json.tool

# Health check de la DB
docker exec <contenedor-db> pg_isready -U <usuario> -d <basededatos>

# Limpiar imágenes y contenedores viejos
docker system prune -f
```

⚠️ `docker system prune --volumes` borra también los **volúmenes sin usar**, y un volumen que
Compose no ve en ese momento cuenta como sin usar. Ahí es donde vive la base de datos. Usa `prune`
sin `--volumes` salvo que hayas verificado uno por uno qué se va a borrar:

```bash
docker volume ls
docker system prune --volumes --dry-run   # revisa la lista ANTES
```

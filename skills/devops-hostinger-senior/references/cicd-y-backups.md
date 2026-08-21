# CI/CD y backups en un VPS propio

Los valores concretos de una instalación (host, rutas, nombres de servicio) van en
`<repo>/.claude/contexto/infraestructura-vps.md`. Aquí está el patrón.

## GitHub Actions — auto-deploy en push

```yaml
# .github/workflows/deploy.yml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -e
            cd <ruta-deploy>
            git pull origin main
            cd <ruta-compose>
            docker compose build <servicio-a> <servicio-b>
            docker compose up -d --no-deps <servicio-a> <servicio-b>
```

**Secrets en GitHub** (`Settings → Secrets → Actions`) — nunca en el YAML:

| Secret | Qué es |
|---|---|
| `VPS_HOST` | IP o host del servidor |
| `VPS_USER` | usuario con el que entra el deploy (**no `root`**, ver abajo) |
| `VPS_SSH_KEY` | clave SSH privada, solo para deploy |

**`set -e` no es opcional.** Sin él, si el `git pull` falla el script sigue y reconstruye la versión
anterior, dejando un deploy "verde" que no desplegó nada.

### El usuario del deploy no debe ser `root`

Es el atajo por defecto y el más caro. Esa clave SSH vive en GitHub: cualquiera que comprometa el
repo, un workflow de un fork, o una action de terceros con acceso a secrets, obtiene **el servidor
entero**, no solo la aplicación.

Crea un usuario acotado:

```bash
# En el VPS
adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy                 # docker sin sudo
chown -R deploy:deploy <ruta-deploy>      # solo su propio directorio
```

Y en `/etc/ssh/sshd_config.d/deploy.conf`, límita esa clave a lo que necesita:

```
Match User deploy
    PasswordAuthentication no
    PermitTTY no
    X11Forwarding no
    AllowTcpForwarding no
```

Pertenecer al grupo `docker` **equivale a root** en la práctica (se puede montar `/` dentro de un
contenedor). No es una defensa perfecta: es reducir la superficie y poder revocar el acceso del
deploy sin tocar tus propias llaves. Si necesitas separación real, expón el deploy como un endpoint
que dispare un script concreto en vez de dar shell.

### Rotar la clave de deploy

```bash
ssh-keygen -t ed25519 -f deploy_key -N "" -C "github-actions-deploy"
# la pública va a ~deploy/.ssh/authorized_keys en el VPS
# la privada va a Settings → Secrets → VPS_SSH_KEY, y el fichero local se borra
```

Rótala cuando alguien deje el equipo, cuando se filtre cualquier cosa del repo, o cada seis meses.

## Backup automático de la base de datos

```bash
#!/bin/bash
# <ruta-deploy>/deploy/backup-db.sh
# Cron: 0 2 * * * <ruta-deploy>/deploy/backup-db.sh >> /var/log/backup-db.log 2>&1
set -euo pipefail

BACKUP_DIR="<ruta-de-backups>"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"
docker exec <contenedor-db> pg_dump -U <usuario> -Fc <basededatos> \
  > "$BACKUP_DIR/<basededatos>_$DATE.dump"

# Falla ruidosamente si el dump salió vacío o truncado
test -s "$BACKUP_DIR/<basededatos>_$DATE.dump"

find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
```

Tres cosas que separan un backup real de uno de mentira:

1. **`set -euo pipefail` y la comprobación de tamaño.** Sin ellas, si el contenedor está caído
   `pg_dump` escribe un fichero vacío, el `find` borra los buenos por antigüedad, y descubres que no
   tienes backups el día que los necesitas.
2. **El backup no puede vivir solo en el mismo servidor.** Un disco lleno, un `rm` mal dado o un
   ransomware se llevan la base y sus copias a la vez. Sincroniza a otro sitio (S3, otro VPS, o un
   `rclone` a almacenamiento externo) después del dump.
3. **Un backup no probado no es un backup.** Restaura uno en una base de pruebas cada cierto tiempo
   y comprueba que la aplicación arranca contra ella. Es la única forma de saber que funciona.

**El log importa.** Con `>> /var/log/backup-db.log 2>&1` en el cron, tienes dónde mirar; sin él, el
cron falla en silencio durante meses.

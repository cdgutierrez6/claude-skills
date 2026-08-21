# GitHub Actions — Patrones Profesionales

## Estructura de workflows recomendada

```
.github/
  workflows/
    ci.yml           # Lint + test en cada PR
    cd-staging.yml   # Deploy a staging en merge a develop
    cd-prod.yml      # Deploy a prod en merge a main (con approval)
    security.yml     # SAST + dependency scan semanal
    cleanup.yml      # Limpieza de recursos temporales
  actions/           # Composite actions reutilizables
```

## Patrones críticos a aplicar siempre

**Caching de dependencias:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

**OIDC para Azure (sin secrets de larga duración):**
```yaml
permissions:
  id-token: write
  contents: read
- uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

**Matrix builds para múltiples servicios (.NET microservicios):**
```yaml
strategy:
  matrix:
    service: [identity, fleet-assets, telemetry, geofencing, notifications]
  fail-fast: false
```

**Environments con required reviewers:**
```yaml
environment:
  name: production
  url: https://app.ejemplo.io
```

**Reusable workflows para DRY:**
```yaml
jobs:
  deploy:
    uses: ./.github/workflows/_deploy-service.yml
    with:
      service: identity
      image-tag: ${{ needs.build.outputs.image-tag }}
    secrets: inherit
```

## Security en CI/CD
- `trivy` para escaneo de imágenes Docker antes de push
- `gitleaks` o `trufflehog` para detección de secrets en commits
- `dependabot` para actualizaciones automáticas de dependencias
- `codeql` para análisis estático de seguridad
- SBOM (Software Bill of Materials) con `syft` en cada release

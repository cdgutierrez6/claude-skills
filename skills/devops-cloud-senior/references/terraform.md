# Terraform — Estructura Standard

```
infra/
  modules/
    app-service/    # Módulo reutilizable por servicio
    database/       # PostgreSQL / TimescaleDB
    networking/     # VNet, subnets, NSGs
  environments/
    staging/
      main.tf
      terraform.tfvars
    production/
      main.tf
      terraform.tfvars
  backend.tf        # Remote state (Azure Storage / S3)
```

**Reglas Terraform:**
- Remote state siempre (nunca local)
- State locking habilitado
- `terraform plan` en PR, `terraform apply` solo en merge
- Módulos versionados (`source = "git::...?ref=v1.2.0"`)
- `checkov` para security scanning del IaC

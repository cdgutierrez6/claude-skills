# GitHub Templates — PR e Issues

## PR Template (`.github/pull_request_template.md`)

```markdown
## What
<!-- Una línea: qué cambia este PR -->

## Why
<!-- Por qué es necesario este cambio -->

## How
<!-- Decisiones técnicas no obvias, alternativas descartadas -->

## Testing
- [ ] Unit tests agregados/actualizados
- [ ] Integration tests pasan localmente
- [ ] Probado manualmente en el flujo golden path

## Checklist
- [ ] No hay secrets hardcodeados
- [ ] Variables nuevas documentadas en `.env.example`
- [ ] Si hay cambio de schema: migration idempotente incluida
- [ ] Breaking changes documentados en CHANGELOG.md

## Screenshots / Videos
<!-- Solo si hay cambios de UI -->
```

## Issue Templates

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Report a bug
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: Description
      description: What happened? What did you expect?
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to Reproduce
      placeholder: "1. Go to...\n2. Click on...\n3. See error"
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: Environment
      placeholder: "OS: Windows 11, Node: 22.x, Branch: main"
```

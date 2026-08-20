# Deploy, Observabilidad y Checklist de Infraestructura Nueva

## Contenido
- [Estrategias de Deploy](#estrategias-de-deploy)
- [Observabilidad — Stack Recomendado](#observabilidad--stack-recomendado)
- [Checklist de Infraestructura Nueva](#checklist-de-infraestructura-nueva)

---

## Estrategias de Deploy

| Estrategia | Cuándo | Cómo |
|-----------|--------|------|
| Rolling | Default, bajo riesgo | `maxSurge: 1, maxUnavailable: 0` |
| Blue/Green | Features grandes, rollback inmediato | 2 entornos, switch de tráfico |
| Canary | Alto riesgo, validar con % real | 5% → 25% → 100% con métricas |
| Feature flags | Sin deploy para activar | LaunchDarkly / env var / DB flag |

---

## Observabilidad — Stack Recomendado

```
Logs:     Loki + Fluentd/Fluent Bit → Grafana
Métricas: Prometheus → Grafana
Trazas:   OpenTelemetry → Jaeger / Tempo
Alertas:  Alertmanager → PagerDuty / Slack
SLOs:     Sloth (Prometheus-based SLO framework)
```

**SLOs mínimos a definir:**
- Availability: 99.9% uptime (permite 8.7h downtime/año)
- Latency: P95 < 500ms, P99 < 2s
- Error rate: < 0.1% de requests con 5xx

---

## Checklist de Infraestructura Nueva

### Pre-deploy
- [ ] Dockerfile multi-stage con usuario no-root
- [ ] Health checks implementados (liveness + readiness)
- [ ] Secrets en vault (Azure Key Vault / AWS Secrets Manager)
- [ ] Variables de entorno documentadas en `.env.example`
- [ ] Resource limits definidos (CPU + memoria)
- [ ] Trivy scan: 0 CVEs críticos/altos

### CI/CD
- [ ] Pipeline CI: lint → test → build → security scan → push
- [ ] Pipeline CD: pull de registry → deploy → smoke test → notificación
- [ ] Environments con required reviewers para producción
- [ ] Rollback automático si health check falla post-deploy
- [ ] Notificaciones de deploy en Slack/Teams

### Post-deploy
- [ ] Dashboards Grafana con métricas del nuevo servicio
- [ ] Alertas configuradas (error rate, latencia, CPU, memoria)
- [ ] Runbook documentado (cómo hacer rollback manual)
- [ ] Backup configurado para datos persistentes

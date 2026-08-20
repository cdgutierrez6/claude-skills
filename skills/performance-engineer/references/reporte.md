# Deliverable — Reporte de Performance

Leer al cerrar cualquier análisis: es el formato obligatorio de entrega. Siempre entregar un reporte con este formato.

```
## Performance Analysis Report

### Baseline (antes)
- Endpoint/Query: [identificador]
- Carga: [N usuarios concurrentes / N RPS]
- P50: Xms | P95: Xms | P99: Xms
- Error rate: X%

### Bottleneck identificado
- Causa raíz: [descripción concreta]
- Evidencia: [EXPLAIN output / flamegraph / profiler output]

### Fix aplicado
- Cambio: [descripción técnica exacta]
- Archivos modificados: [lista]

### Resultado (después)
- P50: Xms (▼X%) | P95: Xms (▼X%) | P99: Xms (▼X%)
- Error rate: X% (▼X%)
- Mejora de throughput: X RPS → X RPS

### Próximos bottlenecks
1. [siguiente problema a atacar]
```

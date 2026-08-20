# Observabilidad — Instrumentación + Kafka Analytics

Métricas custom (OpenTelemetry/Prometheus), dashboards Grafana y monitoreo de Kafka. Ejemplos ilustrativos sobre FleetVision — adaptar al stack real.

## Contenido

- [Instrumentación — Métricas custom .NET 8 (OpenTelemetry)](#instrumentación--métricas-custom-net-8-opentelemetry)
- [Grafana Dashboard JSON structure](#grafana-dashboard-json-structure)
- [Kafka Analytics — Monitoreo de consumer lag](#kafka-analytics--monitoreo-de-consumer-lag)
- [PromQL para Kafka](#promql-para-kafka)

## Instrumentación — Métricas custom .NET 8 (OpenTelemetry)

```csharp
// En cada servicio: registrar métricas de negocio
public class TelemetryMetrics
{
    private readonly Counter<long> _positionsIngested;
    private readonly Histogram<double> _ingestLatency;
    private readonly ObservableGauge<int> _activeVehicles;

    public TelemetryMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("FleetVision.Telemetry");
        _positionsIngested = meter.CreateCounter<long>(
            "fleet.positions.ingested.total",
            description: "Total GPS positions ingested");
        _ingestLatency = meter.CreateHistogram<double>(
            "fleet.ingest.duration.ms",
            unit: "ms",
            description: "Time to process a position from gRPC to Kafka");
        _activeVehicles = meter.CreateObservableGauge<int>(
            "fleet.vehicles.active",
            () => GetActiveVehicleCount());
    }
}
```

## Grafana Dashboard JSON structure

```json
{
  "panels": [
    {
      "title": "GPS Positions/sec",
      "type": "timeseries",
      "targets": [{
        "expr": "rate(fleet_positions_ingested_total[5m])",
        "legendFormat": "{{service}}"
      }]
    },
    {
      "title": "Ingest P95 Latency",
      "type": "stat",
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(fleet_ingest_duration_ms_bucket[5m]))"
      }]
    },
    {
      "title": "Consumer Lag por Topic",
      "type": "timeseries",
      "targets": [{
        "expr": "kafka_consumer_group_lag{group=~\".*-service\"}",
        "legendFormat": "{{group}} - {{topic}}"
      }]
    }
  ]
}
```

## Kafka Analytics — Monitoreo de consumer lag

```bash
# Ver lag de todos los grupos
kafka-consumer-groups --bootstrap-server localhost:9092 --list | \
  xargs -I{} kafka-consumer-groups --bootstrap-server localhost:9092 \
    --describe --group {} 2>/dev/null

# Ver si el DLQ tiene mensajes (señal de errores)
kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic telemetry.raw.dlq
```

## PromQL para Kafka

```promql
# Lag total de todos los consumers
sum(kafka_consumer_group_lag) by (group)

# Topics con mayor throughput
topk(5, rate(kafka_topic_messages_in_total[5m]))

# Alertas: lag > 1000 mensajes por > 5 minutos
ALERT KafkaConsumerLagHigh
  IF kafka_consumer_group_lag > 1000
  FOR 5m
  LABELS { severity = "warning" }
  ANNOTATIONS { summary = "Consumer {{ $labels.group }} lag: {{ $value }}" }
```

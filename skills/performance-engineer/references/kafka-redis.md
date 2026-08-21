# Kafka & Redis Performance

Leer cuando haya que diagnosticar consumer lag / throughput de Kafka (Telemetria), tunear producer/consumer, o analizar memoria, hot keys y estrategia de caché/TTL en Redis.

## Kafka Performance (Telemetria)

```bash
# Consumer lag — métrica crítica de salud
docker exec fv-kafka-1 kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group geofencing-service

# Throughput de un topic
docker exec fv-kafka-1 kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe --topic telemetry.raw
```

**Parámetros de tuning por escenario:**

| Parámetro | Throughput alto | Latencia baja |
|-----------|----------------|---------------|
| `linger.ms` (producer) | 50-100ms | 0-5ms |
| `batch.size` | 65536 (64KB) | 16384 (16KB) |
| `fetch.min.bytes` (consumer) | 65536 | 1 |
| `max.poll.records` | 500 | 50 |

**Red flags:**
- Consumer lag creciendo → consumidor más lento que productor → scale out consumers o optimizar handler
- `enable.auto.commit=true` → posible doble procesamiento → usar commit manual

## Redis Performance

```bash
# Análisis de memoria y hot keys
redis-cli -a $REDIS_PASSWORD --bigkeys      # Keys más grandes
redis-cli -a $REDIS_PASSWORD --hotkeys      # Keys más accedidas
redis-cli -a $REDIS_PASSWORD info memory    # Uso de memoria
redis-cli -a $REDIS_PASSWORD info stats     # Hit rate

# Latencia
redis-cli -a $REDIS_PASSWORD --latency-history
```

**TTL strategy — ejemplo:**
```
Cache-aside pattern (read-through):
  1. GET de Redis
  2. Si miss → query DB → SET en Redis con TTL
  3. En write → DEL la key (no actualizar)

TTLs recomendados:
  - Sesiones JWT: mismo TTL que el token (15min-1h)
  - Datos de flota (vehicles list): 30s (datos cambian frecuente)
  - Perfil de tenant: 5min
  - Datos de odómetro: 48h (deduplication key)
```

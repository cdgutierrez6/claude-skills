# Optimización PostgreSQL / TimescaleDB

Leer cuando haya que optimizar queries, leer un `EXPLAIN`, diagnosticar índices faltantes, o tunear hypertables de TimescaleDB (FleetVision).

## Contenido
- Diagnóstico inicial (queries lentas, índices no usados, seq scans, tamaños)
- EXPLAIN ANALYZE — cómo leerlo + red flags
- TimescaleDB específico (FleetVision): compresión, continuous aggregates, retention, chunks

## Diagnóstico inicial

```sql
-- Queries más lentas (requiere pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time, rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Índices no usados (candidatos a eliminar)
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE '%pkey%';

-- Tablas con muchos sequential scans (candidatos a indexar)
SELECT schemaname, tablename, seq_scan, idx_scan,
       seq_scan - idx_scan AS too_much_seq
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
ORDER BY too_much_seq DESC;

-- Tamaño de tablas e índices
SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## EXPLAIN ANALYZE — cómo leerlo

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT v.id, v.plate, COUNT(t.id) as telemetry_count
FROM vehicles v
JOIN vehicle_positions t ON t.vehicle_id = v.id
WHERE t.recorded_at > NOW() - INTERVAL '1 hour'
  AND v.tenant_id = $1
GROUP BY v.id, v.plate;
```

**Red flags en EXPLAIN:**
- `Seq Scan` en tabla > 10k rows → falta índice
- `Nested Loop` con miles de iteraciones → N+1, usar JOIN o IN
- `Hash Join` con alto `rows` estimado vs real → estadísticas desactualizadas → `ANALYZE`
- `Sort` sin índice → agregar índice en columna de ORDER BY
- `Buffers: shared hit=0 read=...` → datos no en caché → tabla muy grande o índice faltante

## TimescaleDB específico (FleetVision)

```sql
-- Verificar compresión de chunks
SELECT chunk_name, before_compression_total_bytes, after_compression_total_bytes,
       compression_ratio
FROM chunk_compression_stats('vehicle_positions')
ORDER BY chunk_name;

-- Continuous Aggregate para dashboards (evitar full scan)
CREATE MATERIALIZED VIEW vehicle_positions_hourly
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', recorded_at) AS bucket,
       vehicle_id, tenant_id,
       AVG(speed) as avg_speed, MAX(speed) as max_speed,
       COUNT(*) as position_count
FROM vehicle_positions
GROUP BY bucket, vehicle_id, tenant_id;

-- Política de refresh automático
SELECT add_continuous_aggregate_policy('vehicle_positions_hourly',
  start_offset => INTERVAL '3 hours',
  end_offset   => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');

-- Retention policy (borrar datos >90 días)
SELECT add_retention_policy('vehicle_positions', INTERVAL '90 days');

-- Verificar chunk sizes (óptimo: 150MB-500MB por chunk)
SELECT hypertable_name, chunk_schema, chunk_name,
       pg_size_pretty(total_bytes) as size
FROM chunks_detailed_size('vehicle_positions')
ORDER BY total_bytes DESC LIMIT 10;
```

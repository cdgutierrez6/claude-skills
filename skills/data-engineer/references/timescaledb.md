# TimescaleDB — Patrones para FleetVision

Hypertables, continuous aggregates, retención y compresión para telemetría IoT. Ejemplos ilustrativos sobre FleetVision — adaptar al schema real.

## Contenido

- [Continuous Aggregates — Arquitectura en capas](#continuous-aggregates--arquitectura-en-capas)
- [Queries de dashboard optimizadas](#queries-de-dashboard-optimizadas)
- [Gestión de chunks y retención](#gestión-de-chunks-y-retención)

## Continuous Aggregates — Arquitectura en capas

```sql
-- Capa 1: Minutal (datos crudos → agregados por minuto)
CREATE MATERIALIZED VIEW vehicle_stats_1min
WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
SELECT
  time_bucket('1 minute', recorded_at) AS bucket,
  vehicle_id, tenant_id,
  AVG(speed)        AS avg_speed,
  MAX(speed)        AS max_speed,
  AVG(fuel_level)   AS avg_fuel,
  COUNT(*)          AS sample_count,
  ST_MakeLine(geom ORDER BY recorded_at) AS path  -- Trayectoria del minuto
FROM vehicle_positions
GROUP BY 1, vehicle_id, tenant_id;

-- Política de refresh (mantener últimas 3h en tiempo real)
SELECT add_continuous_aggregate_policy('vehicle_stats_1min',
  start_offset    => INTERVAL '3 hours',
  end_offset      => INTERVAL '1 minute',
  schedule_interval => INTERVAL '1 minute');

-- Capa 2: Horaria (sobre el minutal — más eficiente)
CREATE MATERIALIZED VIEW vehicle_stats_1h
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', bucket) AS bucket,
  vehicle_id, tenant_id,
  AVG(avg_speed)  AS avg_speed,
  MAX(max_speed)  AS max_speed,
  MIN(avg_fuel)   AS min_fuel,
  SUM(sample_count) AS total_samples
FROM vehicle_stats_1min
GROUP BY 1, vehicle_id, tenant_id;

-- Capa 3: Diaria (sobre horaria)
CREATE MATERIALIZED VIEW vehicle_stats_daily
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 day', bucket) AS day,
  vehicle_id, tenant_id,
  AVG(avg_speed)    AS daily_avg_speed,
  MAX(max_speed)    AS daily_max_speed,
  MIN(min_fuel)     AS daily_min_fuel,
  SUM(total_samples) AS total_samples
FROM vehicle_stats_1h
GROUP BY 1, vehicle_id, tenant_id;
```

## Queries de dashboard optimizadas

```sql
-- Dashboard de flota: últimas 24h por tenant (usa continuous aggregate)
SELECT
  v.plate,
  vs.avg_speed,
  vs.max_speed,
  vs.daily_min_fuel,
  vs.total_samples AS gps_points
FROM vehicle_stats_daily vs
JOIN vehicles v ON v.id = vs.vehicle_id
WHERE vs.day = CURRENT_DATE
  AND vs.tenant_id = $1
ORDER BY vs.avg_speed DESC;

-- Gap filling: posiciones cada 5 min aunque no haya datos
SELECT
  time_bucket_gapfill('5 minutes', recorded_at, NOW() - INTERVAL '1 hour', NOW()) AS bucket,
  vehicle_id,
  LOCF(AVG(speed)) AS speed  -- Last Observation Carried Forward
FROM vehicle_positions
WHERE vehicle_id = $1
  AND recorded_at > NOW() - INTERVAL '1 hour'
GROUP BY 1, vehicle_id;
```

## Gestión de chunks y retención

```sql
-- Ver tamaño de chunks (identificar anomalías)
SELECT chunk_name,
       range_start, range_end,
       pg_size_pretty(total_bytes) AS size,
       is_compressed
FROM timescaledb_information.chunks
WHERE hypertable_name = 'vehicle_positions'
ORDER BY range_start DESC
LIMIT 20;

-- Política de compresión (comprimir chunks > 7 días)
ALTER TABLE vehicle_positions SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'vehicle_id, tenant_id',
  timescaledb.compress_orderby = 'recorded_at DESC'
);
SELECT add_compression_policy('vehicle_positions', INTERVAL '7 days');

-- Retención diferenciada por tenant (premium vs basic)
-- Implementar con función custom + pg_cron
```

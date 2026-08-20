# Data Quality Checklist

Aplicar en cualquier pipeline de datos nuevo. Cada dimensión con su query de verificación:

- [ ] **Completitud**: ¿Hay NULLs inesperados? `SELECT COUNT(*) FILTER (WHERE col IS NULL) FROM table`
- [ ] **Unicidad**: ¿Hay duplicados en campos que deben ser únicos? `SELECT id, COUNT(*) FROM t GROUP BY id HAVING COUNT(*) > 1`
- [ ] **Rango válido**: ¿Velocidad negativa? ¿Fechas futuras? → Constraints o triggers
- [ ] **Referencial**: ¿FKs sin padre? `SELECT * FROM child LEFT JOIN parent USING (id) WHERE parent.id IS NULL`
- [ ] **Volumen**: ¿El ingreso de datos cayó vs ayer? Alertar si `COUNT(*) < yesterday_count * 0.8`
- [ ] **Freshness**: ¿El dato más reciente es reciente? `SELECT MAX(recorded_at) FROM vehicle_positions` debe ser < 5min
- [ ] **Lineage**: Documentar de dónde vienen los datos y qué transformaciones se aplican

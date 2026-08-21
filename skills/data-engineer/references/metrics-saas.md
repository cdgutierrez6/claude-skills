# Métricas SaaS — KPIs

Fórmulas de negocio y queries de health. Ejemplos ilustrativos sobre un CRM B2B — adaptar al schema real.

## Fórmulas de negocio

```
MRR = Σ(monthly_amount por suscripción activa)
ARR = MRR × 12
Churn Rate = clientes_perdidos_mes / clientes_inicio_mes × 100
Net Revenue Retention = (MRR_fin + expansión - contracción - churn) / MRR_inicio × 100
CAC = total_spend_ventas_marketing / new_customers_adquiridos
LTV = ARPU / churn_rate_mensual
LTV:CAC ratio (saludable > 3:1)
Payback Period = CAC / ARPU_mensual
```

## Queries de SaaS health

```sql
-- Health Score por tenant (compuesto)
SELECT
  t.name AS tenant,
  CASE
    WHEN last_login > NOW() - INTERVAL '7 days'  THEN 4 ELSE 0
  END +
  CASE
    WHEN active_users > 5 THEN 3
    WHEN active_users > 2 THEN 1 ELSE 0
  END +
  CASE
    WHEN features_used > 5 THEN 3 ELSE features_used / 2
  END AS health_score,
  subscription_tier, created_at
FROM tenants t
JOIN tenant_usage u USING (id)
ORDER BY health_score ASC;  -- Primero los que van a churnar
```

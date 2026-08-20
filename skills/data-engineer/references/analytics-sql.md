# Analytics SQL Avanzado

Window functions, CTEs, materialized views y patrones OLAP. Ejemplos ilustrativos sobre EfiziAI CRM — adaptar al schema real del proyecto.

## Patrones Window Functions para SaaS (EfiziAI)

```sql
-- MRR por mes con tendencia
WITH monthly_mrr AS (
  SELECT
    date_trunc('month', subscription_start) AS month,
    SUM(monthly_amount) AS mrr,
    COUNT(DISTINCT tenant_id) AS paying_customers
  FROM subscriptions
  WHERE status = 'active'
  GROUP BY 1
)
SELECT
  month,
  mrr,
  paying_customers,
  LAG(mrr) OVER (ORDER BY month) AS prev_mrr,
  ROUND((mrr - LAG(mrr) OVER (ORDER BY month)) / NULLIF(LAG(mrr) OVER (ORDER BY month), 0) * 100, 2) AS mrr_growth_pct,
  SUM(mrr) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative_mrr
FROM monthly_mrr
ORDER BY month;

-- Churn rate mensual
WITH cohort AS (
  SELECT tenant_id, date_trunc('month', created_at) AS cohort_month
  FROM tenants WHERE status = 'active'
),
churned AS (
  SELECT tenant_id, date_trunc('month', cancelled_at) AS churn_month
  FROM subscriptions WHERE cancelled_at IS NOT NULL
)
SELECT
  c.cohort_month,
  COUNT(DISTINCT c.tenant_id) AS cohort_size,
  COUNT(DISTINCT ch.tenant_id) AS churned,
  ROUND(COUNT(DISTINCT ch.tenant_id)::numeric / COUNT(DISTINCT c.tenant_id) * 100, 2) AS churn_rate_pct
FROM cohort c
LEFT JOIN churned ch ON c.tenant_id = ch.tenant_id
  AND ch.churn_month = c.cohort_month + INTERVAL '1 month'
GROUP BY 1
ORDER BY 1;

-- Lead conversion funnel (EfiziAI CRM)
SELECT
  stage,
  COUNT(*) AS count,
  ROUND(COUNT(*)::numeric / FIRST_VALUE(COUNT(*)) OVER (ORDER BY stage_order) * 100, 1) AS conversion_pct
FROM (
  SELECT 'prospect' AS stage, 1 AS stage_order FROM leads WHERE status = 'prospect'
  UNION ALL
  SELECT 'qualified', 2 FROM leads WHERE status = 'qualified'
  UNION ALL
  SELECT 'proposal', 3 FROM leads WHERE status = 'proposal'
  UNION ALL
  SELECT 'closed_won', 4 FROM leads WHERE status = 'closed_won'
) funnel
GROUP BY stage, stage_order
ORDER BY stage_order;
```

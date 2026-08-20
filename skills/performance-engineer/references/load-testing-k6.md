# Load Testing con k6

Leer cuando haya que crear un load/stress/soak/spike test, definir SLOs de latencia, o elegir el tipo de prueba.

## Script básico profesional

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration', true);

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp-up
    { duration: '5m', target: 50 },   // Steady state
    { duration: '2m', target: 100 },  // Spike
    { duration: '5m', target: 100 },  // Steady at peak
    { duration: '2m', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<2000'],  // SLOs
    errors: ['rate<0.01'],                             // < 1% errors
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/vehicles`, {
    headers: { Authorization: `Bearer ${__ENV.TOKEN}` },
  });

  const success = check(res, {
    'status 200': (r) => r.status === 200,
    'duration < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);
  apiDuration.add(res.timings.duration);
  sleep(1);
}
```

## Tipos de prueba y cuándo usar cada una

| Tipo | Comando | Cuándo |
|------|---------|--------|
| Smoke | `--vus 5 --duration 1m` | Validar que el test funciona |
| Load | stages normales | Carga esperada del sistema |
| Stress | Aumentar VUs hasta romper | Encontrar límite del sistema |
| Soak | Alta carga por 8h+ | Detectar memory leaks / degradación |
| Spike | 0→500 VUs en 10s | Simular picos de tráfico súbitos |

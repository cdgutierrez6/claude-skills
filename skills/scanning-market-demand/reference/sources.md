# Fuentes y frases-señal — scanning-market-demand

Solo búsqueda web abierta y APIs públicas. No saltar logins ni muros de pago.

## DEMANDA DE SERVICIO (caja inmediata, cobro único)
- **Workana** — workana.com — proyectos freelance LATAM (la más relevante para Colombia).
- **Freelancer** — freelancer.com — proyectos globales.
- **Upwork** — upwork.com — proyectos globales (leer solo lo público).
- **Grupos de Facebook** de freelance / desarrollo LATAM — buscar vía resultados públicos.
- **LinkedIn** — posts públicos tipo "busco desarrollador", "necesito que me hagan", "se necesita programador".

### Queries servicio
- `Workana proyecto desarrollador [nicho] presupuesto`
- `"busco desarrollador" OR "necesito una app" site:linkedin.com/posts`
- `freelance Colombia "se necesita" automatización OR app OR web`

## DEMANDA DE PRODUCTO (dolor repetido → SaaS)

> ⚠️ **Reddit no es accesible vía la herramienta WebSearch/WebFetch** (el crawler lo bloquea con error 400). No lo uses como fuente primaria desde este pipeline. Si quieres señales de Reddit, hay que llegar por otra vía (lectura manual del navegador, API oficial de Reddit con credenciales). Prioriza las fuentes indexables de abajo.

Fuentes primarias (indexables y con prueba de pago real):
- **Workana / Freelancer / Upwork** — los *proyectos publicados* son la mejor demanda de producto disponible: dolor real con presupuesto. Un patrón repetido de proyectos parecidos = candidato a productizar (productizar el servicio). En la práctica suele dar mejor señal que Reddit.
- **Product Hunt** — comentarios y "I wish this existed" en lanzamientos del nicho.
- **Foros de nicho** indexables, blogs de software vertical y guías de "errores frecuentes de [industria]" — revelan el dolor recurrente que mueve a un mercado entero (p.ej. facturación electrónica DIAN para pymes CO).
- **Reddit (solo si hay acceso por otra vía):** r/SaaS, r/Entrepreneur, r/webdev, r/smallbusiness, r/nocode.

### Frases-señal producto (buscar literalmente)
- `"wish there was an app for"`
- `"is there a tool that"`
- `"would pay for"` / `"I'd pay for a tool"`
- `"ojalá existiera una app que"` / `"alguien debería crear"`
- `"how do you all handle"` (revela workflows manuales = dolor)
- Combinar con subreddit: `"would pay for" site:reddit.com/r/SaaS`

## Cómo medir frecuencia
- `1` → un solo pedido aislado.
- `varios` → 2-5 pedidos parecidos en distintas fuentes.
- `muchos` → patrón claro y repetido (hilos con upvotes, múltiples posts). Lo más valioso para PRODUCTO.

## Pistas de presupuesto
Busca cifras explícitas ("budget $500", "pago 2M COP", "monthly $20"). Si no hay, marca "no indica" — no lo inventes.

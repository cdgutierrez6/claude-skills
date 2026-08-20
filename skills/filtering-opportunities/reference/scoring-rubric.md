# Rubro de viabilidad — filtering-opportunities

Cada oportunidad se puntúa 0-10 como suma ponderada de 6 dimensiones. Umbral de corte: **6.5**.
El rubro ordena y descarta basura; el **criterio senior** (abajo) decide en los bordes.

| # | Dimensión | Peso | Qué evalúa | 0-3 (bajo) | 4-6 (medio) | 7-10 (alto) |
|---|-----------|------|------------|-----------|-------------|-------------|
| 1 | **Tamaño / dolor del mercado CO-LATAM** | 20% | ¿El problema duele a muchos en Colombia/LATAM? | nicho mínimo o dolor leve | mercado medio | dolor agudo y masivo, mercado claro |
| 2 | **Baja fricción de implementación** | 15% | ¿Se apoya en infra existente (Bre-B, WhatsApp API, pasarelas, LLMs, pgvector)? | requiere infra nueva pesada | parcial | se monta sobre infra existente, MVP rápido |
| 3 | **Claridad de monetización (<6 meses)** | 20% | ¿Hay ruta de ingreso clara y pronta? | sin modelo claro | modelo posible, lento | cobra desde el día 1 / ruta < 6 meses |
| 4 | **Confiabilidad / madurez técnica** | 15% | ¿La tecnología es confiable hoy? | research/inestable | en adopción | madura, casos en producción |
| 5 | **Defensibilidad / timing** | 15% | ¿Hay ventaja (timing regulatorio, datos, red, switching cost) o se copia fácil? | commodity, fácil de copiar | algo de ventaja | timing fuerte (p.ej. Bre-B) o foso real |
| 6 | **Demanda verificada** | 15% | ¿Alguien lo pide? ¿con presupuesto? ¿muchos? ¿parche manual ya existe? | nadie lo pide (latente puro) | pedido aislado | pedido explícito + presupuesto + muchos |

## Cálculo
`score = Σ (puntaje_dimensión × peso)`, resultado en escala 0-10.

Ejemplo: dim1=8 (0.20) + dim2=7 (0.15) + dim3=9 (0.20) + dim4=7 (0.15) + dim5=6 (0.15) + dim6=9 (0.15)
= 1.60 + 1.05 + 1.80 + 1.05 + 0.90 + 1.35 = **7.75** → finalista.

## Las 3 preguntas que matan o salvan (criterio senior, sobre el número)
1. **¿Por qué ahora?** Catalizador de este año (regulación, costo que cayó, comportamiento nuevo). Sin "why now" → degrada al menos un nivel. **Pero el catalizador no basta con estar *anunciado*: la infra/estándares/SDK que necesitas para construir deben existir HOY.** Un decreto sin estándares publicados, o una plataforma "próximamente", es "why-now prematuro" → trátalo como descarte, no como finalista.
2. **¿Ventaja injusta?** Por qué Cristian y no cualquiera: dominio, stack ya montado, acceso a clientes, timing.
3. **¿Distribución?** Canal claro y barato para llegar al cliente (en CO/LATAM casi siempre WhatsApp/comunidades). Sin canal, el producto muere aunque sea bueno.

## Checklist de falsos positivos (descartar aunque el número engañe)
- **Feature, no producto:** resuelve algo que el incumbente añade en una tarde. Sin foso.
- **TAM inflado:** mercado enorme en papel donde nadie paga (educación gratuita, ONG sin presupuesto, "todo el mundo").
- **Mercado que no paga:** usuarios que aman lo gratis y nunca convierten.
- **Me-too sin ventaja:** clon de algo existente sin distribución ni timing distinto.
- **Vitamina disfrazada de analgésico:** suena urgente pero es posponible indefinidamente.
- **Dependencia frágil:** todo el negocio cuelga de una API/plataforma que puede cerrarte la puerta o copiarte.
- **Why-now prematuro:** el catalizador (decreto, anuncio, ronda) existe, pero la infraestructura, estándares o SDK que necesitas para construir **aún no están disponibles** (p.ej. Open Finance obligatorio con estándares de la SFC pendientes 6-12 meses). Construir hoy es adelantarse a la infra → espera o descártala.

## Reglas de desempate y ajustes
- **Demanda explícita con presupuesto (o parche manual ya existente)** es la señal más fuerte de viabilidad real: cuando la dimensión 6 es alta, no descartes por dudas en defensibilidad — alguien ya está dispuesto a pagar.
- Una señal **tech sin demanda** (dim6 baja) rara vez supera 6.5 sola; combínala con una demanda (D) para que valga.
- Penaliza la **madurez emergente** (dim4) si el cliente necesita algo confiable ya; favorécela si la oportunidad es "early mover" y el timing es la ventaja.
- Ante empate de score, gana la de **ruta de monetización más corta** (dim3).

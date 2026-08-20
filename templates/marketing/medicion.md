# Medición — Consultas NUEVAS por WhatsApp (loop humano, sin dashboard)

> Plantilla de la Fase 8. La métrica única de toda la máquina. **No hay dashboard automático**: WhatsApp
> no entrega analítica de origen. Lo único que sobrevive hasta la conversación es el **texto pre-cargado**,
> que actúa de etiqueta de origen (`Ref:`). Contrato: [[reglas-duras]] · Convención de links: [[landing]].

## 1. Definición precisa (que todos midan lo mismo)
Una **consulta nueva** = una conversación de WhatsApp **entrante**, de alguien que **no había escrito
antes**, atribuible a un **canal de origen**. No cuentan: clientes que ya te escribían, reenvíos internos,
ni tu propia prueba. **La métrica NO es ventas ni ingreso** (eso es negociación humana / CRM, fuera de alcance).

## 2. El mecanismo honesto: el codeword en el mensaje pre-cargado
Cada canal usa un `wa.me` con una frase de apertura distinta que **es la etiqueta de origen**:
`https://wa.me/57{NUMERO_WA}?text=<mensaje-url-encoded>`

| Canal | Frase de apertura (la etiqueta) |
|---|---|
| Landing (web) | `Hola, vengo de su página web y quiero...` |
| Instagram (bio) | `Hola, los vi en Instagram y quiero...` |
| Instagram (historia) — `IG-HIST` | `Hola, vi su historia y quiero...` |
| Facebook | `Hola, los encontré en Facebook y quiero...` |
| Google Business | `Hola, los encontré en Google y quiero...` |
| Estados de WhatsApp | `Hola, vi su estado y quiero...` |
| Volante / QR físico | `Hola, escaneé su código y quiero...` |

## 3. Qué generar (entregable)
- Un `wa.me` por **cada canal marcado en el intake D3**, con su frase-etiqueta.
- Tabla de links en `<negocio>/marketing/resultados/links-wa.md` (canal → link → dónde pegarlo).
- **Opcional (si hay dominio):** redirección propia (`minegocio.com/ig` → 302 a `wa.me/...`) para contar
  clics en servidor/n8n. El redirector suma "clics"; el codeword sigue confirmando el origen dentro del chat.

## 4. Qué registrar (el loop humano / n8n)
- **WhatsApp Business (gratis, manual):** una **etiqueta por canal** + etiqueta `Nuevo`. Al abrir cada
  chat entrante nuevo, etiquetarlo según el codeword. Cero código; depende de disciplina.
- **n8n (semi-automático, si hay redirector):** registra `fecha + canal` por clic; la confirmación de
  "conversación nueva" sigue siendo humana (leer el codeword del primer mensaje).

Log mínimo (una fila por consulta nueva):
`fecha | canal (del codeword) | ¿primera vez? sí/no | producto de interés | ¿avanzó a cotización? sí/no | notas`

## 5. Ritual semanal (15 min, p. ej. lunes)
1. Contar **consultas nuevas de la semana por canal**. 2. Identificar el **canal ganador** y el que no jaló.
3. Decidir **dónde reforzar** la publicación (el humano publica). 4. Anotar el total abajo para ver la tendencia.

### Tablero de tendencia (rellenar)
| Semana | WEB | FB | IG | EST | Otro | **Total consultas nuevas** |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## 6. Honestidad — lo que NO se puede medir automático
- **Clics sin conversación:** sin redirector no se saben; con redirector se cuentan clics, no quién no escribió.
- **Texto borrado:** el cliente puede borrar el mensaje pre-cargado → se pierde el codeword. *Mitigación:*
  poner la etiqueta al **inicio** y que suene natural.
- **Multi-touch:** si vio Instagram y luego buscó en Google, se cuenta el **último** canal (el del link que abrió).
- **Etiquetado manual:** depende de disciplina; la atribución real automática exige **WhatsApp Business
  API (Cloud API)** + herramienta — es otro proyecto, no lo cubre esta máquina.
- **La métrica es "consultas", no ventas.** Cerrar es humano; no se instrumenta aquí.

> **Riesgo #1 del sistema (nota del PO):** si el dueño no etiqueta con disciplina (o no acepta el
> redirector), la métrica se degrada a impresión subjetiva. Confirmarlo en el intake (D3) antes de
> prometer "sabrás qué canal funciona". Sin ese compromiso, se entrega landing y copy excelentes, pero el
> "sabrás qué jala" queda a medias — y eso se dice de frente.

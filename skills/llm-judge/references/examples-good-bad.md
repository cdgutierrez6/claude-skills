# Ejemplos Calibrados — LLM Judge

> Ejemplos de outputs buenos vs malos para calibrar el scoring.
> Se actualiza automáticamente cuando score < 3.5 en una evaluación.

---

## ✅ BUENOS OUTPUTS (Score 4.5+)

### Ejemplo 1 — Endpoint Express con manejo correcto
```typescript
// ✅ Por qué es bueno:
// - Input validado con zod antes de tocar DB
// - try/catch explícito en async
// - No expone stack trace al cliente
// - SQL parametrizado (Prisma maneja esto)
// - Respuesta consistente: siempre { data, error }

export const createLead = async (req: Request, res: Response) => {
  try {
    const parsed = createLeadSchema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ data: null, error: parsed.error.flatten() });
    }
    
    const lead = await prisma.lead.create({ data: parsed.data });
    return res.status(201).json({ data: lead, error: null });
  } catch (err) {
    logger.error('createLead failed', { err, body: req.body });
    return res.status(500).json({ data: null, error: 'Internal server error' });
  }
};
```

---

## ❌ MALOS OUTPUTS (Score < 3.5)

### Ejemplo 1 — Async sin manejo de errores
```typescript
// ❌ Por qué es malo:
// - Sin try/catch → crash no manejado si DB falla
// - Sin validación de input → SQL injection potencial si no usa ORM
// - Expone err directamente al cliente (información sensible)
// - Sin logging → imposible debuggear en producción

export const createLead = async (req, res) => {
  const lead = await db.query(`INSERT INTO leads VALUES (${req.body.name})`);
  res.json(lead);
};
```

---

## ⚠️ OUTPUTS AMBIGUOS (Score 3.0-3.5)

### Ejemplo 1 — Funciona pero frágil
```typescript
// ⚠️ Por qué es ambiguo:
// - Correcto en happy path
// - Error handling presente pero genérico
// - Falta validación de tipos específicos
// - Funcional para MVP, pero no para producción con carga

export const createLead = async (req: Request, res: Response) => {
  try {
    if (!req.body.name || !req.body.email) {
      return res.status(400).json({ error: 'Missing fields' });
    }
    const lead = await prisma.lead.create({ data: req.body });
    return res.status(201).json(lead);
  } catch (err) {
    return res.status(500).json({ error: 'Error' });
  }
};
// ⚠️ Problemas: req.body no validado completamente, 
//    error 500 sin logging, response inconsistente (a veces lead, a veces {error})
```

---

<!-- Los ejemplos se agregan automáticamente cuando score < 3.5 -->

---

## ❌ MALO — Prompt image-input que "protege" el logo pero lo pierde (2026-07-23, score 3.2)

```
BRAND LOGO — mandatory: mounted on the wall, in the upper third of the frame, is a large sign
showing EXACTLY the logo from the attached reference image. Reproduce it verbatim — silver
metallic wordmark "TALLER-EJEMPLO & MAS", the thin red rule, the big chrome "S&M" monogram...
Do not redraw, re-letter, translate, restyle, crop, mirror or recolor it.
```
❌ Por qué es malo, pese a sonar blindado:
- **"upper third" en un 9:16 social = debajo del header de WhatsApp Status / Reels.** El logo existe
  en el render y es invisible en el feed. El requisito del cliente se cumple en el archivo y falla en
  la pantalla.
- **No declara qué es la imagen adjunta.** El modelo puede tomar el fondo negro texturizado del PNG
  como caja alrededor del logo, o como referencia de estilo de toda la escena.
- **Describe el logo en prosa** al lado de la orden de preservarlo → invita a regenerarlo desde texto
  en vez de copiar píxeles. La descripción debe marcarse "for verification only".
- **No fija un piso de tamaño.** "Large" es interpretable; a menos del ~45% del ancho el wordmark y
  "IND. COLOMBIANA" caen por debajo del umbral donde el modelo los resuelve.

## ✅ BUENO — el mismo bloque corregido
```
LOGO — MANDATORY, USE THE ATTACHED IMAGE: the attached image is a brand logo asset, not a scene
reference. Use ONLY the logo artwork; ignore its background, framing and composition. Copy it
pixel-for-pixel. Do NOT redraw / re-letter / re-typeset / translate / restyle / recolor / crop /
mirror / stretch it. [lista de los 5 elementos] — this description is for VERIFICATION ONLY, it
is not a licence to regenerate the logo from text. Cut it out cleanly: no black box, no leftover
background from the source file.
PLACEMENT: vertical band between 20% and 40% of frame height.
FRAME SAFETY (9:16 social): top 15% and bottom 18% stay clear — platform UI sits there.
GEOMETRY: frontal, flat, zero perspective/keystone/tilt/curvature/motion blur. Minimum 45% of
frame width. Nothing overlapping or shadowing it.
```

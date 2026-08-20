# Contexto del negocio — Brief (esquema de intake)

> **Qué es esto:** el ÚNICO input variable de la máquina de marketing. Cada negocio llena su copia en
> `<negocio>/marketing/contexto/contexto.md`. Todo lo demás (estrategia, copy, landing, kit, medición)
> es función de este archivo + las [[reglas-duras]] + los playbooks. La máquina lo llena
> **entrevistándote**; si prefieres, lo llenas a mano aquí.
>
> **Marcas:** `[OBL]` = obligatoria (sin ella no se construye bien) · `[OPC]` = opcional (mejora el
> resultado). Si una `[OBL]` falta, la máquina **no construye a ciegas**: la vuelve a pedir o deja el
> hueco como `TODO` visible. **Nunca inventa** número, prueba social ni datos legales.

---

## Bloque A — Negocio y oferta
- **A1 [OBL]** Nombre exacto del negocio (como debe aparecer): → `{NEGOCIO}` = 
- **A2 [OBL]** En una frase, ¿qué vendes o haces? (producto/servicio principal): 
- **A3 [OBL]** ¿Cuál es el **resultado/transformación** que se lleva el cliente? (el "para qué", no el "qué"): → `{BENEFICIO}` = 
- **A4 [OBL]** 3–5 productos/servicios a impulsar (mejor margen o más pedidos): → `{SERVICIOS}` / `{PRODUCTOS}` = 
- **A5 [OBL]** ¿Dónde operas? Local (ciudad/barrio), regional, nacional o virtual. ¿Local físico con dirección pública?: → `{CIUDAD}` / `{ZONA}` / `{DIRECCION}` = 
- **A6 [OPC]** ¿Temporada o momento clave del año?: 
- **A7 [OPC]** ¿Algo que baje la fricción de la primera consulta (diagnóstico, revisión, asesoría) **sin comprometer precio ni plazo**?: 

## Bloque B — Cliente ideal y objeciones
- **B1 [OBL]** ¿Quién es tu **mejor** cliente? (persona/empresa, edad aprox., ocupación, qué lo mueve): 
- **B2 [OBL]** ¿Con qué problema/necesidad llega normalmente?: 
- **B3 [OBL]** Las **3 dudas o miedos** que hacen que NO te escriban (→ FAQ + JSON-LD FAQPage): 
- **B4 [OPC]** ¿Qué **palabras usan** tus clientes para pedir lo que vendes? (cómo lo googlean): 
- **B5 [OPC]** ¿Con qué **tipo** de competidor te comparan? (categoría, **no nombres** — no identificamos terceros): 
- **B6 [OPC]** ¿Tratas al cliente de **tú** o de **usted**? (por defecto **usted**, LATAM): → `{VOZ}` = 

## Bloque C — Diferenciador y prueba social
- **C1 [OBL]** ¿Por qué te eligen a ti? **1–3 razones concretas y verificables** (no "somos los mejores"): → `{DIFERENCIAL}` = 
- **C2 [OBL]** Prueba social **REAL y con permiso** (marca lo que aplique): reseñas Google · testimonios (con consentimiento) · nº clientes/trabajos · años de experiencia · garantía propia · certificaciones · marcas/repuestos que manejas: → `{PRUEBA}` = 
- **C3 [OPC]** ¿2–3 casos/fotos de trabajos reales (antes/después)? ¿Con permiso de quien aparezca?: 
- **C4 [OPC]** ¿Garantía/respaldo que dé confianza (**sin mencionar precio ni plazo**)?: 

## Bloque D — Canales y WhatsApp
- **D1 [OBL]** **Número de WhatsApp** que recibe consultas — **10 dígitos SIN el 57** (la plantilla lo antepone). ¿Business o normal?: → `{NUMERO_WA}` = 
- **D2 [OBL]** ¿**Quién responde** y en qué **horario de atención**? (hecho, no promesa de velocidad): → `{HORARIO}` = 
- **D3 [OBL]** ¿Desde qué **canales** compartirás el link? (landing · Instagram · Facebook · TikTok · Google Business · Estados WhatsApp · volante/QR · tarjeta): → define un `wa.me` distinto por canal (base de la métrica). 
- **D4 [OPC]** ¿Un **saludo** que quieras que el cliente traiga ya escrito al abrir el chat?: 
- **D5 [OPC]** Perfiles a enlazar (Instagram/Facebook/Google Business): → `{REDES}` = 

## Bloque E — Activos visuales disponibles
- **E1 [OBL]** ¿Tienes **logo**? Formato (PNG/SVG/vector). Si no, ¿wordmark?: 
- **E2 [OBL]** ¿**Fotos propias** de producto/trabajo/local/equipo, buena calidad, con permiso?: (si no hay → se marca faltante o imagen IA marca-segura, nunca fotos de terceros). 
- **E3 [OPC]** ¿Colores/identidad ya definidos, o los proponemos?: 
- **E4 [OPC]** ¿**Video** (local/producto/proceso)? ¿Con audio? (posible hero cinematográfico): 
- **E5 [OPC]** ¿Material que **NO** quieras usar?: 

## Bloque F — Restricciones, legales y excepciones a reglas duras
- **F1 [OBL]** ¿Tu sector exige **avisos legales / reglas de publicidad** (salud, financiero, legal, alimentos…)?: 
- **F2 [OBL]** ¿Algo que **NO puedas/quieras afirmar** (garantías, "el mejor", resultados prometidos)?: 
- **F3 [OBL]** **Confirmación de reglas duras:** la landing NO llevará **precios** ni **plazos**, el CTA será **WhatsApp**, y **tú publicas**. ¿De acuerdo? ¿O hay **obligación legal** que fuerce mostrar algún dato? → única vía para tocar una regla dura: **solo por mandato legal, citando la norma**; el juez la **escala a humano** y nunca la auto-aprueba. Contrato: [[reglas-duras]]. 
- **F4 [OPC]** Datos legales del footer: razón social, NIT, ciudad, política de datos (Ley 1581 / habeas data): 
- **F5 [OPC]** Dominio/subdominio de publicación (canonical, OG, SEO): 

---

### Gate de arranque (Definition of Ready)
La máquina **no pasa de la entrevista a construir** hasta tener todas las `[OBL]`. Faltantes = se piden
o quedan como `TODO` visible en los Resultados. Ver el flujo completo en [[maquina-marketing]].

> Excepción a una regla dura (F3): solo por obligación legal, se registra aquí firmada por el dueño —
> nunca se asume por defecto. Contrato de reglas: [[reglas-duras]].

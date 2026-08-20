# Patrones Aprendidos — LLM Judge

> Este archivo se actualiza automáticamente después de cada evaluación.
> Es la MEMORIA ACUMULATIVA del sistema de calidad.
> Cuando un patrón aparece 3+ veces → proponer nueva regla en CLAUDE.md

Última actualización: 2026-07-31
Total evaluaciones realizadas: 5
Total puntos ciegos encontrados: 25

---

## Instrucciones para el Judge

Al finalizar cada evaluación, AGREGAR una entrada aquí si:
- Se encontró un punto ciego no trivial
- El pipeline anterior dijo APROBADO pero el judge encontró problemas
- Hay un patrón que podría repetirse en el futuro

**NO agregar** entradas para observaciones obvias o muy específicas al caso.

---

## Registro de Patrones

<!-- Las entradas se agregan aquí automáticamente en formato:

## [FECHA] — [TIPO: Backend/Frontend/Arquitectura/DB] — [PROYECTO]
**Punto ciego:** descripción concisa
**Por qué el pipeline lo pasó:** análisis honesto
**Señal de detección:** cómo detectarlo antes en el futuro
**Frecuencia:** 1ª vez | RECURRENTE x2 | RECURRENTE x3+
**Severidad:** crítico | importante | sugerencia

-->

<!-- INICIO DEL REGISTRO — los patrones se agregan debajo de esta línea -->

## 2026-06-25 — Frontend/Landing — EfiziAI Recepcionista IA
**Punto ciego:** La copy del hero y secciones usa "paciente" en todo el sitio, pero el ICP declarado incluye barberías/salones/spas (clientes, no pacientes). Inconsistencia de posicionamiento contra el propio ICP.
**Por qué el pipeline lo pasó:** El gate de revisión (tech-lead+seguridad+a11y/SEO+QA, 33 agentes) estaba calibrado a CÓDIGO — paridad i18n, headers, CLS, a11y. Ningún lente evaluaba "¿la copy le habla al ICP correcto?". La calidad de copywriting/posicionamiento cae fuera de un review técnico.
**Señal de detección:** Cuando un rediseño define un ICP multi-vertical, verificar que el sustantivo central de la copy (paciente/cliente/usuario) sea inclusivo de TODAS las verticales listadas. Añadir un lente de "copy vs ICP" al gate de landings.
**Otros puntos ciegos del mismo caso:** CTA "ver la llamada en vivo" → transcript estático (over-promise); fricción de formulario (9 campos en lead frío); cero prueba social tras quitar testimonios.
**Frecuencia:** 1ª vez
**Severidad:** importante

## 2026-07-23 — Prompts generativos (Veo 3 / Nano Banana) — Taller Ejemplo & Más
**Punto ciego 1 (CRÍTICO, safe area):** 12 de 16 piezas colocan el logo "in the upper third" de un 9:16
destinado a WhatsApp Status / Reels. Ese es exactamente el lugar donde la plataforma dibuja su header
(avatar, nombre, barra de progreso). El único requisito duro del cliente — "el logo SIEMPRE visible" —
quedaba tapado por la UI en el 75% del paquete.
**Punto ciego 2 (CRÍTICO, image-input):** ningún prompt le dice al modelo QUÉ ES la imagen adjunta. Con
image-input, un logo sobre fondo negro texturizado se arrastra como caja negra alrededor del logo, o peor,
el modelo toma ese fondo como referencia de estilo/composición de la escena. Falta la línea "the attached
image is a brand logo asset, not a scene reference — ignore its background and framing".
**Punto ciego 3 (auto-sabotaje):** los prompts describen el logo en prosa detallada ("silver metallic
wordmark...") junto a la orden de preservarlo. La descripción invita al modelo a REGENERAR el logo desde
texto en vez de copiar píxeles. Hay que marcar explícitamente la descripción como "for verification only,
not a licence to regenerate".
**Punto ciego 4 (variedad):** 4 de 16 piezas usaban la misma integración (panel plano colgado en la pared)
y 6 pares eran casi la misma idea en video y foto. Además, la integración que el propio cliente pidió
("reflejado sobre el cromo espejado") no se usó en ninguna de las 16.
**Por qué el pipeline lo pasó por alto:** el gate estaba calibrado a la CALIDAD DEL PROMPT (composición,
luz, claims, honestidad) y no al MEDIO DE DESTINO (UI de la plataforma) ni al MECANISMO DEL MODELO
(cómo trata un image-input con fondo). Igual que el caso EfiziAI: se auditó el artefacto, no su contexto
de consumo.
**Señal de detección futura:** ante cualquier paquete de creatividades para redes verticales — (a) dibujar
mentalmente la UI de la plataforma encima antes de aprobar la composición; (b) si hay image-input,
preguntar siempre "¿qué hace el modelo con el fondo/encuadre de la referencia?"; (c) inventariar las
integraciones en tabla y contar repeticiones, no confiar en que "se sienten distintas".
**Frecuencia:** 1ª vez (pero comparte raíz con EfiziAI: RECURRENTE x2 en "el gate audita el artefacto,
no su contexto de consumo real")
**Severidad:** crítico

## 2026-07-23 — Diseño de pieza social (grilla de catálogo 9:16) — Taller Ejemplo & Más
**Punto ciego 1 (CRÍTICO, mecanismo roto):** estrategia y diseño se contradicen en la NUMERACIÓN —
po-senior propuso números locales 1–6 por pieza; ux-senior exigió numeración global 01–78. Con 1–6
repetido en 8 piezas, "quiero el 5" es ambiguo entre 8 productos distintos: la pieza cuyo objetivo era
eliminar turnos de chat los multiplica. Ninguno de los dos simuló el mensaje entrante.
**Punto ciego 2 (CRÍTICO, negocio):** nadie modeló el TECHO DE AUDIENCIA del canal. Los Estados de
WhatsApp solo los ven los contactos que ya tienen el número guardado. Toda la serie se diseñó para un
canal cuyo alcance es la libreta de contactos existente; ninguna de las dos piezas propone la acción
de ampliarla.
**Punto ciego 3 (contradicción interna del diseño):** ux-senior especificó a la vez `cover` para la
foto y "producto al 82% del ancho". Son incompatibles: un cover de 466×156 sobre una foto 4:3 recorta
~70% de la altura y decapita el producto si no está centrado en el original. Colocación manual, no
cover automático.
**Punto ciego 4 (unidad de la celda):** ux numeró por SKU ("AVEO CORTO" / "AVEO LARGO"); po por MODELO.
Gana MODELO por una razón que ninguno dio: el dueño del carro NO SABE si el suyo lleva el corto o el
largo — pedirle esa decisión en la pieza produce parálisis o pedido equivocado y devolución.
**Punto ciego 5 (cobertura):** el plan de 9 piezas de ux cubre ~33 celdas de 78 SKUs sin decir qué pasa
con el resto. Solo cierra si se agrupa por modelo (~32 aplicaciones).
**Punto ciego 6 (cifra en pieza):** H1 "78 TALLER-EJEMPLO" es cierto pero envejece, invita a "muéstreme
los 78" y contradice que solo se publican ~32 celdas. Cifra de inventario en creatividad = deuda.
**Punto ciego 7 (marca):** el H1 gigante con la marca del vehículo (CHEVROLET, 112 px) sin descargo de
"aplicación referencial" puede leerse como afiliación. po lo vio para LOGOS, nadie para el TITULAR.
**Punto ciego 8 (operación):** ninguno entregó lo que el dueño necesita el día 1 — hoja maestra
código→producto, respuestas rápidas de WhatsApp Business para código ambiguo/sin código/pregunta de
precio, y la regla "un código nunca se recicla" (el cliente guarda la imagen y escribe 3 semanas después).
**Punto ciego 9 (dato mal calculado):** ux declaró blanco sobre #E51E2A en 4.0:1 y prohibió texto
<32 px sobre rojo. El ratio real es 4.61:1 — pasa AA para texto normal. Restricción de diseño
autoimpuesta sobre una cifra errónea.
**Por qué el pipeline lo pasó por alto:** dos agentes especialistas produjeron artefactos internamente
coherentes y nadie corrió el DIFF entre ambos ni simuló el flujo completo hasta el mensaje entrante.
Cada uno auditó su propia capa (producto / píxeles); el punto de falla vive en la costura entre las dos
y en el turno siguiente (lo que hace el dueño del taller cuando llega el WhatsApp).
**Señal de detección futura:** (a) ante dos reportes de especialistas distintos, construir la tabla de
contradicciones ANTES de sintetizar — nunca asumir que convergen; (b) toda pieza con "call to action"
debe simularse hasta el mensaje entrante y la respuesta humana, no hasta el clic; (c) preguntar siempre
"¿quién ve esto y cuántos son?" antes de optimizar la pieza; (d) recalcular a mano todo ratio de
contraste citado.
**Frecuencia:** RECURRENTE x3 en la raíz "el gate audita el artefacto, no su contexto de consumo real"
(EfiziAI copy-vs-ICP · prompts Veo3 safe-area · esta) → **proponer regla en CLAUDE.md: todo entregable
de cara al cliente se audita simulando el turno SIGUIENTE al entregable (quién lo ve, qué escribe, qué
responde el humano), no solo el entregable.**
**Severidad:** crítico

## 2026-07-23 — Paquete de prompts (grilla catálogo 9:16, Nano Banana) — Taller Ejemplo & Más
**Punto ciego 1 (CRÍTICO, contradicción interna del prompt):** la lista de exclusiones prohíbe
"real car manufacturer wordmarks" mientras el bloque TEXT ordena renderizar el titular
"¿TIENE CHEVROLET?". El modelo recibe dos órdenes opuestas sobre el mismo string y el resultado
es lotería: puede omitir el titular, deformarlo o negarse. Nadie leyó la lista de prohibiciones
CONTRA la lista de strings obligatorios. **Es RECURRENTE x2 del punto ciego 7 de la entrada
anterior (titular con marca del vehículo) — allí fue riesgo de afiliación, aquí es el mismo
string rompiendo el prompt por dentro.**
**Punto ciego 2 (CRÍTICO, empaquetado):** dentro del MISMO bloque de código copiable convivían
(a) instrucciones en español para el humano, (b) el aviso de riesgos y (c) el prompt real, con un
separador que decía "pegue también todo lo que sigue". El usuario que copia el bloque entero le
manda al generador texto meta en español que menciona "PROMPT B" — texto que el modelo puede
intentar dibujar. Un prompt no es autocontenido si comparte contenedor con instrucciones humanas.
**Punto ciego 3 (referencia colgante dentro del prompt):** el PROMPT B decía
"LAYOUT (identical geometry to the text version)". El generador no tiene "la versión con texto".
La geometría sí estaba repetida completa, así que el daño era cosmético, pero la regla se sostiene:
CERO referencias cruzadas dentro de un bloque que se pega solo.
**Punto ciego 4 (honestidad mal calibrada, dos direcciones):** (a) el paquete presenta coordenadas
en píxeles como "hard constraints" cuando un modelo de imagen NO ejecuta layout — las usa como
pista; eso sobrevende precisión; (b) el aviso de riesgo dice "si falla dos veces" como si el éxito
fuera lo normal, cuando la pieza pide 14 strings distintos (5 códigos + 5 modelos + titular +
kicker + 2 líneas de fuga + CTA) y el fallo parcial es el caso esperado, no la excepción.
**Punto ciego 5 (mitigación ausente que valía más que todo el resto):** faltaba la orden
"si no puedes renderizar el string EXACTO, deja el badge VACÍO — nunca aproximes ni inventes".
Un badge vacío se arregla en Canva; un "A8" inventado que parece correcto entra a WhatsApp y
rompe el pedido. Faltaba también un ORDEN DE PRIORIDAD explícito para cuando el modelo no pueda
honrar todo (fotos fieles > zona segura > strings exactos > coordenadas).
**Punto ciego 6 (colisión de códigos en la tabla de familias):** VITARA aparece en la familia A
(Chevrolet) y en la D (Suzuki). El esquema letra+dígito existía justamente para matar la
ambigüedad y la tabla la reintroduce por el nombre del modelo.
**Por qué el pipeline lo pasó por alto:** el borrador se auditó como DOCUMENTO (¿está completo?,
¿es claro para el cliente?) y no como INPUT DE MÁQUINA (¿qué recibe literalmente el modelo si el
usuario hace Ctrl+C sobre el bloque?, ¿hay dos órdenes que se contradicen?). Legibilidad humana y
autocontención para máquina son gates distintos.
**Señal de detección futura:** (a) en todo paquete de prompts, leer la lista de PROHIBICIONES
línea por línea contra la lista de CONTENIDO OBLIGATORIO y marcar intersecciones; (b) un bloque
copiable contiene EXACTAMENTE lo que se pega, nada de instrucciones humanas dentro; (c) contar los
strings que se le piden renderizar al modelo — si son >5, el plan sin texto es el default, no el
plan B; (d) todo prompt de texto-en-imagen lleva la cláusula "ante duda, deja vacío, no inventes".
**Frecuencia:** RECURRENTE x2 (titular con marca) · RECURRENTE x4 en la raíz "el gate audita el
artefacto, no su contexto de consumo real" — aquí el contexto de consumo es el portapapeles.
**Severidad:** crítico

## 2026-07-31 — Skill de rol senior (analytics-measurement-senior, re-juicio) — Máquina de Marketing IA
**Contexto:** re-juicio tras aplicar 5 must-fix (hard-gate consent, G7 anti-Conversion, nota
"cableado propuesto-no-ejecutado", des-duplicación esquema, A/B por conversiones-por-variante).
Los 5 quedaron REALMENTE resueltos y bien escritos. Pero quedan 4 puntos ciegos que la mantienen
por debajo de "élite":
**Punto ciego 1 (IMPORTANTE, Ley 1581 asimétrica):** la skill se vende sobre rigor Habeas Data y
rechaza Consent Mode v2 por transmitir IP pre-consentimiento — pero solo implementa OPT-IN. No hay
flujo de REVOCACIÓN de la autorización (Art. 8 Ley 1581 = derecho explícito a revocar), ni expiry,
ni re-consent si cambia la política. Rigor aplicado pre-consent, relajado post-consent.
**Punto ciego 2 (IMPORTANTE, A/B sin plomería — "no simuló el turno siguiente"):** la conversión
real vive en Capa 2 (codeword en el chat, keyed SOLO por canal `Ref:`). La skill fija "A/B se
gatilla por ~cientos de conversiones POR VARIANTE" pero NUNCA describe cómo se estampa la variante
en el codeword para atribuir una conversión de chat a una variante de landing. Bajo su propio muro
de dos capas + taxonomía `Ref:` congelada (REGLA #6.0), el A/B sobre la métrica real es
arquitectónicamente inalcanzable; el A/B sobre clics optimizaría el número que la propia skill
prohíbe (la parábola canal A/B). Presenta un umbral para algo que no tiene mecanismo.
**Punto ciego 3 (correctitud del reference):** el wrapper usa `window.gtag?.('event',...)` con
optional-chaining (sugiere gtag indefinido) pero en onConsentGranted llama `gtag(...)` pelado. Sin
especificar el stub `dataLayer` síncrono, hay ventana de carga async tras el `granted` donde el
whatsapp_click —el evento que más importa— se DESCARTA en vez de encolarse. No especifica el patrón
stub → riesgo de eventos perdidos.
**Punto ciego 4 (rigor de analista):** el embudo se calcula solo sobre la subpoblación que dio
consent. A consent bajo, "page_view bajo" puede ser problema de tasa-de-consent, no de adquisición.
No monitorea la tasa de consent ni advierte que los ratios del embudo son condicionales al consent.
**Por qué el pipeline lo pasó:** los must-fix se auditaron uno por uno (¿quedó resuelto?) sin correr
el flujo completo del turno siguiente: "traffic sube → corremos A/B → ¿cómo se cuenta la variante
ganadora?" y "usuario ya consintió → ¿cómo lo revoca?". Misma raíz recurrente: se audita el artefacto,
no su contexto de consumo (aquí: el ciclo de vida del consent y el A/B a futuro).
**Señal de detección futura:** (a) toda skill que prometa cumplimiento (Ley 1581/GDPR) se audita por
el ciclo COMPLETO: grant + revoke + expiry, no solo grant; (b) si una skill fija un UMBRAL para una
técnica futura (A/B), exigir que describa la PLOMERÍA de atribución, no solo el gatillo; (c) todo
embudo declara sobre qué subpoblación se mide.
**Frecuencia:** RECURRENTE x5 en la raíz "el gate audita el artefacto, no su contexto de consumo real"
(EfiziAI · Veo3 · grilla · portapapeles · aquí ciclo-de-vida-consent + A/B-futuro).
**Severidad:** importante (no bloquea; la baja de élite a "aprobado con observaciones")

## 2026-08-11 — CLI tool (story-tool, re-juicio del BUILD) — story
**Punto ciego (CRÍTICO, security):** blocker #2 "fence bypass" reportado CERRADO por tech-lead y QA
(blockersClosed=true) pero SIGUE ABIERTO. `validate_trace` valida la SEMÁNTICA del identificador
(membresía en task_refs / resolubilidad del ref / contención+extensión de files) y luego `build_show`
imprime el STRING CRUDO del atacante en la partición TRUSTED (File List / QA Results, explícitamente
fuera del fence). 3 PoCs vivos confirmados por el juez con CERO setup: (A) `qa.verdict` nunca se valida
en NINGÚN lado (ni validate_trace ni model.from_text) → `verdict="pass\nPWNED..."` aterriza fuera del
fence; (B) el check `tid not in task_set` es CIRCULAR (el atacante controla task_refs Y las claves de
trace) → `tid="1.1\nPWNED..."` en ambos pasa; (C) `files=[".../x\nPWNED\ny.ts"]` pasa is_contained +
path_allowed (basename termina en .ts) y el newline rompe el code-span. El security-auditor lo cazó; el
tech-lead y el QA dieron falso all-clear.
**Por qué el pipeline lo pasó:** los tests de cierre prueban 3 INSTANCIAS (tid∉task_refs; verifies sin
'#'; files con '../') y pasan (suite 60 verde) → falsa confianza. "Es un ref resoluble" se confundió con
"es un string sin newline/control-chars". Validar la semántica de un id ≠ sanear el string que se emite a
un sink de confianza. La suite verde fue usada como evidencia de cierre — el modo de falla exacto.
**Señal de detección futura:** (a) cuando 2 reviewers dicen "cerrado" y 1 dice "abierto", CORRER el PoC
antes de creerle a la mayoría; (b) por CADA campo-máquina que aflore fuera del fence, exigir saneo
ESTRUCTURAL (allowlist / rechazo de [\x00-\x1f\x7f] / re-serialización), no validación semántica; (c)
todo sink de confianza que reciba datos derivados de input no confiable se audita por CLASE, no por
instancia — "¿qué OTRO campo llega crudo aquí?".
**Frecuencia:** RECURRENTE x7 en la raíz "se parchó/auditó la instancia, no la clase / el artefacto, no su
contexto de consumo real" — aquí el contexto es el sink TRUSTED del agente de build.
**Severidad:** crítico (bloquea producción; prompt-injection al contexto de confianza del agente)

## 2026-08-10 — Feature Android (entrenador 5 niveles, feature/trainer) — ReadCoach
**Punto ciego 1 (el único funcional real):** `MicSession.speak` usa `hardTimeout = (2000 + len*90).coerceAtMost(30_000)`,
CIEGO a la velocidad. Aritmética: Turn 4 (456 en / 512 es) y Turn 6 topan el techo de 30s; en N3 (rate 0.70,
~1.4x más lento) la línea corre ~43s → se corta a media frase, justo en el nivel de comprensión lenta donde esa
línea importa más. El build compila, 68 tests verdes, MicSession intacto por regla — pero NADIE oyó Turn 4 en N3.
La zona crítica se dejó sin tocar (correcto); el fix aditivo-seguro es de CONTENIDO (partir Turn 4/6 en dos
`DialogueTurn`), no de mecánica. Es RECURRENTE de la raíz "se audita el artefacto, no su consumo real": el
artefacto (código) es correcto, la experiencia (escuchar la línea) se rompe.
**Punto ciego 2 (defensa en profundidad muerta):** la invariante mejor-probada del módulo (Aborted → nunca
reabrir el mic, 2 tests) NUNCA se cablea en el ViewModel — el aborto runtime se logra solo por
`turnJob.cancel()`+`mic.cancel()`+guarda de fase. Las dos capas de seguridad del MICRÓFONO discrepan; un futuro
edit a la lógica de fase quita la única protección viva. Una línea en `block()` (`cursor = cursor?.advance(Aborted)`)
alinea código y test. Cae bajo REGLA #9 (invariante frágil = test, y aquí el test existe pero no respalda código vivo).
**Punto ciego 3 (cobertura del refactor P1.3):** la caracterización que congela el core extraído solo prueba
`softSkill=true`; la rama `else fb` (no-soft-skill conserva la opinión técnica) tiene CERO cobertura. El spec solo
pidió `softSkill=true`, así que no es violación — pero el propósito de P1.3 (proteger core probado en la extracción)
queda a medias en la rama que el modo entrevista sí usa en producción.
**Por qué el pipeline lo pasó:** el gate (build + 3 reviews) SÍ marcó los 3, pero como P1/P2 "verificar en device"
— correcto, salvo que sin device el #1 se queda en promesa. La aritmética ya predice el corte; no hace falta el
teléfono para saber que va a pasar.
**Señal de detección futura:** todo timeout/budget derivado de longitud debe recalcularse a mano contra el
PEOR caso de velocidad/tamaño del contenido real (no del típico) ANTES de aprobar; y toda invariante con test
propio debe tener un call-site vivo, o el test es teatro.
**Frecuencia:** RECURRENTE x6 en la raíz "el gate audita el artefacto, no su contexto de consumo real".
**Severidad:** importante (build mergeable; #1 es gate ANTES de shippear al teléfono)

## 2026-08-18 — DEPLOY MASIVO A VERCEL — carpeta "claude projects"
**Punto ciego encontrado:** El pipeline reporto 9 candidatos pero entrego `resultados=[]`,
`bloqueados=[]` y `hallazgos=[]`. Cero deploys ejecutados y cero razones documentadas:
un no-op presentado como pipeline completo. Verificado con `vercel projects ls` (ultimo
deploy real: 9 dias) y `find -mmin -720` (ningun archivo de proyecto tocado).
**Trampa de VERACIDAD detectada:** `freelance-landing.vercel.app`, `study-flow.vercel.app` y
`landing-leads.vercel.app` responden 200 pero son sitios de TERCEROS (nombres ocupados en
vercel.app). Un check "curl 200 = desplegado" habria producido 3 falsos positivos.
**Por que el pipeline lo paso por alto:** no hay gate que exija `deploys.length > 0 OR
bloqueados.length == candidatos.length`. Un array vacio pasa como "sin errores".
**Senal de deteccion futura:** (1) si `resultados` y `bloqueados` estan ambos vacios con
candidatos > 0 → RECHAZO automatico; (2) nunca validar deploy por HTTP 200: cruzar contra
`vercel projects ls` + `orgId` del scope del usuario.
**Frecuencia:** 1a vez

## 2026-08-19 — NEUTRALIZACION DE 4 PLANTILLAS DE VENTA — carpeta "plantillas"
**Punto ciego encontrado:** al quitar una senal falsa (JSON-LD colombiano) un agente
INTRODUJO otra senal falsa de la misma clase: plantilla-industrial ahora declara
`lang="en"` + `og:locale="en_US"` sobre una interfaz escrita en espanol
("Indice", "Saltar al contenido", "anatomia"). Verificado ejecutando
`npm run check:content` (exit 1) y leyendo `src/config/ui.strings.ts`.
El agente lo detecto y lo reporto, pero igual dejo la plantilla en ese estado.
**Segundo punto ciego (el que nadie vio):** plantilla-hotel declara en su propio
inventario que las cadenas fijas son "textos genericos y ciertos para cualquier
hospedaje" — pero son "Reservar", "Huespedes", "Entrada", "Salida", "Siguenos",
"Galeria". Generico != neutro: son espanol. ~25 cadenas visibles que NO estan
listadas en `shotlist-texto.json`. Detectado extrayendo el texto visible del
`index.html` con un regex y cruzandolo contra el JSON, no leyendo el reporte.
**Por que el pipeline lo paso por alto:** el criterio de aceptacion era un grep de
TERMINOS PROHIBIDOS (Manizales, Caldas, COP...). Un grep de lista negra no puede
detectar la ausencia de algo ni una senal falsa NUEVA. "Cero hits" se leyo como
"neutro", cuando solo significa "ninguno de los 12 terminos que se me ocurrieron".
**Tercer patron:** 3 de 4 plantillas protegen un `VERCEL_OIDC_TOKEN` y el correo
personal del vendedor con una VINETA EN EL README. Solo `plantilla-industrial`
tiene `npm run package`. La proteccion del P0 es prosa (viola REGLA #8).
**Senal de deteccion futura:** (1) para "neutralizar identidad", el gate no es grep de
lista negra sino INVENTARIO POSITIVO: extraer todo el texto visible del artefacto
compilado y exigir que cada cadena este en el inventario o sea placeholder;
(2) verificar `lang`/`og:locale` DECLARADO contra el idioma ESCRITO, siempre —
cambiar el locale sin traducir es cambiar de mentira, no quitarla;
(3) si un entregable contiene secretos, el gate es un script de empaquetado
fail-closed, nunca un checklist.
**Frecuencia:** RECURRENTE x2 en la raiz "el gate audita el artefacto, no su contexto
de consumo real" (aqui: el contexto es el comprador en EEUU, no el repo).
**Severidad:** BLOQUEANTE comercial (LICENSE indefinida en 4 formas distintas) +
importante (senal de idioma falsa).

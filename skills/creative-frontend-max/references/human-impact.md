# human-impact.md — Por qué algo mueve a un humano

> **Este es el documento raíz de la skill.** `webgl-craft`, `kinetic-type`, `pointer-interaction`,
> `system-viz` y `craft-details` dicen **CÓMO**. Este dice **POR QUÉ**, y sin el por qué el cómo
> produce ruido caro.

## La tesis (léela aunque no leas nada más)

**Técnica sin razón humana = slop.** Un shader impecable que no significa nada se lee como
plantilla. Y esto no es filosofía: es mecánico. El cerebro del visitante clasifica en
~50 ms si algo es *intencional* o *decorativo*. Lo decorativo se ignora — o peor, se lee como
"esta persona compró un template".

Lo que un jurado de Awwwards y un recruiter senior tienen en común: **ambos han visto mil
efectos**. Lo que no han visto es un efecto que *diga algo*. La escasez de la intención es el
lujo, no la cantidad de partículas.

Las tres preguntas que separan craft de ruido:

1. **¿Qué emoción humana busca este efecto?** (asombro, calma, curiosidad, tensión, orgullo)
2. **¿Qué le DA al usuario?** (información, orientación, jerarquía, deleite). Si sólo le quita
   (tiempo, batería, claridad), es un impuesto.
3. **Si lo borro, ¿se pierde algo?** Si la respuesta es no, sobraba.

Este documento existe para que puedas responder las tres con evidencia, no con vibras.

---

## 1. La psicología del AWE — la receta literal del "wow"

### La investigación real

Keltner & Haidt (2003, *Cognition and Emotion*, "Approaching awe, a moral, spiritual, and
aesthetic emotion") definen el asombro con **dos evaluaciones (appraisals) que están presentes
en TODOS los casos claros de awe**:

1. **Vastness (vastedad)** — el estímulo se percibe como *mucho más grande* que uno mismo y que
   las cosas a las que uno está acostumbrado. Puede ser vastedad física (una montaña), social
   (una multitud) o conceptual (una idea que abarca más de lo que creías).
2. **Need for accommodation (necesidad de acomodación)** — término tomado de Piaget: **la
   incapacidad de asimilar la experiencia en tus estructuras mentales actuales**. Tu modelo del
   mundo *no alcanza* y tiene que actualizarse. Ese ajuste ES el asombro.

Cinco appraisals secundarios modulan el *tono* (agradable/amenazante): amenaza, belleza,
habilidad excepcional, virtud, y lo sobrenatural.

**Corolario duro:** *escala sola no produce awe.* Un H1 gigante es sólo un H1 gigante.
**Vastness sin accommodation = decoración.** La accommodation es el ingrediente que la mayoría
de las páginas "impactantes" no tiene — y por eso se olvidan en 3 segundos.

### Cómo se traduce a la web

| Appraisal | Mecánica en pantalla | Parámetro concreto |
|---|---|---|
| **Vastness** | **Contraste de escala**, no tamaño absoluto. Algo se lee gigante sólo *junto a* algo pequeño. | Ratio de escala **≥ 8:1** entre el elemento dominante y el cuerpo de texto adyacente. `clamp(4rem, 14vw, 13rem)` contra `1rem`. |
| **Vastness** | **Romper el viewport**: el objeto se sale del marco → el cerebro infiere que continúa. Un objeto contenido es un objeto medido; uno cortado es infinito. | El elemento sangra ≥ 15% fuera de al menos un borde. Nunca `contain`. |
| **Vastness** | **Profundidad**: campo de estrellas/partículas con paralaje por capas, niebla exponencial. El infinito se siente, no se declara. | ≥ 3 planos de profundidad con velocidades distintas (`0.2x / 0.6x / 1.0x`). |
| **Accommodation** | **EL REVEAL QUE RE-ENCUADRA**: lo que el usuario creía que era X resulta ser Y. Aquí está el 90% del wow. | Un solo evento. Ver receta abajo. |
| **Accommodation** | **Cambio de sistema de referencia**: la cámara retrocede y lo que era "el fondo" era en realidad "un detalle de algo enorme". | `camera.position.z` de 4 → 28 en 1200 ms con `expo.out`, revelando que el objeto era 1 nodo de 200. |

### El "reveal que re-encuadra" (esto es LA receta)

> **El usuario debe tener que actualizar su modelo mental de lo que estaba mirando.**

Fórmula en 3 tiempos:
1. **Establecer una lectura** (5–10 s de scroll). El usuario cree entender qué es el objeto.
2. **Contradecirla con un solo movimiento** (600–1200 ms). No con cinco efectos: con uno.
3. **Dejar la nueva lectura estable** (el objeto ahora *es* otra cosa, y se queda así).

### Ejemplo concreto — portafolio-frontend

Hoy: un `laptop.glb` que viaja por la página con poses keyframed. Eso es **vastness = 0,
accommodation = 0**. Es un objeto que se mueve. Bonito, olvidable.

Convertirlo en awe:

- **Acto 1 (hero):** el laptop está **cerrado**, pequeño, centrado, con una luz dura lateral.
  El usuario lo lee como "un objeto decorativo bonito". Lectura establecida.
- **Acto 2 (el pico, ~35–45% de la página):** al entrar la sección de arquitectura, el laptop
  **se abre** (`LidPivot` — ojo: `gltf-transform optimize` lo borra, ver
  `reference_3d_scroll_r3f_blender`), la cámara hace **dolly-in hacia la pantalla**, y **la
  pantalla del laptop deja de ser una pantalla: el contenido de la sección está DENTRO**. Un
  segundo después la cámara sigue empujando y **atraviesa** la pantalla → el usuario ya no está
  mirando un laptop, **está dentro del sistema**: los 9 microservicios como nodos, las aristas
  con paquetes viajando (ver `system-viz.md`).
  - **Vastness:** lo que cabía en 300 px ahora es un espacio que no cabe en el viewport.
  - **Accommodation:** "no era un objeto decorativo, era la *puerta*". El modelo mental se rompe
    y se reconstruye. Eso es awe, medible, en una web.
- **Acto 3:** la cámara sale (push-out) y el laptop, ahora abierto, queda pequeño otra vez en la
  esquina, mientras el contenido sigue. **La escala pequeña después de la grande es lo que hace
  que la grande se haya sentido grande.**

Presupuesto: **UN** reveal en toda la página. Si hay dos, no hay ninguno (ver §4, peak-end).

**Anti-patrón:** "hago que todo sea grande y con mucha profundidad". Eso es vastedad plana:
el usuario se acostumbra en 2 s (habituación) y el efecto se evapora. **El awe vive del
contraste, y el contraste requiere que la mayor parte de la página sea sobria.**

---

## 2. Cine — el lenguaje de los que llevan 100 años resolviendo esto

### 2.1 Composición

| Recurso | Qué comunica | Cuándo usarlo | Traducción a la web |
|---|---|---|---|
| **Regla de tercios** | Dinamismo, tensión, movimiento implícito, "va a pasar algo" | Heroes narrativos, secciones de proceso | Sujeto en la intersección: `grid-template-columns: 1fr 1fr 1fr` y el foco en la columna 1 o 3, no en la 2. El objeto 3D en x ≈ ±0.33 del ancho. |
| **Centrado simétrico** | Autoridad, orden, monumentalidad, *poder institucional* (Kubrick, Wes Anderson) | Un único momento de declaración: el nombre, la tesis, el CTA final | Centrado perfecto **sólo si el resto de la página NO es simétrica**. Simetría en todo = catálogo aburrido; simetría en un solo punto = trono. |
| **Encuadre desequilibrado (aire a un lado)** | Espera, algo fuera de campo, incomodidad productiva | Antes de un reveal | Deja el 60% del hero vacío al lado del sujeto. El cerebro *quiere* llenarlo → hace scroll. |

**Opinión:** un portafolio de arquitecto de soluciones debería ser **simétrico y monumental en el
hero** (autoridad: "yo diseño sistemas, no maquillo botones") y **asimétrico en las pruebas**
(dinamismo: "y esto se mueve"). Lo contrario es lo que hace todo el mundo.

### 2.2 Lenguaje de cámara — cada movimiento es una frase

| Movimiento | Significado emocional | Parámetro web |
|---|---|---|
| **Dolly-in** (la cámara avanza) | **Intimidad, revelación, "presta atención a ESTO"**. Es el movimiento del descubrimiento. | `camera.position.z` -35% en **800–1200 ms**, `expo.out`. Scroll-linked, no autoplay. |
| **Push-out / dolly-out** | **Soledad, contexto, consecuencia, cierre**. "Esto que viste era pequeño en el mundo." | z +200%, 1000–1500 ms. Perfecto para el **final** de la página. |
| **Dolly zoom (Vertigo)** | Desorientación, el suelo se mueve. **Casi siempre un error en web** (mareo, §8). | Sólo si el contenido *trata* de la desorientación. Prohibido con `prefers-reduced-motion`. |
| **Paralaje (traslación lateral)** | **Profundidad, materialidad, "esto es un espacio real"**. Barato y potentísimo. | Capas a `0.2x / 0.5x / 1.0x`. **Amplitud máxima 8–12% del viewport.** Más = mareo (§8). |
| **Truck/pan lento constante** | Vida, respiración, "esto no es una foto" | Rotación ambiental de **≤ 0.05 rad/s**, ruido tipo Perlin. Casi imperceptible. Es la diferencia entre "3D" y "vivo". |
| **Cámara quieta** | Peso, seriedad, confianza | **La cámara quieta es una decisión, no una ausencia.** Si todo se mueve, nada se mueve. |

**Regla:** la cámara la mueve **el scroll del usuario**, nunca un timer. El movimiento
autónomo de cámara le quita al usuario la autoría de lo que ve → es exactamente la sensación de
"anuncio", no de "obra".

### 2.3 Claroscuro — POR QUÉ una luz dura sobre fondo oscuro se lee como CARO

Caravaggio (y todo el Barroco) resolvió esto en 1600: **el ojo humano lee "importante" como
"iluminado"**. Con un fondo oscuro, el 90% del campo visual no compite, y la luz se convierte en
una *flecha* que no parece una flecha. Es dirección de atención sin UI.

Por qué se lee como **caro** específicamente:
- La luz dura revela **material** (grano, metal, borde, subsurface). El plano lo esconde. Nuestro
  cerebro asocia "puedo ver de qué está hecho" con "es real" con "cuesta dinero".
- Un fondo oscuro **oculta los errores baratos** (bordes duros, aliasing, texturas pobres) y
  perdona presupuesto. Es literalmente la técnica de bajo presupuesto que se ve de alto.
- El contraste alto = alta fluidez de procesamiento en la figura (§3) → belleza percibida.

**Traducción a la web (números):**

```css
/* La paleta del claroscuro. NO uses #000: mata el grano y se ve barato en OLED. */
--bg-deep:   #08090B;   /* fondo. Casi negro, pero con temperatura */
--bg-raise:  #101216;   /* superficies elevadas: +2 a +4% luminancia, nunca más */
--key:       #F4F1EA;   /* la LUZ. Cálida, nunca #FFF puro */
--accent:    /* UN solo acento saturado. Uno. */
```

- **Key-to-fill ratio: 8:1 a 16:1** (en Three.js: `keyLight.intensity = 8`, `ambientLight ≈ 0.4–0.8`).
  Ratios de 2:1 se ven a "producto de stock"; 16:1 se ve a cine.
- **Rim light / contraluz obligatoria** en el objeto principal: una luz débil (intensidad 1–2)
  detrás y arriba, del color del acento. **Es la que separa la figura del fondo** (§3) y la que
  hace que un modelo mediocre se vea bien. Sin rim light, el objeto oscuro sobre fondo oscuro es
  una mancha.
- **Silueta primero:** si pones el objeto en negro plano sobre blanco plano, ¿se reconoce?
  Si no, ningún shader lo va a salvar. Los animadores de Disney testeaban así cada personaje.
  Aplica al laptop: **la silueta del laptop abierto (el ángulo en L) es icónica; cerrado es un
  ladrillo.** Por eso el reveal de abrirlo funciona: *es un cambio de silueta*.
- **Vignette:** sutil, `0.25–0.4` de intensidad. Más = filtro de Instagram de 2012.

**El costo del claroscuro:** contraste de texto. Un fondo `#08090B` con texto `#8A8A8A` da ~4.6:1
— pasa AA de raspón. **No hagas eso.** Texto de cuerpo mínimo `#C9C6C0` sobre `#08090B` ≈ **11:1**.
Los grises tenues "elegantes" son la forma #1 en que un portafolio bonito se vuelve inutilizable
al sol en un teléfono (§8).

### 2.4 Ritmo y pacing — tensión → liberación

Ninguna película es intensa todo el tiempo. **La intensidad continua es indistinguible del
ruido.** El cine construye: calma → tensión → *más* tensión → **liberación** → calma.

**Traducción:** el eje de scroll es tu línea de tiempo. Mapea densidad:

```
Sección:   HERO      QUIÉN     PROYECTOS   [EL PICO]   PROCESO    CIERRE
Densidad:  ███       ░          ██          █████      ░           ██
Motion:    lento     ninguno    medio       máximo     ninguno     lento
Espacio:   mucho     mucho      poco        TODO       mucho       mucho
```

- **La sección INMEDIATAMENTE anterior al pico debe ser la más quieta y sobria de la página.**
  Esto no es un desperdicio: es el silencio antes del acorde. Sin él, el pico no existe.
- **El corte:** en cine, el corte duro es información. En web, es la **transición de sección sin
  animación**. Después de un momento cinematográfico, un corte seco a fondo claro y tipografía
  desnuda es más potente que otra animación. **Cambiar de registro > subir el volumen.**
- **Duración del pico: 1.5–3 s de scroll** (≈ 800–1600 px de recorrido a velocidad natural con
  Lenis). Menos y no se registra; más y el usuario siente que le secuestraron el scroll (§8).

### 2.5 El hero shot

En cine el "hero shot" es el plano donde el objeto se presenta con su mejor luz y su mejor
ángulo, y **la cámara le da tiempo**. En web, el hero shot no es "el hero de la página": es
**el frame que el usuario podría capturar y compartir**.

**Test:** haz un screenshot en un momento cualquiera del pico. ¿Ese PNG suelto, sin contexto, se
sostiene como imagen? Si no, no tienes hero shot, tienes movimiento.

---

## 3. Percepción — por qué el ojo obedece antes de que la mente decida

### 3.1 Gestalt (lo que sí importa)

| Ley | Qué hace | Traducción |
|---|---|---|
| **Proximidad** | Lo cercano se lee como un grupo, **más fuerte que cualquier borde o color** | **Espaciado intra-grupo ≤ 40% del espaciado inter-grupo.** Si tu label está a 8px del input, el siguiente grupo empieza a ≥ 24px. Esto solo arregla el 60% de los layouts "sucios". |
| **Continuidad** | El ojo sigue líneas y curvas y las completa | Alinea los elementos a un eje real. Un elemento fuera del eje **cuesta** atención — úsalo sólo cuando quieras que cueste. |
| **Cierre** | La mente completa formas incompletas — **y disfruta haciéndolo** | **Corta el objeto con el borde del viewport.** El usuario completa mentalmente el laptop que se sale → participa → se involucra. Un objeto entero y centrado no le pide nada. |
| **Figura-fondo** | El cerebro **obliga** a asignar un rol: una cosa es objeto, la otra es espacio | La clave del hero (abajo) |
| **Destino común** | Lo que se mueve junto, es junto | Stagger: los ítems que entran juntos con el mismo easing son percibidos como una sola cosa. Si quieres separar dos grupos, **dales easings distintos**, no colores distintos. |

### 3.2 Figura-fondo: por qué es LA clave de un hero que respira

El cerebro **no puede** procesar figura y fondo simultáneamente como figura. Tiene que elegir.
Un hero que "no respira" es un hero donde **el fondo está compitiendo por ser figura**: el
gradiente animado, las partículas brillantes, el mesh gradient, el video — todos gritan "soy un
objeto".

Resultado: el usuario no sabe dónde mirar → carga cognitiva → **se percibe como barato**, aunque
cada pieza sea técnicamente impecable. Esta es exactamente la razón por la que "efectos sin
razón" se leen como cheap: **rompen la asignación figura-fondo**.

**Reglas duras:**
- **El fondo debe ser CAMPO, no OBJETO.** Un campo tiene: baja frecuencia espacial, bajo
  contraste interno (**< 1.3:1 entre sus zonas**), y movimiento por debajo del umbral de
  detección atencional (velocidad angular baja, sin bordes duros).
- Si tu fondo tiene bordes definidos y alto contraste interno, ya no es fondo. **Difumínalo o
  bájalo:** `opacity ≤ 0.35`, blur, o menos densidad de partículas.
- **Una sola figura por pantalla.** El H1 **o** el objeto 3D. No los dos con el mismo peso. En
  el hero de un portafolio de ingeniero: **la figura es el H1** (el LCP es el H1, además — ver
  el presupuesto en SKILL.md), y el 3D es atmósfera. En el pico, se invierten.
- El "respiro" es literalmente **Ma** (§6): **≥ 40% del hero vacío**, y ese vacío debe ser
  contiguo, no migajas de padding.

### 3.3 Fluidez cognitiva (processing fluency) — el hallazgo incómodo

Reber, Schwarz & Winkielman (2004, *Personality and Social Psychology Review*): **cuanto más
fluidamente se procesa un objeto, más positiva es la respuesta estética.** La belleza no está
sólo en el estímulo, está en **la experiencia de procesarlo**. Y el efecto se extiende a la
verdad: lo fácil de procesar **se juzga como más verdadero** (fluency → truth effect).

Variables que aumentan fluidez: **buena figura (Prägnanz), contraste figura-fondo, simetría,
prototipicidad, repetición, priming**.

**Consecuencia brutal para un portafolio:** tu página no sólo se ve más bonita si es fácil de
procesar — **te hace parecer más competente y más creíble**. Una página difícil de leer se lee
como un ingeniero difícil de trabajar. Ese es el ROI de la tipografía.

**Traducción (números):**
- Cuerpo: **16–18 px**, `line-height` **1.55–1.7**, **medida de 60–75 caracteres**
  (`max-width: 62ch`). Fuera de eso la fluidez cae y con ella la percepción de calidad.
- Contraste texto: **≥ 7:1** para cuerpo en fondo oscuro (AAA), no el mínimo 4.5:1.
- **Escala modular** (no tamaños al azar): ratio **1.25** (dashboards/densidad) o **1.333–1.5**
  (editorial/portafolio). Un solo ratio en toda la página. La consistencia de ratio es
  literalmente fluidez.
- **Una familia de easing en todo el sitio** (§5). Cambiar de easing entre componentes es la
  versión temporal de usar 6 tipografías.

**La tensión real** (dilo en voz alta cuando alguien pida "más wow"):
> **Fluidez = belleza + credibilidad. Awe = ruptura de fluidez (accommodation).**
> Son fuerzas opuestas. Por eso la página tiene que ser **99% fluida y 1% ruptura**.
> Un sitio "todo wow" es un sitio con la fluidez destruida: se ve caro en un screenshot y
> se siente barato al usarlo. **Ese es exactamente el fracaso que hay que evitar.**

### 3.4 Jerarquía visual real

La jerarquía no es "títulos grandes". Es **el orden en que el ojo aterriza**, y se controla con
cinco palancas, en este orden de fuerza:

1. **Contraste de luminancia** (la más fuerte, con diferencia — es preatencional)
2. **Tamaño / masa visual**
3. **Aislamiento** (espacio alrededor — un elemento solo gana a uno grande acompañado)
4. **Movimiento** (secuestra la atención de forma involuntaria; por eso es un arma cargada)
5. **Color/saturación** (la más débil de las cinco, y la que todo el mundo usa primero)

**Test de los ojos entrecerrados:** desenfoca la pantalla (o `filter: blur(8px)`). Deberías ver
**exactamente 3 manchas** en orden claro de prioridad. Si ves 8 manchas iguales, no hay
jerarquía, hay una lista.

---

## 4. Memoria y emoción — diseñas un RECUERDO, no una experiencia

### 4.1 Peak-end rule (Kahneman, Fredrickson, Schreiber & Redelmeier, 1993)

El "yo que recuerda" resume una experiencia con **dos muestras: el PICO y el FINAL**. La
duración es prácticamente irrelevante — **duration neglect** (confirmado en meta-análisis de 2022:
el efecto peak-end sobre la evaluación retrospectiva es grande y robusto; el efecto de la
duración es esencialmente nulo).

**Esto reescribe cómo se asigna el presupuesto de craft.** No estás diseñando 8 secciones.
Estás diseñando **2 momentos** y 6 secciones que no los estorben.

**Traducción, como ley:**

> ### LA REGLA DEL PICO ÚNICO
> **UN (1) momento signature en toda la página. Todo lo demás lo SOSTIENE.**
> Cinco momentos memorables = cero momentos memorables. El promedio no se recuerda; el pico sí.
> Repartir el presupuesto de efectos equitativamente entre secciones es **la forma exacta** de
> producir una página que se siente "cargada" y no se recuerda.

> ### LA REGLA DEL FINAL
> **El final NO es el footer. El final es el último momento diseñado antes de irse.**
> La mayoría de los portafolios mueren en un `<footer>` con tres iconos grises. Estás tirando el
> 50% del recuerdo. El cierre debe tener: una frase con peso, un CTA sin fricción, y **un último
> gesto** (push-out de la cámara; el laptop se cierra; el grano se detiene; una línea que se
> completa). Barato de implementar, desproporcionado en retorno.

**Ejemplo concreto (portafolio-frontend):**
- **PICO:** el reveal de la §1 (atravesar la pantalla → estás dentro del sistema).
- **FINAL:** al llegar al contacto, la cámara hace **push-out** hasta que el laptop es un punto
  de luz en el vacío, la niebla se cierra, y queda sólo: nombre + una línea + un email que se
  copia con un click y confirma. **Duración total ~1200 ms, `expo.out`.** Eso es lo que el
  visitante le va a describir a otra persona.
- Y por lo tanto: **las secciones de proyectos NO llevan efectos WebGL.** Llevan tipografía
  impecable, buena foto y cero movimiento gratuito. Ese es el sacrificio que hace que el pico
  exista.

### 4.2 Anticipación → pago

El placer no está en el evento; está en **la expectativa cumplida**. Un reveal sin anticipación
es un sobresalto (`jump scare`): sorprende y no gusta. Un reveal anticipado es una promesa
cumplida: gusta y se recuerda.

**Cómo se construye anticipación en scroll (esto es lo que casi nadie hace):**
- **Foreshadowing:** el objeto del pico debe **existir antes**, sin explicarse. El laptop cerrado
  en el hero es una pregunta abierta ("¿qué hay dentro?"). El usuario lleva 40% de la página
  cargando esa pregunta sin saberlo.
- **Rampa:** en los ~300 px antes del pico, sube tensión con señales sutiles: el grano se
  intensifica, la luz key se estrecha, el ambient se apaga 20%, el texto se pone más pequeño y
  más suelto. **El usuario no lo nota; lo siente.**
- **Micro-pausa antes del pago:** 80–150 ms de quietud justo antes del movimiento grande. En
  música se llama *anacrusa*; en animación, *anticipación* (§5). Sin ella, el reveal se lee
  mecánico.
- **El pago se cobra completo:** el reveal no se puede interrumpir a la mitad ni ser tímido. Si
  vas a atravesar la pantalla, atraviésala. La media tinta es peor que no hacerlo.

### 4.3 Norman: visceral / conductual / reflexivo

| Nivel | Qué es | Cuándo actúa | En tu página |
|---|---|---|---|
| **Visceral** | Reacción pre-consciente, ~50 ms. Forma, color, luz, silueta. | El primer frame | Claroscuro + silueta + escala. **Es lo que decide si siguen scrolleando.** Aquí manda §2 y §3. |
| **Conductual** | La sensación de usarlo. Fluidez, feedback, control. | Todo el scroll | Lenis suave pero **con la inercia correcta** (`lerp` 0.08–0.12; más alto = flotante y mareante), hovers de 120 ms, cero jank. **Un solo frame perdido destruye el nivel conductual** — y este es el nivel que un recruiter técnico juzga. |
| **Reflexivo** | La historia que se cuenta después. Identidad, orgullo, significado. | Al cerrar la pestaña | "Este tipo diseña sistemas y **me hizo *ver* un sistema**." El reflexivo es donde el pico paga. Es también el único nivel que produce un mensaje de LinkedIn. |

**Los tres o ninguno.** Visceral sin conductual = bonito y odioso. Conductual sin reflexivo =
correcto y olvidable (**exactamente donde está el 95% de los portafolios de ingeniero**).

---

## 5. Movimiento — por qué un easing correcto se lee como "caro"

**El mecanismo:** el cerebro tiene un modelo físico integrado (masa, inercia, fricción). Cuando
algo se mueve **linealmente**, viola ese modelo → se lee como *mecánico, falso, barato*. Cuando
acelera y frena como un objeto con masa, el cerebro lo acepta como real → **realidad = calidad**.
No es gusto: es física esperada.

**Corolario:** `linear` en una UI es el equivalente visual del Comic Sans. Sólo se permite en
loops infinitos (marquee, rotación ambiental) y en animaciones **acopladas al scroll**
(ahí el easing lo pone el usuario con su dedo — meterle otro easing encima es lo que produce esa
sensación de "esto va con retraso").

### Los principios de Disney que SÍ aplican a UI

| Principio | Traducción a UI | Parámetro |
|---|---|---|
| **Slow-in / slow-out (ease)** | **El único no negociable.** Todo lo que entra desacelera; todo lo que sale acelera. | Entrada: `expo.out` = `cubic-bezier(0.16, 1, 0.3, 1)`. Salida: `power2.in`. Ida y vuelta: `cubic-bezier(0.65, 0, 0.35, 1)`. |
| **Anticipación** | Un micro-movimiento **contrario** antes del movimiento principal. Es lo que hace que el usuario *sepa* que algo va a pasar. | Botón al presionar: `scale 1 → 0.96` en **80 ms**, luego la acción. Un panel que sube: baja 4 px en 100 ms y luego sube. Cuesta 100 ms y cambia el registro por completo. |
| **Follow-through / overlapping** | Las partes no llegan todas a la vez. La sombra llega después del objeto; el texto después de la tarjeta. | **Stagger 40–80 ms.** El elemento secundario arranca cuando el primario va al 60%. |
| **Arcs** | **Nada natural se mueve en línea recta.** El movimiento rectilíneo puro es robótico. | Trayectorias con `MotionPath` o un simple offset en el eje perpendicular. Un objeto que va de A a B **se desvía 5–15%** en el eje perpendicular. Aplica a tu laptop entre poses: **hoy va recto entre keyframes; que vaya en arco.** |
| **Exageración** | La física real se ve *floja* en pantalla. Hay que empujarla. | `back.out(1.2–1.5)` = un overshoot de **3–6%**. Más de 10% = juguete/infantil. Menos de 2% = no se percibe. |
| **Squash & stretch** | **Casi siempre NO en UI profesional.** Deforma → lee a juguete. | Excepción: microinteracciones lúdicas (like, toggle). Nunca en un portafolio de arquitecto. |
| **Puesta en escena (staging)** | Una idea por movimiento. Si dos cosas se mueven a la vez compitiendo, ninguna se ve. | Nunca dos animaciones de ≥ 400 ms simultáneas en zonas distintas de la pantalla. |

### El sistema de motion (memorízalo — 1 familia, 3 duraciones)

```js
// UNA familia de easing en todo el sitio. Cambiarla entre componentes = 6 tipografías.
const EASE = {
  out:   'cubic-bezier(0.16, 1, 0.3, 1)',    // expo.out — entradas, reveals. EL easing "caro".
  inOut: 'cubic-bezier(0.65, 0, 0.35, 1)',   // movimientos que salen y llegan
  in:    'cubic-bezier(0.55, 0, 1, 0.45)',   // salidas, cosas que se van
  back:  'back.out(1.4)',                    // GSAP: sólo para el 1 elemento con personalidad
};

const DUR = {
  micro:  0.12,  // 120 ms — hover, press, focus, color. Debe sentirse INSTANTÁNEO.
  ui:     0.32,  // 320 ms — menú, modal, tarjeta, acordeón.
  cine:   0.90,  // 900 ms — reveal de sección, movimiento de cámara. SÓLO para el pico.
};
```

**Números duros:**
- **< 100 ms** = el usuario lo percibe como instantáneo (no lo "ve" como animación). Ideal para
  feedback de input.
- **100–300 ms** = el rango de UI. Aquí vive el 90% de lo que animas.
- **> 400 ms** en algo que **bloquea la lectura** = **impuesto** al usuario (§8). Prohibido, salvo
  en el pico.
- **> 1000 ms** = sólo cinematográfico, sólo scroll-linked, sólo una vez en la página.
- **Distancia importa:** un elemento que recorre 20 px no puede tardar lo mismo que uno que
  recorre 400 px. Escala aproximada: **duración ≈ 0.2 s + distancia_px / 1200**. Un fade de un
  tooltip a 8 px en 300 ms se siente *lento y pegajoso*.
- **Stagger total ≤ 600 ms.** Si tienes 12 tarjetas a 80 ms, la última entra en 960 ms → el
  usuario ya está leyendo abajo y ve elementos apareciendo tarde: se lee como bug, no como craft.
  Con >8 elementos: baja el stagger a 30–40 ms, o anima el **grupo**, no los ítems.

**El error más común (y el más caro):** animar `opacity` desde 0 en contenido de texto que el
usuario ya podría estar leyendo. **Un fade-in de texto es tiempo robado.** Prefiere un reveal por
**máscara** (`clip-path`), que es un gesto (el texto *llega*), no una espera (el texto *aparece*).
Y con `prefers-reduced-motion`, el texto simplemente ya está ahí.

---

## 6. Historia del arte y del diseño — qué robar de cada uno

| Corriente | La idea central | Qué robar exactamente | Dónde en un portafolio de ingeniero |
|---|---|---|---|
| **Bauhaus** (1919) | La forma sigue a la función; el material dice la verdad | **Grid honesto**, geometría primaria, cero ornamento aplicado. El ornamento debe *ser* la estructura. | La retícula base de todo el sitio. Si un elemento no está en la grid, tiene que ser una decisión declarada. |
| **Estilo Suizo / Internacional** (Müller-Brockmann, 1950s) | **La retícula y el blanco son el diseño**; la tipografía es información | Retícula de **12 columnas**, tipografía sans neutra a **1 sola familia y 2 pesos**, alineación **flush-left / ragged-right** (nunca justificado en web), jerarquía por tamaño y espacio, **no por decoración** | El 90% de tus páginas. Es la base sobre la que el 10% restante puede explotar. **Es lo que hace que un dev senior te respete.** |
| **Constructivismo** (Rodchenko, El Lissitzky) | **La diagonal = tensión y velocidad**; el texto es forma | Diagonales fuertes, tipografía como bloque estructural, negro + rojo + blanco, cortes agresivos | La sección del pico. Una diagonal en una página ortogonal es **violencia visual controlada** — llama la atención sin gritar. Úsala **una vez**. |
| **Barroco / Caravaggio** | La luz **dirige** y **dramatiza** | Claroscuro (§2.3), luz dura direccional, diagonal compositiva, un solo foco | La iluminación de toda tu escena 3D. Es la diferencia entre "render de práctica" y "producto". |
| **Ma 間 (japonés)** | **El vacío no es ausencia: es el elemento activo.** Es el intervalo que da sentido a lo que hay | El vacío **con forma e intención**, no padding sobrante. Asimetría. El silencio antes del sonido. | **≥ 40% del hero vacío**, y una sección entera de "casi nada" antes del pico (§2.4). **El coraje de dejar vacío es la señal #1 de confianza en el trabajo.** Un CV con miedo al vacío es un CV con miedo. |
| **Wabi-sabi** | La imperfección y el paso del tiempo son belleza; lo perfecto es inhumano | **Grano/noise** (2–5% de opacidad), micro-imperfecciones, aberración cromática mínima, texturas orgánicas | El grano es el detalle más barato y más transformador que existe: **un `data:` URI de 2 KB convierte un gradiente digital plano en una superficie con materia.** Sin él, todo se ve a Figma. Con él, se ve a película. |
| **Proporción áurea / escala modular** | Relaciones, no medidas | **φ = 1.618** para layouts (una división 62/38 en lugar de 50/50 o 70/30). Escala tipográfica **1.25 / 1.333 / 1.5**. Espaciado en potencias: 4-8-12-16-24-32-48-64-96-128. | La grid y la escala de tipos. Y **un solo ratio en toda la página** (fluidez, §3.3). |
| **Brutalismo** | **Honestidad del material**: el hormigón se ve como hormigón | Mostrar la estructura, monospace de verdad, bordes duros, cero skeuomorfismo, cero glassmorphism decorativo | Aquí hay algo específico para ti: **el brutalismo digital es honestidad de ingeniero.** Un bloque de código real, un diagrama real, un log real, mostrados sin maquillar, con tipografía mono impecable — es más impresionante que un gradiente. **Muestra el material: sistemas.** |

**Regla de robo:** **una corriente domina, una segunda tensiona, el resto no entra.**
Recomendación para portafolio-frontend: **base Suiza (autoridad, legibilidad, retícula) +
Barroco en la escena 3D (luz, drama) + Ma en el espacio + grano wabi-sabi.** Y una diagonal
constructivista **una sola vez**, en el pico. Eso es un sistema, no un moodboard.

---

## 7. Narrativa — la página como arco, no como lista

Una página con secciones es un catálogo. Una página con **arco** es una experiencia. Nadie hace
scroll por 8 secciones; la gente hace scroll porque **quiere saber qué pasa después**.

| Beat | Función dramática | Sección | Qué tiene que lograr | Motion |
|---|---|---|---|---|
| **1. Gancho** | Detener. Ganarse los siguientes 5 s. | Hero | **Una frase que sea una posición, no un título de puesto.** "Solutions Architect" es un puesto. "Diseño los sistemas que no se caen a las 3 a.m." es un gancho. + un objeto que abre una pregunta (laptop cerrado). | Mínimo. Un reveal por máscara del H1 (900 ms) + respiración ambiental. **El hero no es el pico.** |
| **2. Promesa** | Decir qué va a obtener. Contrato con el lector. | Qué hago / tesis | 2–3 líneas. Concreto: .NET, Node, microservicios, agentes LLM, 13+ años. **Sin adjetivos.** | Cero. Sobriedad = confianza. |
| **3. Prueba** | Cumplir el contrato. Evidencia. | Proyectos | un sistema de microservicios, un producto de voz + LLM, etc. **Números, arquitectura, decisiones. No screenshots bonitos: decisiones.** | Cero WebGL. Tipografía y foto. Este es el sacrificio que financia el pico. |
| **4. GIRO** | **Reencuadrar. Aquí vive el awe (§1).** El visitante creía que veía un portafolio; ahora ve una mente. | El pico | El laptop se abre → la cámara atraviesa → **estás dentro de la arquitectura**, los nodos se organizan, los paquetes viajan por las aristas. **El giro es: "no construyo páginas, construyo sistemas — y aquí está uno, vivo."** | **TODO el presupuesto.** 1.5–3 s de scroll. |
| **5. Cierre** | El FINAL de la peak-end rule. Lo último que se recuerda. | Contacto | Push-out, el sistema se aleja hasta ser un punto, una frase con peso, un email de un click. **Fricción cero.** | Un solo gesto, 1200 ms, `expo.out`. |

**Cómo se sabe si el arco existe:** describe la página en 5 frases, una por beat, sin usar la
palabra "sección" ni nombrar tecnologías. Si no puedes, no hay arco: hay un `<div>` detrás de
otro.

**El giro tiene que ser TUYO.** El giro genérico ("mira, partículas") no es un giro. El tuyo es
específico: **eres arquitecto de sistemas y de agentes LLM; el giro es hacer que un sistema
distribuido sea *visible y bello*, algo que tus competidores describen con bullets.** Esa es la
única ventaja competitiva no copiable que tienes en una página web.

---

## 8. LO FUNCIONAL — el contrapeso (y pesa lo mismo que lo bello)

**Un efecto que estorba al humano no es "arte con costo": es un defecto.** Esta sección tiene el
mismo rango que todas las anteriores. En una página que va a ver un recruiter técnico en un
Android de gama media con datos móviles, **es la que decide si te contratan.**

### 8.1 Legibilidad por encima de todo. Sin excepciones.

- **El texto nunca se sacrifica por un efecto.** Ni por blur, ni por un video, ni por un gradiente
  animado detrás, ni por un `mix-blend-mode` "que se ve genial".
- Contraste: **≥ 4.5:1 (AA) obligatorio, ≥ 7:1 (AAA) es el objetivo** para cuerpo. Texto grande
  (≥ 24 px, o ≥ 18.66 px bold): ≥ 3:1. **Mídelo, no lo estimes** — el gris "elegante" `#888`
  sobre `#0A0A0B` da ~5.3:1 y se vuelve ilegible al sol.
- **Si el texto va sobre algo vivo (canvas, video, imagen): capa de protección obligatoria.**
  Un `backdrop` sólido o un gradiente de ≥ 55% de opacidad. "Se lee bien en mi monitor" no es
  evidencia.
- Tamaño mínimo de cuerpo: **16 px**. En móvil, 16 px también evita el zoom automático de iOS en
  inputs.

### 8.2 El usuario nunca pierde el control

- **PROHIBIDO el scroll-jacking.** Nada de "hago scroll y la página decide llevarme a otro lado",
  nada de secuestrar la rueda para hacer un slider horizontal a la fuerza, nada de secciones que
  no dejan avanzar hasta que la animación termine. **Lenis suaviza; no secuestra.** La distinción:
  ¿la posición final del scroll sigue siendo una función monótona de lo que hizo el dedo? Si no,
  es secuestro.
  - Config segura de Lenis: `lerp: 0.1` (rango sano 0.08–0.12). `lerp < 0.06` = flotante,
    mareante, y rompe la sensación de control. **Y `syncTouch` desactivado o muy conservador**:
    en móvil, pelear con el scroll nativo es la forma más rápida de que cierren la pestaña.
- **Toda animación scroll-linked debe ser reversible y scrubbable.** Si el usuario hace scroll
  hacia arriba, el estado vuelve exactamente. Un efecto que sólo va hacia adelante es un bug.
- **Nada de autoplay que compita con la lectura.** Si algo se mueve solo mientras el usuario lee,
  le estás robando ancho de banda atencional (§3.4: el movimiento es preatencional; no puede
  ignorarlo aunque quiera).
- **Nunca desactives el scroll durante un preloader de más de 1.5 s.** Y el preloader necesita
  justificarse: si no estás cargando 8 MB, no tienes derecho a un preloader.

### 8.3 Cero mareo — esto es una condición médica, no una preferencia

El movimiento en pantalla activa el sistema vestibular. En personas con trastornos vestibulares
(≈ 35% de adultos mayores de 40 años tienen alguna disfunción), el parallax agresivo produce
**náusea real**. No es "no les gusta": **se marean**.

- **`prefers-reduced-motion: reduce` es obligatorio y no negociable.**
  - **Congelar, no ocultar.** Una escena 3D **estática y bien iluminada** es hermosa. Un hueco
    vacío es un bug. Congela `delta → 0`, no desmontes el canvas.
  - Reemplaza translate/scale/parallax por **fade de ≤ 150 ms** o por **nada**.
  - Los reveals por scroll: el contenido **ya está visible**, punto.
- **Parallax: amplitud máxima 8–12% del viewport.** Por encima de eso, el desacople entre lo que
  el ojo ve y lo que el oído interno espera se vuelve provocador de náusea.
- **Prohibido lo que más marea:** zoom acoplado al scroll de gran amplitud, dolly-zoom (Vertigo),
  rotación de la escena completa, movimiento de fondo de pantalla completa a alta velocidad,
  cualquier cosa que mueva **>1/3 del viewport a >~500 px/s**.
- **El pico también respeta esto.** Si el reveal marea, el reveal está mal diseñado — no es que
  el usuario sea "sensible". La versión reduced-motion del pico debe seguir siendo **un momento**:
  un corte duro a la escena final, tipografía potente, y ya. Un corte también es cine (§2.4).

### 8.4 Nunca escondas contenido detrás de una animación

- **El contenido crítico se renderiza en el servidor y es visible sin JS.** Si tu H1, tus
  proyectos o tu email sólo aparecen cuando un `IntersectionObserver` dispara un `gsap.to`,
  entonces: un usuario con JS lento no ve nada, un crawler no ve nada, un lector de pantalla
  puede ver nada, y **tu LCP está en manos de tu librería de animación.**
- Regla técnica: **anima desde un estado visible hacia otro visible, o usa `clip-path`/máscara.**
  `opacity: 0` en el HTML inicial es una apuesta contra tu propio usuario.
- **Ningún efecto puede ser el elemento LCP.** El H1 real, server-rendered, es el LCP. El canvas
  entra con `next/dynamic({ ssr: false })` **después**.

### 8.5 El tiempo del usuario es sagrado

> **Toda animación que retrasa la lectura es un impuesto que le cobras al visitante.**
> Puedes cobrarlo — una vez, en el pico, y con un producto que valga el precio.
> Cobrarlo 30 veces (un fade-in por cada bloque de texto) es lo que hace que una página se
> sienta *pretenciosa* en lugar de *impresionante*. Y esa es exactamente la línea entre "wow" y
> "cheap".

Presupuesto de impuesto por página: **~1200 ms totales de espera impuesta**. El pico se lleva 900.
Te quedan 300 para todo lo demás. Administra.

### 8.6 Accesibilidad = respeto, no una casilla

- **Teclado:** todo lo que responde a hover tiene su espejo en `:focus-visible`. Si un momento del
  sitio sólo existe con mouse, para un usuario de teclado **ese momento no existe** — y para un
  usuario táctil (la mayoría) tampoco.
- **Táctil:** el cursor mágico, el botón magnético, el spotlight — **cero coste en móvil**.
  Gate con `matchMedia('(pointer: fine)')` **antes de registrar el listener**, no dentro del
  handler. Targets ≥ 44×44 px.
- **`cursor: none`** (cursor personalizado que oculta el nativo): **regresión de accesibilidad
  documentada.** No lo hagas en un portafolio que quieres que te contraten por él.
- **Lector de pantalla:** el `<canvas>` va con `aria-hidden="true"`. La narrativa visual necesita
  un equivalente textual — si tu pico "cuenta" que eres arquitecto de sistemas, **escríbelo
  también.** El diagrama tiene que existir como texto.
- **Gama media real:** el ladder de degradación (drei `PerformanceMonitor`) no es opcional.
  Mídelo en un teléfono, con throttling. **"Corre en mi 4070" no es evidencia** — y un recruiter
  con un Moto G que ve tu página a 12 fps concluye, correctamente, que no sabes optimizar.

---

## 9. EL GATE — forcing function

> **Una página NO está lista si no puedes responder estas preguntas, por escrito, PARA CADA
> EFECTO. Si un efecto no las pasa, el efecto no se implementa. Sin negociación.**

### 9.1 Las 5 preguntas (por cada efecto)

| # | Pregunta | Falla si… |
|---|---|---|
| **1** | **¿Qué emoción humana busca?** (asombro / calma / curiosidad / tensión / confianza / orgullo) | La respuesta es "se ve chévere", "es moderno", "lo vi en Awwwards". Eso no es una emoción, es una imitación. |
| **2** | **¿Qué principio lo respalda?** (awe: vastness+accommodation · claroscuro · figura-fondo · fluidez · peak-end · anticipación · un principio de Disney · Ma) | No puedes nombrar el principio. Entonces es decoración: **bórralo**. |
| **3** | **¿A qué beat narrativo pertenece?** (gancho / promesa / prueba / **giro** / cierre) | "A ninguno" o "a todos". Un efecto sin beat es ruido con GPU. |
| **4** | **¿Qué le DA al usuario?** (jerarquía, orientación, información, memoria, deleite) — no sólo qué le quita (tiempo, batería, claridad) | Sólo hay columna de "quita". Es un impuesto sin producto. |
| **5** | **¿Cuál es su fallback sin motion / sin WebGL / en gama baja?** Y ese fallback, **¿es bello por sí solo?** | El fallback es "no se ve nada". Un hueco vacío es un bug, no una degradación. |

### 9.2 Las tres leyes

> **LEY DEL PICO ÚNICO** — **Un (1)** momento signature por página. Todo lo demás **sostiene**.
> Si tienes dos candidatos, mata uno. Cinco picos = ningún pico (peak-end, §4.1).
> *Verificación:* nombra el pico en una sola frase que un humano le pueda repetir a otro humano.
> Si no sale en una frase, no existe.

> **LEY DEL FINAL** — La página debe tener un **cierre diseñado**, no un footer. El visitante
> recuerda el pico y el final; el promedio no lo recuerda nadie. Si tu último gesto es un
> `<footer>` gris, tiraste la mitad del recuerdo.

> **LEY DE LA SUSTRACCIÓN** — **Si lo quitas y no se pierde nada, sobraba.**
> Aplícalo literalmente: comenta el efecto, recarga, mira la página 30 segundos. ¿La echas de
> menos? ¿Se perdió una emoción, una jerarquía, un significado? Si no → el commit es el `git rm`.
> **La página final debe ser el resultado de haber borrado cosas, no de haberlas acumulado.**

### 9.3 Checklist binario de cierre (todos SÍ o no se entrega)

**Humano**
- [ ] Puedo nombrar EL momento en una frase repetible.
- [ ] La página tiene un cierre diseñado (no un footer).
- [ ] Hay foreshadowing del pico ≥ 30% de scroll antes de que ocurra.
- [ ] La sección anterior al pico es la más sobria de la página.
- [ ] Los 5 beats narrativos existen y los puedo enunciar sin decir "sección".
- [ ] El giro es **específico de Cristian**, no genérico ("mira, partículas").
- [ ] Cada efecto que sobrevive pasó las 5 preguntas de §9.1, por escrito.

**Percepción**
- [ ] Test de blur: veo exactamente 3 manchas jerarquizadas, no 8 iguales.
- [ ] El fondo es CAMPO (contraste interno < 1.3:1), no OBJETO.
- [ ] Una sola figura dominante por pantalla.
- [ ] ≥ 40% del hero es vacío contiguo (Ma), no padding disperso.
- [ ] Un solo ratio de escala tipográfica. Una sola familia de easing.
- [ ] Silueta: el objeto principal se reconoce en negro plano.

**Funcional (cualquier NO = no se entrega)**
- [ ] Todo el texto ≥ 4.5:1 (objetivo 7:1); texto sobre canvas tiene capa de protección.
- [ ] El scroll **no** se secuestra. Toda animación scroll-linked es reversible.
- [ ] `prefers-reduced-motion`: probado. La escena **se congela, no desaparece**, y el fallback
      del pico sigue siendo un momento.
- [ ] Parallax ≤ 12% del viewport. Cero dolly-zoom, cero rotación de escena completa.
- [ ] Ningún contenido depende de una animación para existir. H1 server-rendered = LCP.
- [ ] Impuesto total de espera ≤ ~1200 ms, con el pico llevándose la mayor parte.
- [ ] Hover ↔ `:focus-visible` en paridad. Efectos de puntero **no registrados** en táctil.
- [ ] `<canvas aria-hidden="true">` + equivalente textual de lo que narra el pico.
- [ ] **Medido en un Android real con throttling.** 60 fps o el ladder degrada solo.
- [ ] INP < 200 ms · LCP < 2.5 s · CLS < 0.1, verificados, no estimados.

---

## Apéndice A — Tabla maestra: emoción → mecanismo → parámetro

| Emoción buscada | Principio | Mecanismo | Parámetro | Fallback sin motion |
|---|---|---|---|---|
| **Asombro** | Vastness + accommodation (Keltner/Haidt) | Reveal que re-encuadra: el objeto era la puerta | Ratio de escala ≥ 8:1; dolly-in 800–1200 ms `expo.out`; **una vez** | Corte duro a la escena final, estática, bien iluminada |
| **Lujo / "caro"** | Claroscuro barroco + física plausible | Luz key dura + rim light + easing con masa | Key:fill 8:1–16:1; `cubic-bezier(0.16,1,0.3,1)`; grano 2–5% | Idéntico: el claroscuro **no necesita movimiento** |
| **Confianza / autoridad** | Fluidez de procesamiento (Reber et al.) + Suizo | Retícula, medida 62ch, un ratio, contraste alto | 16–18 px / lh 1.6 / ≥7:1 / escala 1.333 | Idéntico (no hay motion involucrado) |
| **Calma / respiro** | Figura-fondo + Ma | Fondo como campo; vacío contiguo | ≥40% vacío; fondo contraste interno <1.3:1 | Idéntico |
| **Curiosidad** | Cierre (Gestalt) + anticipación | Objeto cortado por el viewport; pregunta sin responder | Sangrado ≥15% fuera del borde | Idéntico |
| **Tensión** | Constructivismo + pacing | Una diagonal en una página ortogonal; rampa antes del pico | Una vez; 300 px de rampa | Diagonal estática (funciona igual) |
| **Vida / presencia** | Movimiento sub-umbral | Respiración ambiental, grano animado | Rotación ≤ 0.05 rad/s | Grano estático |
| **Memoria / recuerdo** | Peak-end (Kahneman) | UN pico + UN cierre | 1 de cada; pico 1.5–3 s de scroll | El cierre puede ser puramente tipográfico y sigue funcionando |

## Apéndice B — Lo que se lee como BARATO (y por qué)

| Síntoma | Por qué se percibe barato |
|---|---|
| Efectos repartidos por igual en todas las secciones | Sin pico → sin recuerdo (§4.1). Se siente "cargado" y se olvida. |
| Fondo animado que compite con el texto | Rompe figura-fondo → carga cognitiva → **baja fluidez → se juzga peor Y menos verdadero** (§3.3) |
| `linear` o `ease` (el default del navegador) | Viola la física esperada → mecánico |
| Fade-in de texto en cada scroll | Impuesto sin producto (§8.5). Grita "tengo una librería de animación". |
| Un H1 gigante sin nada pequeño al lado | Vastness sin contraste = tamaño, no escala. No produce awe. |
| Objeto 3D centrado, entero, girando solo | Cero cierre Gestalt, cero pregunta, cero control del usuario. Es un salvapantallas. |
| Glassmorphism/gradiente sin material ni grano | Se ve a Figma, no a fotografía. Falta wabi-sabi. |
| Cursor personalizado con `cursor: none` | Regresión de a11y + cero valor en el 70% táctil |
| Preloader sin nada que cargar | Impuesto puro. Insulto medible. |
| Overshoot > 10% | Lee a juguete, no a producto |
| Footer gris con 3 iconos | Tira el 50% del recuerdo (§4.1) |

---

## Fuentes

- [Keltner, D. & Haidt, J. (2003). *Approaching awe, a moral, spiritual, and aesthetic emotion*. Cognition and Emotion 17(2)](https://www.tandfonline.com/doi/abs/10.1080/02699930302297) — vastness + need for accommodation
- [Reber, R., Schwarz, N. & Winkielman, P. (2004). *Processing Fluency and Aesthetic Pleasure: Is Beauty in the Perceiver's Processing Experience?* PSPR 8(4)](https://pages.ucsd.edu/~pwinkiel/reber-schwarz-winkielman-beauty-PSPR-2004.pdf) — fluidez → belleza
- [Schwarz, N. *Of fluency, beauty, and truth*](https://dornsife.usc.edu/norbert-schwarz/wp-content/uploads/sites/231/2023/12/18_ch_Schwarz_Fluency_beauty_truth.pdf) — fluidez → juicio de verdad
- [Peak–end rule (Kahneman, Fredrickson, Schreiber & Redelmeier, 1993)](https://en.wikipedia.org/wiki/Peak%E2%80%93end_rule) · [Laws of UX](https://lawsofux.com/peak-end-rule/)
- [Meta-análisis peak-end / duration neglect (2022), OBHDP](https://www.sciencedirect.com/science/article/abs/pii/S0749597822000334) — efecto grande y robusto; duración ≈ irrelevante
- [The Science of Awe — Greater Good / Templeton white paper](https://www.templeton.org/wp-content/uploads/2018/08/Awe-White-Paper_distribution.pdf)
- Norman, D. *Emotional Design* (visceral/conductual/reflexivo) · Thomas & Johnston, *The Illusion of Life* (12 principios)

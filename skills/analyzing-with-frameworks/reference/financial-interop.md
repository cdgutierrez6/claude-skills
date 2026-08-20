# Marco 4 — Interoperabilidad financiera (Bre-B / Open Finance Colombia)

## Idea central
La fricción de pago mata conversiones. El entorno colombiano de **pagos inmediatos
interoperables (Bre-B)** y **Open Finance** permite cobrar al instante, entre cualquier
banco/billetera, vía QR o llaves, sin tarjetas ni efectivo. El checkout sin fricción es
una **palanca de negocio**, no un detalle técnico.

## Bre-B (sistema de pagos inmediatos del Banco de la República)
- **Qué es:** infraestructura que interconecta bancos y billeteras para transferencias y cobros **inmediatos (segundos), 24/7**, interoperables entre entidades.
- **Llaves:** un alias (tipo documento, celular o llave alfanumérica) que enruta el dinero a una cuenta sin tener que pedir número de cuenta + entidad. Reduce fricción y error.
- **QR interoperable:** un mismo QR sirve para pagar desde cualquier billetera/banco adherido — clave para el comercio pequeño.
- **Por qué importa:** rompe los silos (antes mover plata entre billeteras/bancos era lento o caro). Cobro instantáneo sin adquirencia de tarjeta → **menos comisiones y menos abandono**.

## Billeteras y rails locales
- **Nequi, Daviplata, dale!, Movii**, etc.: altísima penetración, incluso en economía informal y población no bancarizada tradicional.
- Tarjeta de crédito tiene baja penetración relativa → diseñar para billetera/QR, no para checkout de tarjeta.

## Open Finance Colombia
- Marco de **finanzas abiertas voluntario** (Decreto 1297 de 2022): con **consentimiento del usuario**, las entidades comparten datos financieros vía APIs.
- Habilita: **scoring alternativo** (crédito a quien no tiene historia tradicional), **conciliación automática**, **iniciación de pagos**, agregación de cuentas.

## Implicaciones de diseño (lo que un fintech senior considera)
- **Checkout embebido** en el flujo (incluso dentro del chat de WhatsApp, ligando con el Marco 3): QR dinámico o link de pago, sin redirección ni datos de tarjeta.
- **Conciliación automática** vía webhooks del proveedor de pagos; idempotencia en confirmaciones.
- **Pagos inmediatos = irreversibles:** el riesgo de fraude es en tiempo real. Hace falta antifraude, límites y verificación.
- **Cumplimiento:** KYC y **SARLAFT** (prevención de lavado), límites regulatorios por tipo de cuenta, protección de datos (Ley 1581).

## Cómo escribir el párrafo
¿La oportunidad se apoya en cobro inmediato interoperable (Bre-B/QR/billeteras)? ¿Reduce
el abandono por fricción de pago? ¿Aprovecha Open Finance para datos/scoring/conciliación?
¿El timing del despliegue de Bre-B le da ventaja ahora? ¿Qué riesgo de fraude/cumplimiento introduce?

## Pregunta guía
*"¿Cómo aprovecha esta oportunidad el checkout sin fricción (Bre-B/QR/billeteras/Open Finance) para reducir fricción de pago y ganar timing, y qué riesgo de fraude/cumplimiento debe manejar?"*

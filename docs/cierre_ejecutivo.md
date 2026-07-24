# Cierre Ejecutivo — Sobregiros en Cuentas Corrientes Embargadas

## Situación identificada

Las cuentas corrientes embargadas con saldo de sobregiro presentan un problema
de prelación en la aplicación de recursos. Cuando la cuenta recibe un crédito,
el sistema cobra primero los intereses y el capital del sobregiro (`INT_SOB` y
`CAP_SOB`), agotando el saldo disponible. Al día siguiente, la Gerencia de
Embargos ejecuta el débito manual con la transacción `006`, la cual no tiene
autorización para operar sobre el cupo de sobregiro, generando su rechazo.

El análisis del período **2026-07-15 al 2026-07-21** evidenció **95 cuentas
corrientes embargadas sobregiradas** activas, con un valor total rechazado de
**$277.964.010**, distribuido entre cinco entes legales: DIAN, UGPP,
Fiscalía Regional, Juzgado 01 Civil y Superfinanciera.

---

## Riesgos mitigados

- **Regulatorio:** El incumplimiento reiterado de órdenes de embargo expone al
  banco a sanciones de la Superfinanciera y deteriora la relación con entes
  como la DIAN y la UGPP.
- **Financiero:** La Gerencia de Depósitos asume los rechazos contra su P&G
  mediante traslados contables manuales, generando pérdidas recurrentes.
- **Operativo:** El proceso de corrección es 100% reactivo y manual, sin
  trazabilidad automática ni alertas tempranas.

---

## Solución propuesta

Se diseñó una solución en dos componentes:

1. **Medida puente (4 meses):** Implementación de una regla de prelación en el
   proceso nocturno de cierre que reserva el monto embargable antes de aplicar
   cualquier cobro de sobregiro, garantizando que la `006` siempre encuentre
   saldo disponible.

2. **Monitor diario:** Producto de datos en Python que clasifica diariamente
   las cuentas en riesgo (`ALERTA` / `NORMAL`), permite a la Gerencia de
   Embargos actuar de forma proactiva y genera reportes automáticos en CSV.

---

## Beneficios esperados

| Beneficio | Impacto |
|---|---|
| Cumplimiento regulatorio | Eliminación del riesgo de sanciones por incumplimiento de órdenes de embargo |
| Reducción de pérdidas | Disminución de traslados contables CxC contra P&G |
| Automatización | Reemplazo del proceso manual y reactivo por monitoreo proactivo diario |
| Trazabilidad | Registro automático de alertas con historial auditable |

---

## Recomendación

Priorizar la implementación de la regla de prelación como medida puente en un
horizonte de **4 meses**, en paralelo con la operación del monitor diario como
insumo para la Gerencia de Embargos. Esto reduce la exposición regulatoria y
financiera mientras se desarrolla la solución definitiva en el sistema Core.
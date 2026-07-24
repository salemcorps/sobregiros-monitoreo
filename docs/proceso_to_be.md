# Proceso To Be — Cuentas corrientes embargadas con sobregiro

## Descripción de la solución

Se propone implementar una **regla de prelación de recursos** en el proceso nocturno de cierre de depósitos. Antes de aplicar cualquier cobro de sobregiro, el sistema debe verificar si la cuenta tiene un embargo activo con saldo pendiente. Si existe, reserva primero el monto embargable y solo cobra el sobregiro sobre el remanente.

Como medida transitoria (antes de la solución definitiva en 3 años), se implementa adicionalmente un **producto de datos de monitoreo diario** que identifica proactivamente las cuentas en riesgo.

---

## Cambios respecto al proceso actual

| Aspecto | As Is (actual) | To Be (propuesto) |
|---|---|---|
| Secuencia de aplicación | Sobregiro → Embargo | Embargo → Sobregiro |
| Detección de rechazos | Reactiva (día siguiente) | Proactiva (mismo día) |
| Gestión | Manual por Gerencia de Depósitos | Automatizada por el sistema |
| Trazabilidad | Sin registro automático | Log diario de alertas |
| Riesgo regulatorio | Alto | Mitigado |

---

## Prelación de recursos propuesta

Cuando una cuenta corriente embargada y sobregirada recibe un crédito:

| Prioridad | Aplicación | Justificación |
|---|---|---|
| 1 | Embargo (`006`) | Obligación legal — prevalece sobre cualquier cobro interno |
| 2 | Intereses de sobregiro (`INT_SOB`) | Solo si hay remanente tras cubrir el embargo |
| 3 | Capital de sobregiro (`CAP_SOB`) | Solo si hay remanente adicional |

---

## Diagrama del proceso propuesto

```mermaid
flowchart TD
    A([Orden de embargo judicial]) --> B

    B["🔵 Sistema Core\nRegistra embargo activo en la cuenta"]
    B --> C["Cuenta recibe transacción crédito"]
    C --> D{¿Cuenta tiene embargo\nactivo con saldo pendiente?}

    D -- No --> E["🔵 Sistema Core\nProceso normal de cierre\nCobra sobregiro si aplica"]
    E --> Z([Fin del proceso])

    D -- Sí --> F{¿Cuenta sobregirada?}

    F -- No --> G["🔵 Sistema Core\nReserva monto embargable\nBloquea saldo para trx 006"]
    F -- Sí --> H["🔵 Sistema Core\n⭐ NUEVO: Verifica remanente\ntras reservar embargo"]

    H --> I{¿Crédito ≥ valor\npendiente embargo?}

    I -- Sí --> J["🔵 Sistema Core\n1. Reserva embargo\n2. Cobra INT_SOB con remanente\n3. Cobra CAP_SOB con remanente"]
    I -- No --> K["🔵 Sistema Core\n1. Reserva crédito completo para embargo\n2. Difiere cobro de sobregiro"]

    G --> L
    J --> L
    K --> L

    L["🟣 Gerencia de Embargos\nEjecuta trx 006 sobre saldo reservado"]
    L --> M{¿Trx 006 aplicada\nexitosamente?}

    M -- Sí --> N["🟢 Ente Legal\nAbono de recursos vía Sebra"]
    N --> O{¿Embargo cubierto?}
    O -- Sí --> P([Levantamiento del embargo])
    O -- No --> C

    M -- No --> Q["📊 Monitor diario\nRegistra alerta — genera reporte"]
    Q --> R["🟡 Gerencia de Depósitos\nGestión excepcional\n(casos residuales mínimos)"]

    style L fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
    style Q fill:#fef3c7,stroke:#f59e0b,color:#78350f
    style H fill:#ede9fe,stroke:#7c3aed,color:#3b0764
```

---

## Componentes de la solución

### 1. Regla de prelación (cambio en Sistema Core)

Modificación en el proceso nocturno de cierre de depósitos para evaluar, antes de cualquier cobro de sobregiro, si la cuenta tiene embargo activo. Esta es la **solución estructural** y requiere desarrollo en el sistema Core con un horizonte de implementación de 4 meses como medida puente.

### 2. Monitor diario (producto de datos)

Script Python que se ejecuta cada día y genera un reporte con las cuentas en riesgo. Permite a la Gerencia de Embargos actuar de forma proactiva antes de ejecutar la `006`.

```
Entradas:   sobregiros.db (snapshot diario)
Proceso:    Clasificación ALERTA / NORMAL por cuenta
Salidas:    Reporte CSV con cuentas en riesgo del día
```

---

## Roadmap de implementación

```mermaid
gantt
    title Roadmap solución — Sobregiros en cuentas embargadas
    dateFormat  YYYY-MM-DD
    section Medida puente
    Producto de datos monitor diario     :done,    m1, 2026-07-01, 30d
    Ajuste regla prelación Core          :active,  m2, 2026-08-01, 60d
    Pruebas integradas                   :         m3, 2026-10-01, 30d
    section Solución definitiva
    Diseño técnico solución permanente   :         m4, 2026-11-01, 90d
    Desarrollo e implementación          :         m5, 2027-02-01, 365d
```

---

## Riesgos residuales mitigados

| Riesgo | As Is | To Be |
|---|---|---|
| Incumplimiento regulatorio | Alto | Bajo — embargo siempre tiene prioridad |
| Pérdida financiera P&G | Recurrente | Excepcional — solo casos residuales |
| Gestión manual | 100% de rechazos | Solo casos no cubiertos por la regla |
| Trazabilidad | Nula | Automática vía monitor diario |
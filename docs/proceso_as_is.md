# Proceso As Is — Cuentas corrientes embargadas con sobregiro

## Descripción del problema

Cuando una cuenta corriente embargada recibe un crédito y tiene saldo de sobregiro pendiente, el sistema aplica primero los intereses (`INT_SOB`) y el capital (`CAP_SOB`) del sobregiro, agotando el saldo disponible. Al día siguiente, la Gerencia de Embargos ejecuta el débito manual con la transacción `006`, la cual **no tiene autorización para operar sobre el cupo de sobregiro**, generando su rechazo.

Esto incumple la prelación legal que establece que las obligaciones de embargo deben atenderse antes que cualquier cobro interno.

---

## Áreas participantes

| Área | Rol en el proceso |
|---|---|
| Ente legal | Emite la orden de embargo (DIAN, UGPP, Juzgados) |
| Sistema Core | Bloquea el cupo de sobregiro y aplica cobros automáticos |
| Gerencia de Embargos | Ejecuta el débito manual `006` al día siguiente |
| Gerencia de Depósitos | Asume el rechazo mediante traslado contable CxC |

---

## Diagrama del proceso actual

```mermaid
flowchart TD
    A([Orden de embargo judicial]) --> B

    B["🔵 Sistema Core\nBloquea cupo de sobregiro"]
    B --> C["Cuenta recibe transacción crédito"]
    C --> D{¿Cuenta sobregirada?}

    D -- No --> E["🔵 Sistema Core\nBloquea saldo disponible"]
    D -- Sí --> F["🔵 Sistema Core\nCobra intereses de sobregiro\n(INT_SOB)"]
    F --> G["🔵 Sistema Core\nAmortiza capital de sobregiro\n(CAP_SOB)"]
    G --> H

    E --> H["🟣 Gerencia de Embargos\nDía siguiente: débito manual trx 006"]

    H --> I{¿Saldo ≥ valor embargo?}

    I -- Sí --> J["🟢 Ente Legal\nAbono de recursos vía Sebra"]
    J --> K{¿Embargo cubierto?}
    K -- Sí --> L([Levantamiento del embargo])
    K -- No --> C

    I -- No --> M["⚠ Trx 006 RECHAZADA\nNo autorizada para usar cupo de sobregiro"]
    M --> N["🟡 Gerencia de Depósitos\nTraslado contable CxC\nGestión manual o asume P&G"]

    style M fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
    style N fill:#fef3c7,stroke:#f59e0b,color:#78350f
```

---

## Punto crítico de fallo

El problema ocurre en la **secuencia de aplicación de recursos** cuando la cuenta está sobregirada:

| Orden actual (incorrecta) | Orden correcta (según prelación legal) |
|---|---|
| 1. Intereses de sobregiro (`INT_SOB`) | 1. Embargo (`006`) |
| 2. Capital de sobregiro (`CAP_SOB`) | 2. Intereses de sobregiro (`INT_SOB`) |
| 3. Embargo (`006`) — **rechazado** | 3. Capital de sobregiro (`CAP_SOB`) |

---

## Riesgos identificados

- **Regulatorio:** Incumplimiento de órdenes judiciales y administrativas frente a entes como DIAN, UGPP y juzgados. Riesgo de sanciones de la Superfinanciera.
- **Financiero:** La Gerencia de Depósitos debe asumir el valor rechazado contra su P&G mediante traslado contable CxC.
- **Operativo:** El proceso de corrección es 100% manual y reactivo, sin trazabilidad automática.
- **Reputacional:** Incumplimiento reiterado puede deteriorar la relación con entes legales y reguladores.
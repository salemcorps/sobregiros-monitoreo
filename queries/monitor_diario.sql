-- =============================================================
-- Monitor diario: cuentas corrientes embargadas con sobregiro
-- Detecta casos donde la trx 006 puede ser rechazada
--
-- Parámetro: reemplaza :fecha con la fecha a analizar (YYYY-MM-DD)
-- Ejemplo:   '2026-07-21'
-- =============================================================

WITH creditos_dia AS (
    -- Agrupa los movimientos del día por cuenta
    -- y separa los montos según su tipo de aplicación
    SELECT
        m.num_cta,
        m.fecha_movimiento,

        -- Recursos que ingresaron como embargables
        SUM(m.valor_movimiento) FILTER (
            WHERE m.grupo_movimiento = 'RECURSO_EMBARGABLE'
        ) AS valor_credito_embargable,

        -- Lo que el sistema cobró como intereses de sobregiro
        SUM(m.valor_movimiento) FILTER (
            WHERE m.tipo_aplicacion = 'INTERES'
        ) AS aplicado_interes_sob,

        -- Lo que el sistema cobró como capital de sobregiro
        SUM(m.valor_movimiento) FILTER (
            WHERE m.tipo_aplicacion = 'CAPITAL'
        ) AS aplicado_capital_sob,

        -- Lo que efectivamente se aplicó al embargo
        SUM(m.valor_movimiento) FILTER (
            WHERE m.tipo_aplicacion = 'EMBARGO'
        ) AS aplicado_embargo,

        -- Valor total de movimientos rechazados
        SUM(m.valor_movimiento) FILTER (
            WHERE m.estado_movimiento = 'RECHAZADO'
        ) AS valor_rechazado

    FROM movimientos m
    WHERE m.fecha_movimiento = :fecha
    GROUP BY m.num_cta, m.fecha_movimiento
)

SELECT
    -- Datos de la cuenta
    c.num_cta,
    c.sld_actual,
    c.cupo_sobregiro,
    c.dias_sobregiro,
    c.estado,

    -- Datos del embargo
    e.ente_legal,
    e.valor_embargo,
    e.saldo_pendiente_embargo,
    e.estado_embargo,

    -- Movimientos del día
    cd.fecha_movimiento,
    cd.valor_credito_embargable,
    cd.aplicado_interes_sob,
    cd.aplicado_capital_sob,
    cd.aplicado_embargo,
    cd.valor_rechazado,

    -- Clasificación de alerta
    -- ALERTA: se cobró sobregiro sin aplicar embargo → trx 006 en riesgo
    CASE
        WHEN (
            (COALESCE(cd.aplicado_interes_sob, 0) > 0
             OR COALESCE(cd.aplicado_capital_sob, 0) > 0)
            AND COALESCE(cd.aplicado_embargo, 0) = 0
        ) THEN 'ALERTA'
        ELSE 'NORMAL'
    END AS marca_alerta

FROM cuentas c
JOIN embargos e
    ON c.num_cta = e.num_cta
JOIN creditos_dia cd
    ON c.num_cta = cd.num_cta

WHERE c.cod_aplicacion = 'CTE'       -- Solo cuentas corrientes
  AND c.estado       = 'EMBARGADA'   -- Con embargo vigente
  AND c.sld_actual   < 0             -- Sobregiradas
  AND e.estado_embargo = 'ACTIVO'    -- Embargo activo con saldo pendiente

ORDER BY
    marca_alerta DESC,               -- Alertas primero
    cd.valor_credito_embargable DESC -- Mayor valor primero
;

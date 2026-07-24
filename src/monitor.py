import pandas as pd
from database import DatabaseConnector
from clasificador import ClasificadorCasos


class SobregirosMonitor:
    """
    Monitorea diariamente las cuentas corrientes embargadas con sobregiro
    para identificar casos donde la trx 006 puede ser rechazada.
    """

    SQL_MONITOR = """
        WITH creditos_dia AS (
            SELECT
                m.num_cta,
                m.fecha_movimiento,
                SUM(m.valor_movimiento) FILTER (
                    WHERE m.grupo_movimiento = 'RECURSO_EMBARGABLE'
                ) AS valor_credito_embargable,
                SUM(m.valor_movimiento) FILTER (
                    WHERE m.tipo_aplicacion = 'INTERES'
                ) AS aplicado_interes_sob,
                SUM(m.valor_movimiento) FILTER (
                    WHERE m.tipo_aplicacion = 'CAPITAL'
                ) AS aplicado_capital_sob,
                SUM(m.valor_movimiento) FILTER (
                    WHERE m.tipo_aplicacion = 'EMBARGO'
                ) AS aplicado_embargo,
                SUM(m.valor_movimiento) FILTER (
                    WHERE m.estado_movimiento = 'RECHAZADO'
                ) AS valor_rechazado
            FROM movimientos m
            WHERE m.fecha_movimiento = ?
            GROUP BY m.num_cta, m.fecha_movimiento
        )
        SELECT
            c.num_cta,
            c.sld_actual,
            c.cupo_sobregiro,
            c.dias_sobregiro,
            c.estado,
            e.ente_legal,
            e.valor_embargo,
            e.saldo_pendiente_embargo,
            e.estado_embargo,
            cd.fecha_movimiento,
            cd.valor_credito_embargable,
            cd.aplicado_interes_sob,
            cd.aplicado_capital_sob,
            cd.aplicado_embargo,
            cd.valor_rechazado
        FROM cuentas c
        JOIN embargos e ON c.num_cta = e.num_cta
        JOIN creditos_dia cd ON c.num_cta = cd.num_cta
        WHERE c.cod_aplicacion = 'CTE'
          AND c.estado = 'EMBARGADA'
          AND c.sld_actual < 0
          AND e.estado_embargo = 'ACTIVO'
        ORDER BY cd.valor_credito_embargable DESC
    """

    def __init__(self, db_connector: DatabaseConnector):
        self.db = db_connector
        self.clasificador = ClasificadorCasos()
        self._resultados: pd.DataFrame = pd.DataFrame()

    def ejecutar(self, fecha: str) -> pd.DataFrame:
        """
        Ejecuta el monitoreo para una fecha dada (formato YYYY-MM-DD).
        Retorna un DataFrame con los casos clasificados.
        """
        datos = self.db.ejecutar_query(self.SQL_MONITOR, params=(fecha,))

        if datos.empty:
            print(f"Sin casos para la fecha {fecha}.")
            return datos

        self._resultados = self.clasificador.clasificar(datos)
        return self._resultados

    def resumen(self) -> dict:
        """Retorna un resumen con los indicadores clave del monitoreo."""
        if self._resultados.empty:
            return {}

        df = self._resultados
        return {
            "total_cuentas": len(df),
            "cuentas_alerta": len(df[df["marca_alerta"] == "ALERTA"]),
            "cuentas_normal": len(df[df["marca_alerta"] == "NORMAL"]),
            "valor_total_en_riesgo": df.loc[
                df["marca_alerta"] == "ALERTA", "valor_credito_embargable"
            ].sum(),
            "valor_total_rechazado": df["valor_rechazado"].sum(),
            "entes_legales": df["ente_legal"].unique().tolist(),
        }

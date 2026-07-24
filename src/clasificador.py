import pandas as pd


class ClasificadorCasos:
    """
    Clasifica cada cuenta como ALERTA o NORMAL según la prelación
    de recursos aplicada en el día analizado.

    ALERTA: se cobró sobregiro (intereses o capital) antes del embargo
            y no se registró aplicación al embargo — trx 006 en riesgo.
    NORMAL: el embargo fue cubierto o no hubo cobro de sobregiro.
    """

    def clasificar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega la columna marca_alerta al DataFrame."""
        df = df.copy()
        df["marca_alerta"] = df.apply(self._evaluar_fila, axis=1)
        return df

    def _evaluar_fila(self, fila: pd.Series) -> str:
        cobro_sobregiro = (
            (fila.get("aplicado_interes_sob") or 0) > 0
            or (fila.get("aplicado_capital_sob") or 0) > 0
        )
        embargo_aplicado = (fila.get("aplicado_embargo") or 0) > 0

        if cobro_sobregiro and not embargo_aplicado:
            return "ALERTA"
        return "NORMAL"

    def estadisticas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Retorna conteo y valor en riesgo agrupado por ente legal."""
        alertas = df[df["marca_alerta"] == "ALERTA"]
        return (
            alertas.groupby("ente_legal")
            .agg(
                cuentas_en_alerta=("num_cta", "count"),
                valor_en_riesgo=("valor_credito_embargable", "sum"),
                valor_rechazado=("valor_rechazado", "sum"),
            )
            .reset_index()
            .sort_values("valor_en_riesgo", ascending=False)
        )

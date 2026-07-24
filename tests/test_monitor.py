import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clasificador import ClasificadorCasos


class TestClasificadorCasos:
    """Pruebas unitarias para la lógica de clasificación de alertas."""

    def setup_method(self):
        self.clasificador = ClasificadorCasos()

    def _crear_df(self, filas: list) -> pd.DataFrame:
        columnas = [
            "num_cta", "aplicado_interes_sob",
            "aplicado_capital_sob", "aplicado_embargo",
        ]
        return pd.DataFrame(filas, columns=columnas)

    def test_alerta_cuando_cobra_interes_sin_embargo(self):
        """Si se cobra interés de sobregiro y no se aplica embargo → ALERTA."""
        df = self._crear_df([("001", 50000, 0, 0)])
        resultado = self.clasificador.clasificar(df)
        assert resultado.iloc[0]["marca_alerta"] == "ALERTA"

    def test_alerta_cuando_cobra_capital_sin_embargo(self):
        """Si se cobra capital de sobregiro y no se aplica embargo → ALERTA."""
        df = self._crear_df([("002", 0, 100000, 0)])
        resultado = self.clasificador.clasificar(df)
        assert resultado.iloc[0]["marca_alerta"] == "ALERTA"

    def test_normal_cuando_embargo_fue_aplicado(self):
        """Si el embargo fue aplicado correctamente → NORMAL."""
        df = self._crear_df([("003", 0, 0, 200000)])
        resultado = self.clasificador.clasificar(df)
        assert resultado.iloc[0]["marca_alerta"] == "NORMAL"

    def test_normal_cuando_no_hay_cobros(self):
        """Si no hubo cobros de ningún tipo → NORMAL."""
        df = self._crear_df([("004", 0, 0, 0)])
        resultado = self.clasificador.clasificar(df)
        assert resultado.iloc[0]["marca_alerta"] == "NORMAL"

    def test_normal_cuando_valores_son_none(self):
        """Si los valores son None (sin movimientos) → NORMAL, no error."""
        df = self._crear_df([("005", None, None, None)])
        resultado = self.clasificador.clasificar(df)
        assert resultado.iloc[0]["marca_alerta"] == "NORMAL"

    def test_multiples_cuentas(self):
        """Clasifica correctamente un lote de cuentas mixtas."""
        df = self._crear_df([
            ("001", 50000, 0,      0),       # ALERTA
            ("002", 0,     100000, 0),       # ALERTA
            ("003", 0,     0,      200000),  # NORMAL
            ("004", 0,     0,      0),       # NORMAL
        ])
        resultado = self.clasificador.clasificar(df)
        assert list(resultado["marca_alerta"]) == ["ALERTA", "ALERTA", "NORMAL", "NORMAL"]

    def test_estadisticas_por_ente_legal(self):
        """Las estadísticas agrupan correctamente por ente legal."""
        df = pd.DataFrame({
            "num_cta": ["001", "002", "003"],
            "ente_legal": ["DIAN", "DIAN", "UGPP"],
            "aplicado_interes_sob": [50000, 30000, 0],
            "aplicado_capital_sob": [0, 0, 0],
            "aplicado_embargo": [0, 0, 200000],
            "valor_credito_embargable": [50000, 30000, 200000],
            "valor_rechazado": [50000, 30000, 0],
            "marca_alerta": ["ALERTA", "ALERTA", "NORMAL"],
        })
        stats = self.clasificador.estadisticas(df)
        assert len(stats) == 1                          # Solo DIAN tiene alertas
        assert stats.iloc[0]["ente_legal"] == "DIAN"
        assert stats.iloc[0]["cuentas_en_alerta"] == 2

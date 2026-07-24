import pandas as pd
from pathlib import Path
from datetime import datetime


class GeneradorReporte:
    """Exporta los resultados del monitoreo a archivos CSV."""

    def __init__(self, directorio_salida: str = "reports"):
        self.directorio = Path(directorio_salida)
        self.directorio.mkdir(exist_ok=True)

    def exportar_csv(self, df: pd.DataFrame, fecha: str) -> Path:
        """
        Exporta el DataFrame completo a CSV.
        Retorna la ruta del archivo generado.
        """
        nombre = f"monitor_sobregiros_{fecha}.csv"
        ruta = self.directorio / nombre
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"Reporte exportado: {ruta}")
        return ruta

    def exportar_alertas(self, df: pd.DataFrame, fecha: str) -> Path:
        """
        Exporta solo las cuentas en ALERTA a un CSV independiente.
        Retorna la ruta del archivo generado.
        """
        alertas = df[df["marca_alerta"] == "ALERTA"].copy()
        nombre = f"alertas_sobregiros_{fecha}.csv"
        ruta = self.directorio / nombre
        alertas.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"Alertas exportadas ({len(alertas)} casos): {ruta}")
        return ruta

    def imprimir_resumen(self, resumen: dict) -> None:
        """Imprime el resumen del monitoreo en consola."""
        separador = "=" * 50
        print(f"\n{separador}")
        print("  RESUMEN MONITOR DIARIO — SOBREGIROS")
        print(separador)
        print(f"  Total cuentas analizadas : {resumen.get('total_cuentas', 0)}")
        print(f"  Cuentas en ALERTA        : {resumen.get('cuentas_alerta', 0)}")
        print(f"  Cuentas NORMAL           : {resumen.get('cuentas_normal', 0)}")
        print(f"  Valor en riesgo          : ${resumen.get('valor_total_en_riesgo', 0):,.0f}")
        print(f"  Valor rechazado          : ${resumen.get('valor_total_rechazado', 0):,.0f}")
        entes = resumen.get("entes_legales", [])
        print(f"  Entes legales activos    : {', '.join(entes) if entes else 'Ninguno'}")
        print(separador + "\n")

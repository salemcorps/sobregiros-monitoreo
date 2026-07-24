"""
Punto de entrada del monitor diario de sobregiros en cuentas embargadas.

Uso:
    python main.py                     # Usa la última fecha disponible en la BD
    python main.py --fecha 2026-07-21  # Ejecuta para una fecha específica
"""

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import DatabaseConnector
from monitor import SobregirosMonitor
from reporte import GeneradorReporte


def obtener_ultima_fecha(db_path: str) -> str:
    """Retorna la fecha más reciente disponible en la tabla movimientos."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(fecha_movimiento) FROM movimientos;")
    fecha = cursor.fetchone()[0]
    conn.close()
    return fecha


def main():
    parser = argparse.ArgumentParser(
        description="Monitor diario de sobregiros en cuentas corrientes embargadas."
    )
    parser.add_argument(
        "--fecha",
        type=str,
        default=None,
        help="Fecha a analizar en formato YYYY-MM-DD (por defecto: última fecha en BD)",
    )
    args = parser.parse_args()

    db_path = "data/sobregiros.db"
    fecha = args.fecha or obtener_ultima_fecha(db_path)
    print(f"\nEjecutando monitor para la fecha: {fecha}")

    with DatabaseConnector(db_path) as db:
        monitor = SobregirosMonitor(db)
        resultados = monitor.ejecutar(fecha)

        if resultados.empty:
            print("No se encontraron casos para procesar.")
            return

        resumen = monitor.resumen()

        reporte = GeneradorReporte()
        reporte.imprimir_resumen(resumen)
        reporte.exportar_csv(resultados, fecha)
        reporte.exportar_alertas(resultados, fecha)


if __name__ == "__main__":
    main()

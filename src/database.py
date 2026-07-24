import sqlite3
import pandas as pd
from pathlib import Path


class DatabaseConnector:
    """Gestiona la conexión y consultas a la base de datos SQLite."""

    def __init__(self, db_path: str = "data/sobregiros.db"):
        self.db_path = Path(db_path)
        self._connection = None

    def conectar(self) -> None:
        """Abre la conexión a la base de datos."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row

    def desconectar(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def ejecutar_query(self, sql: str, params: tuple = ()) -> pd.DataFrame:
        """Ejecuta una consulta SQL y retorna un DataFrame."""
        if not self._connection:
            raise ConnectionError("No hay conexión activa. Llama a conectar() primero.")
        return pd.read_sql_query(sql, self._connection, params=params)

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()

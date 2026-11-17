"""Muestra la consulta del Data Mart local ya generado."""
import sqlite3
import pandas as pd
from src.preparacion_datos import ROOT

if __name__ == "__main__":
    ruta = ROOT / "data/processed/datamart_energia.sqlite"
    if not ruta.exists():
        raise FileNotFoundError("Primero ejecuta: python -m src.ejecutar_proyecto")
    # Abrir en modo lectura evita crear por accidente una base vacía.
    with sqlite3.connect(ruta.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        consulta = (ROOT / "sql/03_consultar_cargas.sql").read_text(encoding="utf-8")
        print(pd.read_sql_query(consulta, conn).round(3).to_string(index=False))

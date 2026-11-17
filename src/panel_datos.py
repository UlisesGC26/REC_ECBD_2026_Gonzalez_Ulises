"""Consultas y predicciones para el panel; no reentrena ni cambia el original."""
from pathlib import Path
import json
import sqlite3

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENTRADAS = [f"X{i}" for i in range(1, 9)]
GEOMETRIA = ENTRADAS[:5]
NOMBRES = {
    "X1": "Compacidad relativa", "X2": "Área de superficie",
    "X3": "Área de muros", "X4": "Área de techo", "X5": "Altura total",
    "X6": "Orientación (código)", "X7": "Acristalamiento",
    "X8": "Distribución del cristal (código)",
    "Y1": "Calefacción", "Y2": "Refrigeración",
    "id_registro": "Registro", "grupo_geometria": "Geometría",
    "clase_calefaccion": "Clase de calefacción",
}
ARCHIVOS = [
    "data/processed/eficiencia_energetica_procesada.csv",
    "data/processed/predicciones_prueba.csv", "data/processed/division_modelos.csv",
    "data/processed/datamart_energia.sqlite", "docs/resultados_modelos.json",
    "docs/reporte_calidad_datos.json", "docs/metricas_regresion.csv",
    "docs/metricas_clasificacion.csv", "modelos/modelo_regresion_cargas.joblib",
    "modelos/modelo_clasificacion_calefaccion.joblib",
]


def archivos_faltantes():
    return [nombre for nombre in ARCHIVOS if not (ROOT / nombre).is_file()]


def firma_archivos():
    """Invalida la caché de la interfaz si se vuelve a ejecutar el proyecto."""
    return tuple((n, (ROOT / n).stat().st_mtime_ns) for n in ARCHIVOS)


def cargar_resultados():
    def csv(nombre):
        return pd.read_csv(ROOT / nombre)
    def js(nombre):
        return json.loads((ROOT / nombre).read_text(encoding="utf-8"))
    return {
        "datos": csv(ARCHIVOS[0]), "prueba": csv(ARCHIVOS[1]),
        "division": csv(ARCHIVOS[2]), "modelos": js("docs/resultados_modelos.json"),
        "calidad": js("docs/reporte_calidad_datos.json"),
        "regresion": csv("docs/metricas_regresion.csv"),
        "clasificacion": csv("docs/metricas_clasificacion.csv"),
    }


def cargar_modelos():
    return (joblib.load(ROOT / "modelos/modelo_regresion_cargas.joblib"),
            joblib.load(ROOT / "modelos/modelo_clasificacion_calefaccion.joblib"))


def filtrar(df, alturas, orientaciones, cristales):
    return df.loc[df.X5.isin(alturas) & df.X6.isin(orientaciones)
                  & df.X7.isin(cristales)].copy()


def resumen_configuraciones(df):
    return df.groupby(["X1", "X5"], as_index=False).agg(
        registros=("Y1", "size"), Y1=("Y1", "mean"), Y2=("Y2", "mean"),
        Y1_min=("Y1", "min"), Y1_max=("Y1", "max"),
        Y2_min=("Y2", "min"), Y2_max=("Y2", "max"))


def obtener_caso(df, geometria, orientacion, cristal, distribucion):
    casos = df.loc[(df.grupo_geometria == geometria) & (df.X6 == orientacion)
                   & np.isclose(df.X7, cristal) & (df.X8 == distribucion)]
    if len(casos) != 1:
        raise ValueError("Selecciona una combinación presente en el dataset.")
    return casos.iloc[[0]].copy()


def predecir_caso(caso, reg, cls):
    pred = reg.predict(caso[ENTRADAS])[0]
    clase = cls.predict(caso[ENTRADAS])[0]
    return {"Y1": float(pred[0]), "Y2": float(pred[1]), "clase": str(clase)}


CONSULTAS = {
    "Cargas por compacidad y altura": """SELECT g.X1 AS compacidad, g.X5 AS altura,
        COUNT(*) AS registros, AVG(h.Y1) AS calefaccion_media,
        AVG(h.Y2) AS refrigeracion_media FROM hecho_simulacion h
        JOIN dim_geometria g ON g.id_geometria=h.id_geometria
        GROUP BY g.X1,g.X5 ORDER BY g.X1""",
    "Cargas por orientación": """SELECT id_orientacion AS orientacion,
        COUNT(*) AS registros, AVG(Y1) AS calefaccion_media,
        AVG(Y2) AS refrigeracion_media FROM hecho_simulacion
        GROUP BY id_orientacion ORDER BY id_orientacion""",
    "Cargas por acristalamiento": """SELECT a.X7 AS acristalamiento,
        COUNT(*) AS registros, AVG(h.Y1) AS calefaccion_media,
        AVG(h.Y2) AS refrigeracion_media FROM hecho_simulacion h
        JOIN dim_acristalamiento a ON a.id_acristalamiento=h.id_acristalamiento
        GROUP BY a.X7 ORDER BY a.X7""",
}


def consultar_datamart(nombre):
    base = ROOT / "data/processed/datamart_energia.sqlite"
    with sqlite3.connect(base.as_uri() + "?mode=ro", uri=True) as conn:
        return pd.read_sql_query(CONSULTAS[nombre], conn)

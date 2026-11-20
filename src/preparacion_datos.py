"""Carga, valida y prepara Energy Efficiency sin modificar el archivo original."""
from pathlib import Path
import hashlib
import json
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ENTRADAS = [f"X{i}" for i in range(1, 9)]
OBJETIVOS = ["Y1", "Y2"]
GEOMETRIA = ["X1", "X2", "X3", "X4", "X5"]
# Regla fija para practicar clasificación. No es una norma de eficiencia.
UMBRAL_CALOR = 25.0


def guardar_json(ruta, contenido):
    Path(ruta).write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")


def preparar():
    for carpeta in ["data/processed", "docs/figuras", "sql", "modelos", "dashboard"]:
        (ROOT / carpeta).mkdir(parents=True, exist_ok=True)
    original = ROOT / "data/raw/ENB2012_data.xlsx"
    firma = hashlib.sha256(original.read_bytes()).hexdigest()
    bruto = pd.read_excel(original)
    columnas = ENTRADAS + OBJETIVOS
    if bruto.columns.tolist() != columnas:
        raise ValueError("El archivo no tiene las columnas X1-X8, Y1 y Y2 esperadas.")
    df = bruto.copy()
    for columna in columnas:
        df[columna] = pd.to_numeric(df[columna], errors="raise")
    if df.isna().any().any() or not np.isfinite(df.to_numpy()).all():
        raise ValueError("Hay valores faltantes o no finitos. Revisar antes de continuar.")
    if df.duplicated(ENTRADAS).any():
        raise ValueError("Hay entradas repetidas. Revisar su procedencia antes de eliminarlas.")
    if not df.X6.isin([2, 3, 4, 5]).all() or not df.X8.isin(range(6)).all():
        raise ValueError("Se encontraron códigos de categorías inesperados.")
    if not (df[["X1", "X2", "X3", "X4", "X5", "Y1", "Y2"]] > 0).all().all():
        raise ValueError("Se encontraron valores no positivos inesperados.")
    if not df.X7.between(0, 1).all():
        raise ValueError("Revisar el rango de acristalamiento.")
    df[["X6", "X8"]] = df[["X6", "X8"]].astype(int)
    df.insert(0, "id_registro", range(1, len(df) + 1))
    # El conjunto UCI no trae tiempo. Se crea un calendario sintético diario para
    # practicar DimTime y un corte temporal; no representa mediciones reales.
    df["fecha_simulada"] = pd.date_range("2025-01-01", periods=len(df), freq="D")
    df["grupo_geometria"] = df.groupby(GEOMETRIA, sort=True).ngroup() + 1
    df["clase_calefaccion"] = np.where(df.Y1 >= UMBRAL_CALOR, "alta", "baja")
    destino = ROOT / "data/processed"
    df.to_csv(destino / "eficiencia_energetica_procesada.csv", index=False)

    calidad = {
        "filas_originales": len(bruto), "filas_procesadas": len(df),
        "columnas_originales": len(columnas), "entradas": len(ENTRADAS), "objetivos": 2,
        "faltantes": int(bruto.isna().sum().sum()),
        "duplicados_completos": int(bruto.duplicated().sum()),
        "duplicados_entradas": int(bruto.duplicated(ENTRADAS).sum()),
        "filas_eliminadas": 0, "valores_imputados": 0,
        "geometrias": int(df.grupo_geometria.nunique()),
        "sha256_original": firma,
        "compacidades_con_ambas_alturas": int((df.groupby("X1").X5.nunique() > 1).sum()),
        "umbral_clasificacion": UMBRAL_CALOR,
        "regla_clasificacion": "alta si Y1 >= 25; baja si Y1 < 25. Regla didáctica, no normativa.",
        "unidades_cargas": "Escala original. La ficha UCI consultada no declara unidades.",
        "tiempo": "Fecha sintética diaria 2025-01-01 a 2027-02-07; creada para ETL y DimTime, no observación real.",
    }
    guardar_json(ROOT / "docs/reporte_calidad_datos.json", calidad)
    df[columnas].describe().T.to_csv(destino / "estadistica_descriptiva.csv", index_label="variable")
    resumen = df.groupby(["X1", "X5"], as_index=False).agg(
        registros=("Y1", "size"), calefaccion_media=("Y1", "mean"),
        calefaccion_mediana=("Y1", "median"), calefaccion_desviacion=("Y1", "std"),
        refrigeracion_media=("Y2", "mean"), refrigeracion_mediana=("Y2", "median"),
        refrigeracion_desviacion=("Y2", "std"))
    resumen.to_csv(destino / "resumen_compacidad_altura.csv", index=False)
    df.groupby("X5").agg(
        registros=("Y1", "size"), calefaccion_media=("Y1", "mean"),
        calefaccion_mediana=("Y1", "median"), calefaccion_desviacion=("Y1", "std"),
        refrigeracion_media=("Y2", "mean"), refrigeracion_mediana=("Y2", "median"),
        refrigeracion_desviacion=("Y2", "std")).to_csv(destino / "resumen_altura.csv")
    crear_graficas(df, resumen)
    crear_datamart(df)
    assert hashlib.sha256(original.read_bytes()).hexdigest() == firma
    print(f"Preparación terminada: {len(df)} registros, 8 entradas y 2 objetivos.")
    print("Faltantes: 0. Duplicados: 0. No se eliminaron ni imputaron datos.")
    print("Compacidad y altura: no existen compacidades compartidas por ambas alturas.")
    print("SQLite complementario validado. Para el modelo estrella en SQL Server: python -m src.etl_sqlserver --cargar")
    return df, calidad


def crear_graficas(df, resumen):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                        "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, y, etiqueta in zip(axes, ["calefaccion_media", "refrigeracion_media"], ["Y1", "Y2"]):
        for altura, color in [(3.5, "#137f86"), (7.0, "#d87932")]:
            sub = resumen[resumen.X5 == altura]
            ax.plot(sub.X1, sub[y], marker="o", color=color, label=f"Altura {altura:g}")
        ax.set(xlabel="Compacidad relativa (X1)", ylabel=f"Media de {etiqueta} (escala original)")
        ax.set_title("Calefacción" if etiqueta == "Y1" else "Refrigeración")
        ax.legend(frameon=False)
        ax.grid(axis="y", alpha=.2)
    fig.suptitle("Cargas medias de las configuraciones disponibles", fontsize=14)
    fig.tight_layout()
    fig.savefig(ROOT / "docs/figuras/01_compacidad_altura.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    for ax, y, titulo in zip(axes, ["Y1", "Y2"], ["Calefacción", "Refrigeración"]):
        ax.boxplot([df.loc[df.X5 == h, y] for h in [3.5, 7]], tick_labels=["3.5", "7"])
        ax.set(xlabel="Altura total (X5)", ylabel=f"{y} (escala original)", title=titulo)
        ax.grid(axis="y", alpha=.2)
    fig.suptitle("Distribución por altura: grupos con distinta geometría", fontsize=13)
    fig.tight_layout()
    fig.savefig(ROOT / "docs/figuras/02_cargas_altura.png", dpi=180)
    plt.close(fig)


def crear_datamart(df):
    destino = ROOT / "data/processed"
    geometria = df[["grupo_geometria"] + GEOMETRIA].drop_duplicates().sort_values("grupo_geometria")
    geometria = geometria.rename(columns={"grupo_geometria": "id_geometria"})
    orientacion = pd.DataFrame({"id_orientacion": sorted(df.X6.unique())})
    cristal = df[["X7", "X8"]].drop_duplicates().sort_values(["X7", "X8"]).reset_index(drop=True)
    cristal.insert(0, "id_acristalamiento", range(1, len(cristal) + 1))
    hechos = df.merge(cristal, on=["X7", "X8"], validate="many_to_one")
    hechos = hechos.rename(columns={"grupo_geometria": "id_geometria", "X6": "id_orientacion"})
    hechos = hechos[["id_registro", "id_geometria", "id_orientacion", "id_acristalamiento",
                     "Y1", "Y2", "clase_calefaccion"]]
    tablas = {"dim_geometria": geometria, "dim_orientacion": orientacion,
              "dim_acristalamiento": cristal, "hecho_simulacion": hechos}
    esquema = '''
    CREATE TABLE dim_geometria (id_geometria INTEGER PRIMARY KEY,
        X1 REAL NOT NULL, X2 REAL NOT NULL, X3 REAL NOT NULL, X4 REAL NOT NULL, X5 REAL NOT NULL);
    CREATE TABLE dim_orientacion (id_orientacion INTEGER PRIMARY KEY);
    CREATE TABLE dim_acristalamiento (id_acristalamiento INTEGER PRIMARY KEY, X7 REAL NOT NULL, X8 INTEGER NOT NULL);
    CREATE TABLE hecho_simulacion (id_registro INTEGER PRIMARY KEY,
        id_geometria INTEGER NOT NULL REFERENCES dim_geometria(id_geometria),
        id_orientacion INTEGER NOT NULL REFERENCES dim_orientacion(id_orientacion),
        id_acristalamiento INTEGER NOT NULL REFERENCES dim_acristalamiento(id_acristalamiento),
        Y1 REAL NOT NULL, Y2 REAL NOT NULL, clase_calefaccion TEXT NOT NULL);
    '''
    # Solo reconstruye este archivo DERIVADO. Nunca modifica data/raw.
    base = destino / "datamart_energia.sqlite"
    base.unlink(missing_ok=True)
    with sqlite3.connect(base) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(esquema)
        for nombre, tabla in tablas.items():
            tabla.to_csv(destino / f"{nombre}.csv", index=False)
            tabla.to_sql(nombre, conn, if_exists="append", index=False)
        assert conn.execute("SELECT COUNT(*) FROM hecho_simulacion").fetchone()[0] == len(df)
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        consulta = '''SELECT g.X1, g.X5, COUNT(*) AS registros,
        AVG(h.Y1) AS calefaccion_media, AVG(h.Y2) AS refrigeracion_media
        FROM hecho_simulacion h JOIN dim_geometria g ON g.id_geometria=h.id_geometria
        GROUP BY g.X1, g.X5 ORDER BY g.X1;'''
        pd.read_sql_query(consulta, conn).to_csv(destino / "consulta_datamart.csv", index=False)
    (ROOT / "sql/03_consultar_cargas.sql").write_text(consulta, encoding="utf-8")
    # Conservar el esquema SQLite como antecedente; el vigente es datamart.sql en SQL Server.
    (ROOT / "sql/legacy").mkdir(exist_ok=True)
    sql_server = esquema.replace("REAL", "FLOAT").replace("INTEGER", "INT").replace("TEXT", "VARCHAR(10)")
    (ROOT / "sql/legacy/01_crear_datamart_sqlserver.sql").write_text(
        "-- Ejecutar en una base de trabajo VACIA elegida en SQL Server.\n"
        "-- Antecedente historico. Esquema vigente: ../datamart.sql (estrella).\n" + sql_server, encoding="utf-8")
    cargas = ["-- Ejecutar una sola vez después del esquema, en la misma base.\nSET XACT_ABORT ON;\nBEGIN TRANSACTION;"]
    for nombre, tabla in tablas.items():
        for fila in tabla.itertuples(index=False, name=None):
            valores = ["'" + v.replace("'", "''") + "'" if isinstance(v, str) else str(v) for v in fila]
            cargas.append(f"INSERT INTO {nombre} ({', '.join(tabla.columns)}) VALUES ({', '.join(valores)});")
    cargas.append("COMMIT;")
    (ROOT / "sql/legacy/02_cargar_datamart_sqlserver.sql").write_text("\n".join(cargas), encoding="utf-8")


if __name__ == "__main__":
    preparar()

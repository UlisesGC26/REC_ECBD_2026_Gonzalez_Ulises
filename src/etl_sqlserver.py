"""Genera y carga un Data Mart copo de nieve, transaccional e idempotente.

Usa sqlcmd y autenticación integrada de Windows. No contiene contraseñas.
La base REC_ECBD_Energia está dedicada a este proyecto.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import pandas as pd
from src.preparacion_datos import ROOT, ENTRADAS, OBJETIVOS, guardar_json

BASE = 'REC_ECBD_Energia'
RELACIONES = [
    ('DimGeometria', 'id_altura', 'DimAltura', 'id_altura'),
    ('DimAcristalamiento', 'id_porcentaje', 'DimPorcentajeCristal', 'id_porcentaje'),
    ('DimAcristalamiento', 'id_distribucion', 'DimDistribucion', 'id_distribucion'),
    ('HECHOS', 'id_geometria', 'DimGeometria', 'id_geometria'),
    ('HECHOS', 'id_orientacion', 'DimOrientacion', 'id_orientacion'),
    ('HECHOS', 'id_acristalamiento', 'DimAcristalamiento', 'id_acristalamiento'),
    ('HECHOS', 'id_clase', 'DimClase', 'id_clase'),
    ('HECHOS', 'id_conjunto', 'DimConjunto', 'id_conjunto'),
    ('HECHOS', 'id_cluster', 'DimCluster', 'id_cluster'),
]


def tablas_copo():
    df = pd.read_csv(ROOT / 'data/processed/resultados_no_supervisados.csv')
    division = pd.read_csv(ROOT / 'data/processed/division_modelos.csv')
    pred = pd.read_csv(ROOT / 'data/processed/predicciones_prueba.csv')
    tablas = {}
    tablas['DimAltura'] = pd.DataFrame({'id_altura': [1, 2], 'altura': [3.5, 7.]})
    g = df[['grupo_geometria', 'X1', 'X2', 'X3', 'X4', 'X5']].drop_duplicates().copy()
    g['id_altura'] = g.X5.map({3.5: 1, 7.: 2})
    tablas['DimGeometria'] = g.drop(columns='X5').rename(columns={'grupo_geometria': 'id_geometria',
        'X1': 'compacidad', 'X2': 'superficie', 'X3': 'area_pared', 'X4': 'area_techo'})
    # Conservar códigos nominales; la ficha recibida no documenta su traducción.
    tablas['DimOrientacion'] = pd.DataFrame({'id_orientacion': [2, 3, 4, 5],
                                            'orientacion': ['Código 2', 'Código 3', 'Código 4', 'Código 5']})
    porcentajes = sorted(df.X7.unique())
    tablas['DimPorcentajeCristal'] = pd.DataFrame({'id_porcentaje': range(1, len(porcentajes)+1),
                                                  'proporcion_cristal': porcentajes})
    tablas['DimDistribucion'] = pd.DataFrame({'id_distribucion': list(range(6)),
        'distribucion': [f'Código {i}' for i in range(6)]})
    a = df[['X7', 'X8']].drop_duplicates().sort_values(['X7', 'X8']).reset_index(drop=True)
    a['id_acristalamiento'] = range(1, len(a)+1)
    a['id_porcentaje'] = a.X7.map(dict(zip(porcentajes, range(1, len(porcentajes)+1))))
    a['id_distribucion'] = a.X8
    tablas['DimAcristalamiento'] = a[['id_acristalamiento', 'id_porcentaje', 'id_distribucion']]
    tablas['DimClase'] = pd.DataFrame({'id_clase': [1, 2], 'clase': ['baja', 'alta'],
                                     'regla': ['Y1 < 25', 'Y1 >= 25']})
    tablas['DimConjunto'] = pd.DataFrame({'id_conjunto': [1, 2], 'conjunto': ['entrenamiento', 'prueba']})
    perfiles = pd.read_csv(ROOT / 'data/processed/perfiles_clusters.csv')
    tablas['DimCluster'] = pd.DataFrame({'id_cluster': perfiles.id_cluster,
                                        'cluster': [f'Cluster {i}' for i in perfiles.id_cluster]})
    h = df.merge(a, on=['X7', 'X8'], validate='many_to_one').merge(
        division[['id_registro', 'conjunto']], on='id_registro', validate='one_to_one').merge(
        pred[['id_registro', 'Y1_predicha', 'Y2_predicha', 'clase_predicha']],
        on='id_registro', how='left', validate='one_to_one')
    h['id_clase'] = h.clase_calefaccion.map({'baja': 1, 'alta': 2})
    h['id_conjunto'] = h.conjunto.map({'entrenamiento': 1, 'prueba': 2})
    h['error_absoluto_Y1'] = (h.Y1 - h.Y1_predicha).abs()
    h['error_absoluto_Y2'] = (h.Y2 - h.Y2_predicha).abs()
    h = h.rename(columns={'grupo_geometria': 'id_geometria', 'X6': 'id_orientacion'})
    tablas['HECHOS'] = h[['id_registro', 'id_geometria', 'id_orientacion', 'id_acristalamiento',
        'id_clase', 'id_conjunto', 'id_cluster', 'Y1', 'Y2', 'Y1_predicha', 'Y2_predicha',
        'clase_predicha', 'error_absoluto_Y1', 'error_absoluto_Y2', 'PC1', 'PC2']].sort_values('id_registro')
    tablas['MetricasRegresion'] = pd.read_csv(ROOT / 'docs/metricas_regresion.csv')
    tablas['MetricasClasificacion'] = pd.read_csv(ROOT / 'docs/metricas_clasificacion.csv')
    tablas['EvaluacionClusters'] = pd.read_csv(ROOT / 'docs/evaluacion_clusters.csv')
    tablas['VarianzaPCA'] = pd.read_csv(ROOT / 'docs/varianza_pca.csv')
    tablas['PerfilesClusters'] = perfiles
    tablas['ImportanciaVariables'] = pd.read_csv(ROOT / 'docs/importancia_variables.csv')
    tablas['MatrizConfusion'] = pred.groupby(['clase_real', 'clase_predicha']).size().reset_index(name='registros')
    return tablas


def literal(v):
    if pd.isna(v):
        return 'NULL'
    if isinstance(v, str):
        return "N'" + v.replace("'", "''") + "'"
    return str(v)


def generar():
    tablas = tablas_copo()
    raw = pd.read_excel(ROOT / 'data/raw/ENB2012_data.xlsx')
    raw.insert(0, 'id_registro', range(1, len(raw)+1))
    raw[['X6', 'X8']] = raw[['X6', 'X8']].astype(int)
    todas = {'DatasetOriginal': raw, **tablas}
    definiciones = {}
    for nombre, tabla in todas.items():
        cols = []
        for col in tabla.columns:
            tipo = 'INT' if pd.api.types.is_integer_dtype(tabla[col]) else (
                'FLOAT' if pd.api.types.is_numeric_dtype(tabla[col]) else 'NVARCHAR(120)')
            nullable = nombre == 'HECHOS' and col in ['Y1_predicha', 'Y2_predicha', 'clase_predicha', 'error_absoluto_Y1', 'error_absoluto_Y2']
            cols.append(f'[{col}] {tipo} ' + ('NULL' if nullable else 'NOT NULL'))
        if nombre in ['HECHOS', 'DatasetOriginal'] or nombre.startswith('Dim'):
            cols.append(f'CONSTRAINT [PK_{nombre}] PRIMARY KEY ([{tabla.columns[0]}])')
        for hija, fk, padre, pk in RELACIONES:
            if hija == nombre:
                cols.append(f'CONSTRAINT [FK_{hija}_{padre}] FOREIGN KEY ([{fk}]) REFERENCES dbo.[{padre}]([{pk}])')
        if nombre == 'HECHOS':
            cols.append('CONSTRAINT CK_HECHOS_cargas CHECK (Y1 > 0 AND Y2 > 0)')
            cols.append("CONSTRAINT CK_HECHOS_prueba CHECK ((id_conjunto=1 AND Y1_predicha IS NULL AND Y2_predicha IS NULL AND clase_predicha IS NULL) OR (id_conjunto=2 AND Y1_predicha IS NOT NULL AND Y2_predicha IS NOT NULL AND clase_predicha IS NOT NULL))")
        definiciones[nombre] = 'CREATE TABLE dbo.[' + nombre + '] (\n    ' + ',\n    '.join(cols) + '\n);'
    cabecera = f'''-- Data Mart copo de nieve. Base dedicada: {BASE}.
-- Regenera únicamente tablas de este proyecto dentro de una transacción.
-- Ejecutar con sqlcmd -S localhost -E -C -b -f 65001 -i sql/datamart.sql
USE master;
GO
IF DB_ID(N'{BASE}') IS NULL CREATE DATABASE [{BASE}];
GO
USE [{BASE}];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
BEGIN TRY
BEGIN TRANSACTION;
'''
    esquema = []
    for nombre in reversed(list(todas)):
        esquema.append(f'IF OBJECT_ID(N\'dbo.{nombre}\', N\'U\') IS NOT NULL DROP TABLE dbo.[{nombre}];')
    esquema.extend(definiciones.values())
    carga = []
    for nombre, tabla in todas.items():
        for inicio in range(0, len(tabla), 200):
            valores = ',\n'.join('(' + ','.join(literal(v) for v in fila) + ')'
                                for fila in tabla.iloc[inicio:inicio+200].itertuples(index=False, name=None))
            carga.append(f"INSERT INTO dbo.[{nombre}] ({','.join('['+c+']' for c in tabla.columns)}) VALUES\n{valores};")
    cierre = '''
IF (SELECT COUNT(*) FROM dbo.HECHOS) <> 768 THROW 51000, 'Conteo incorrecto en HECHOS', 1;
IF (SELECT COUNT(Y1_predicha) FROM dbo.HECHOS) <> 192 THROW 51001, 'Prueba debe tener 192 predicciones', 1;
COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
GO
'''
    vista = '''CREATE OR ALTER VIEW dbo.vDatasetReconstruido AS
SELECT h.id_registro, g.compacidad X1, g.superficie X2, g.area_pared X3, g.area_techo X4,
       alt.altura X5, o.id_orientacion X6, p.proporcion_cristal X7, d.id_distribucion X8, h.Y1, h.Y2
FROM dbo.HECHOS h
JOIN dbo.DimGeometria g ON h.id_geometria=g.id_geometria
JOIN dbo.DimAltura alt ON g.id_altura=alt.id_altura
JOIN dbo.DimOrientacion o ON h.id_orientacion=o.id_orientacion
JOIN dbo.DimAcristalamiento a ON h.id_acristalamiento=a.id_acristalamiento
JOIN dbo.DimPorcentajeCristal p ON a.id_porcentaje=p.id_porcentaje
JOIN dbo.DimDistribucion d ON a.id_distribucion=d.id_distribucion;
GO
'''
    validacion = '''SET NOCOUNT ON;
IF EXISTS (SELECT * FROM dbo.DatasetOriginal EXCEPT SELECT * FROM dbo.vDatasetReconstruido)
 OR EXISTS (SELECT * FROM dbo.vDatasetReconstruido EXCEPT SELECT * FROM dbo.DatasetOriginal)
 THROW 51002, 'La reconstruccion difiere del dataset original', 1;
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE is_disabled=1 OR is_not_trusted=1)
 THROW 51003, 'Hay llaves foraneas deshabilitadas o no confiables', 1;
SELECT 'HECHOS' tabla, COUNT(*) filas FROM dbo.HECHOS;
SELECT 'DatasetOriginal' tabla, COUNT(*) filas FROM dbo.DatasetOriginal;
SELECT 'Llaves foraneas activas' control, COUNT(*) valor FROM sys.foreign_keys WHERE is_disabled=0 AND is_not_trusted=0;
SELECT 'Predicciones de prueba' control, COUNT(Y1_predicha) valor FROM dbo.HECHOS;
SELECT AVG(Y1) calefaccion_media, AVG(Y2) refrigeracion_media FROM dbo.HECHOS;
SELECT 'RECONSTRUCCION_EXACTA_OK' resultado;
'''
    (ROOT / 'sql/datamart.sql').write_text(cabecera + '\n'.join(esquema+carga) + cierre+vista+validacion, encoding='utf-8')
    (ROOT / 'sql/script_creacion_datamart.sql').write_text('-- Esquema de referencia. Para crear Y cargar ejecutar datamart.sql.\nUSE [REC_ECBD_Energia];\nGO\n'+'\n'.join(definiciones.values()), encoding='utf-8')
    (ROOT / 'sql/validar_datamart.sql').write_text('USE [REC_ECBD_Energia];\nGO\n'+validacion, encoding='utf-8')
    carpeta = ROOT / 'data/processed/copo_nieve'; carpeta.mkdir(exist_ok=True)
    for nombre, tabla in tablas.items():
        tabla.to_csv(carpeta / f'{nombre}.csv', index=False)
    guardar_json(ROOT / 'docs/modelo_copo_nieve.json', {'base': BASE, 'grano': 'Una simulación de edificio por id_registro',
        'tablas': {n: {'filas': len(t), 'columnas': list(t.columns)} for n, t in todas.items()},
        'relaciones': [dict(tabla_hija=h, llave_foranea=f, tabla_padre=p, llave_primaria=k) for h, f, p, k in RELACIONES]})
    return tablas


def cargar(servidor='localhost'):
    generar()
    comando = ['sqlcmd', '-S', servidor, '-E', '-C', '-b', '-f', '65001', '-W', '-s', '|', '-i', str(ROOT / 'sql/datamart.sql')]
    resultado = subprocess.run(comando, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if resultado.returncode:
        raise RuntimeError(resultado.stdout + resultado.stderr)
    if 'RECONSTRUCCION_EXACTA_OK' not in resultado.stdout:
        raise RuntimeError('No se recibió la validación completa de SQL Server')
    evidencia = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'servidor': servidor,
        'base': BASE, 'motor': 'Microsoft SQL Server', 'autenticacion': 'Windows integrada',
        'codigo_salida': resultado.returncode, 'verificacion': resultado.stdout.strip(),
        'sha256_original': hashlib.sha256((ROOT / 'data/raw/ENB2012_data.xlsx').read_bytes()).hexdigest()}
    guardar_json(ROOT / 'docs/verificacion_sqlserver.json', evidencia)
    print(resultado.stdout)
    return evidencia


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cargar', action='store_true')
    parser.add_argument('--servidor', default='localhost')
    args = parser.parse_args()
    cargar(args.servidor) if args.cargar else generar()

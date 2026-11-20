"""Evidencias reproducibles por unidad; no inventa salidas de ejecución."""
import nbformat as nbf
from src.preparacion_datos import ROOT

INICIO = '''from pathlib import Path
import sys, json
import pandas as pd
from IPython.display import display, Image
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'src/preparacion_datos.py').exists())
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
print('Proyecto:', ROOT.name)
'''


def guardar(nombre, titulo, pares):
    c = [nbf.v4.new_markdown_cell(f'# {titulo}\nUlises González Coronado · Recursamiento ECBD 2026\n\n'
        'Dataset Energy Efficiency de UCI. Ejecutar de arriba hacia abajo con el entorno del repositorio.'),
         nbf.v4.new_code_cell(INICIO)]
    for texto, codigo in pares:
        c.append(nbf.v4.new_markdown_cell(texto))
        if codigo: c.append(nbf.v4.new_code_cell(codigo))
    nb = nbf.v4.new_notebook(cells=c, metadata={'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}})
    nbf.write(nb, ROOT / 'notebooks' / nombre)


def generar():
    guardar('Gonzalez_Coronado_Ulises_U2_AE2_ETL.ipynb','Unidad II · Preparación, ETL y Data Mart',[
        ('## 1. Extracción y copia de trabajo\nSe conserva el original; el hash permite comprobarlo.',
         "import hashlib\nraw = ROOT / 'data/raw/ENB2012_data.xlsx'\nfirma = hashlib.sha256(raw.read_bytes()).hexdigest()\noriginal = pd.read_excel(raw)\ntrabajo = original.copy(deep=True)\ndisplay(trabajo.head())"),
        ('## 2. Calidad y transformación justificada\nNo hay faltantes ni duplicados, por eso no se imputan ni eliminan filas. X6/X8 son códigos nominales. Los atípicos estadísticos no se eliminan sin evidencia de error. Se agregan identificadores, grupo de geometría y una clase didáctica.',
         "from src.preparacion_datos import preparar\nprocesado, calidad = preparar()\ndisplay(pd.Series(calidad))\npd.testing.assert_frame_equal(original.astype(float), procesado[original.columns].astype(float))\nassert hashlib.sha256(raw.read_bytes()).hexdigest() == firma\nprint('Los 768 registros originales se preservan exactamente.')"),
        ('## 3. Modelo estrella y grano\nUna fila de HECHOS representa una simulación. Altura forma parte de DimGeometria; proporción y distribución de cristal forman parte de DimAcristalamiento. Todas las dimensiones se conectan directamente a HECHOS. Las cargas se resumen por promedio, no por suma.\n\nEl modelo integrado incorpora resultados de UIII/UIV ya generados en el repositorio. Para reconstruir desde cero ejecutar primero `python -m src.ejecutar_proyecto`.',
         "from src.etl_sqlserver import generar, RELACIONES\ntablas = generar()\ndisplay(pd.DataFrame([{'tabla': n, 'filas': len(t)} for n,t in tablas.items()]))\ndisplay(pd.DataFrame(RELACIONES, columns=['hija','FK','padre','PK']))\ndisplay(tablas['HECHOS'].head())"),
        ('## 4. Carga real a SQL Server\nRequiere SQL Server local, sqlcmd y autenticación Windows. Solo reconstruye las tablas de la base dedicada REC_ECBD_Energia. La carga es transaccional y repetible.',
         "from src.etl_sqlserver import cargar\nverificacion = cargar('localhost')\nprint(verificacion['verificacion'])"),
        ('## 5. Conclusión\nLa reconstrucción desde las dimensiones y HECHOS coincide con DatasetOriginal. Las siete llaves foráneas de HECHOS permanecen activas, incluida DimTime. Las predicciones están disponibles únicamente en los 231 casos de prueba futura simulada; los nulos en entrenamiento son deliberados y no son errores de calidad.',None)])
    guardar('Gonzalez_Coronado_Ulises_U3_AnalisisSupervisado.ipynb','Unidad III · Regresión y clasificación',[
        ('## 1. X, y y separación\nX = X1-X8; regresión = Y1/Y2. Clasificación: alta si Y1 ≥ 25, baja en otro caso. Regla didáctica fijada antes de entrenar. Se excluyen identificadores, objetivos y clase de las entradas. La fecha sintética ordena un corte 70/30: 537 filas de entrenamiento y 231 de prueba futura simulada.',
         "df = pd.read_csv(ROOT / 'data/processed/eficiencia_energetica_procesada.csv')\ndisplay(df.head())\nfrom src.modelos_supervisados import ajustar_modelos\nresultado = ajustar_modelos()\ndisplay(resultado)"),
        ('## 2. Comparación y mejora\nPipeline ajusta escalamiento y OneHotEncoder dentro de cada fold. GridSearchCV compara Ridge/Random Forest y logística/Random Forest con GroupKFold de tres particiones. Se ajustan alpha, profundidad, hojas mínimas y C, según el algoritmo. El criterio de selección usa únicamente entrenamiento.',
         "display(pd.read_csv(ROOT/'docs/validacion_regresion.csv'))\ndisplay(pd.read_csv(ROOT/'docs/validacion_clasificacion.csv'))"),
        ('## 3. Regresión\nMAE mide error absoluto en la escala original; RMSE penaliza errores grandes; R² compara contra la variación de la prueba. Los errores no son porcentajes. La referencia de la media se ajusta en entrenamiento.',
         "display(pd.read_csv(ROOT/'docs/metricas_regresion.csv'))\ndisplay(Image(filename=str(ROOT/'docs/figuras/04_regresion_prueba.png')))"),
        ('## 4. Clasificación\nAccuracy = proporción de aciertos. Precision/Recall/F1 se informan por clase y en promedio macro. La logística reconoce las 120 cargas bajas y las 111 altas de esta prueba futura simulada. El 100% no debe extrapolarse: la fecha fue creada para demostrar el flujo temporal y no reemplaza validación con datos reales.',
         "display(pd.read_csv(ROOT/'docs/metricas_clasificacion.csv'))\ndisplay(pd.DataFrame(json.loads((ROOT/'docs/reporte_clasificacion.json').read_text(encoding='utf-8'))).T)\ndisplay(Image(filename=str(ROOT/'docs/figuras/03_matriz_confusion.png')))"),
        ('## 5. Relevancia y límites\nLa importancia por permutación se calcula después de seleccionar los modelos, sin reentrenar con la prueba. La correlación entre variables geométricas limita su interpretación individual. Una división de solo 12 geometrías simuladas no demuestra desempeño en edificios reales.',
         "imp = pd.read_csv(ROOT/'docs/importancia_variables.csv')\ndisplay(imp.sort_values(['tarea','importancia_media'], ascending=[True,False]))"),
        ('## 6. Utilidad\nLa regresión apoya la comparación de cargas estimadas. La clasificación resume una regla didáctica y no sustituye mediciones reales. Las diferencias de altura y compacidad están confundidas: no se presenta causalidad.',None)])
    guardar('Gonzalez_Coronado_Ulises_U4_AnalisisNoSupervisado.ipynb','Unidad IV · K-Means y PCA',[
        ('## 1. Selección y estandarización\nSe usan seis variables físicas X1-X5 y X7. Se excluyen X6/X8 porque sus códigos nominales no representan distancias. Y1/Y2 solo describen los grupos después de entrenar. StandardScaler centra y escala cada variable.',
         "from src.modelos_no_supervisados import analizar, VARIABLES\nresultado = analizar()\ndisplay(resultado)"),
        ('## 2. Número de grupos\nSe compara k = 2..8 con 30 inicializaciones y semilla 42. Se elige el mayor silhouette. También se revisa la inercia para el codo. Silhouette no es porcentaje de aciertos.',
         "display(pd.read_csv(ROOT/'docs/evaluacion_clusters.csv'))\ndisplay(Image(filename=str(ROOT/'docs/figuras/05_seleccion_clusters.png')))"),
        ('## 3. Caracterización\nDos grupos de 384 simulaciones corresponden a las alturas 3.5 y 7, junto con diferencias en geometría. Las medias de calefacción son aproximadamente 13.34 y 31.28. Y1/Y2 no se utilizaron para crear estos grupos.',
         "display(pd.read_csv(ROOT/'data/processed/perfiles_clusters.csv'))\nprint('ARI con otras semillas:', resultado['ARI_otras_semillas'])"),
        ('## 4. PCA y varianza explicada\nPCA usa la misma matriz estandarizada. Dos componentes explican 82.38% de la varianza; tres superan el 95%. La gráfica 2D pierde información. Las cargas indican qué variables contribuyen a cada eje; el signo puede invertirse sin cambiar la interpretación geométrica.',
         "display(pd.read_csv(ROOT/'docs/varianza_pca.csv'))\ndisplay(pd.read_csv(ROOT/'docs/cargas_pca.csv'))\ndisplay(Image(filename=str(ROOT/'docs/figuras/06_pca_clusters.png')))\ndisplay(Image(filename=str(ROOT/'docs/figuras/07_varianza_pca.png')))"),
        ('## 5. Conocimiento y decisiones\nLa estructura geométrica domina el agrupamiento; varias variables están correlacionadas. Los clusters sirven para organizar comparaciones entre diseños semejantes, no para certificar eficiencia. La estabilidad de semillas no demuestra validez externa. Se requieren mediciones reales y contexto climático para extrapolar.',None)])


if __name__ == '__main__': generar()

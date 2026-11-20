"""Crea un proyecto Power BI PBIP/PBIR con modelo importado desde SQL Server.

Abrir dashboard/Energia.pbip en Power BI Desktop y pulsar Actualizar.
Los JSON PBIR siguen los esquemas públicos de Microsoft, versión 1.0.0.
"""
import json
import uuid
from pathlib import Path
import pandas as pd
from src.preparacion_datos import ROOT
from src.etl_sqlserver import tablas_estrella, RELACIONES, BASE

DASH = ROOT / 'dashboard'
REPORT = DASH / 'Energia.Report'
MODEL = DASH / 'Energia.SemanticModel'
SCHEMA = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'


def escribir(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def lit(v):
    if isinstance(v, bool): value = 'true' if v else 'false'
    elif isinstance(v, str): value = "'" + v.replace("'", "''") + "'"
    else: value = str(v) + 'D'
    return {'expr': {'Literal': {'Value': value}}}


def color(v):
    return {'solid': {'color': lit(v)}}


def field(table, name, agg=None, measure=False):
    expr = {('Measure' if measure else 'Column'): {'Expression': {'SourceRef': {'Entity': table}}, 'Property': name}}
    ref = f'{table}.{name}'
    if agg is not None:
        expr = {'Aggregation': {'Expression': expr, 'Function': agg}}
        ref = f'Aggregation{agg}({ref})'
    return {'field': expr, 'queryRef': ref, 'nativeQueryRef': name}


def medida(name):
    return field('HECHOS', name, measure=True)


def visual(page, name, tipo, x, y, w, h, roles=None, title=None, objects=None):
    config = {'visualType': tipo, 'drillFilterOtherVisuals': True}
    if roles:
        config['query'] = {'queryState': {r: {'projections': f} for r, f in roles.items()}}
    if objects: config['objects'] = objects
    config['visualContainerObjects'] = {
        'background': [{'properties': {'color': color('#FFFFFF'), 'transparency': lit(0)}}],
        'border': [{'properties': {'show': lit(True), 'color': color('#C9D8DC')}}]}
    if title:
        config['visualContainerObjects']['title'] = [{'properties': {
            'show': lit(True), 'text': lit(title), 'fontSize': lit(14), 'fontColor': color('#173848')}}]
    data = {'$schema': SCHEMA+'visualContainer/1.0.0/schema.json', 'name': name,
            'position': {'x': x, 'y': y, 'width': w, 'height': h, 'z': 0, 'tabOrder': 0}, 'visual': config}
    escribir(REPORT / 'definition/pages' / page / 'visuals' / name / 'visual.json', data)


def texto(page, name, text, x, y, w, h, size=15, bold=False, dark=False):
    paragraphs = [{'textRuns': [{'value': linea, 'textStyle': {'fontFamily': 'Segoe UI',
        'fontSize': f'{size}pt', 'fontWeight': 'bold' if bold else 'normal',
        'color': '#173848' if dark else '#516572'}}]} for linea in text.split('\n')]
    visual(page, name, 'textbox', x,y,w,h, objects={'general': [{'properties': {'paragraphs': paragraphs}}]})


def pagina(name, title, subtitle):
    escribir(REPORT / 'definition/pages' / name / 'page.json', {
        '$schema': SCHEMA+'page/1.0.0/schema.json', 'name': name, 'displayName': title,
        'displayOption': 'FitToPage', 'width': 1280, 'height': 800,
        'objects': {'background': [{'properties': {'color': color('#EDF3F5'), 'transparency': lit(0)}}]}})
    texto(name, 'titulo', title, 24,16,1232,50,27,True,True)
    texto(name, 'subtitulo', subtitle,24,72,1232,48,12)


def generar():
    tablas = tablas_estrella()
    medidas = {
        'Simulaciones': ('COUNTROWS(HECHOS)', '#,0'),
        'Calefaccion media': ('AVERAGE(HECHOS[Y1])', '0.00'),
        'Refrigeracion media': ('AVERAGE(HECHOS[Y2])', '0.00'),
        'Geometrias': ('DISTINCTCOUNT(HECHOS[id_geometria])', '0'),
        'MAE calefaccion': ('AVERAGE(HECHOS[error_absoluto_Y1])', '0.000'),
        'MAE refrigeracion': ('AVERAGE(HECHOS[error_absoluto_Y2])', '0.000'),
        'Casos de prueba': ('CALCULATE(COUNTROWS(HECHOS), HECHOS[id_conjunto]=2)', '0'),
        'Accuracy prueba': ('DIVIDE(COUNTROWS(FILTER(HECHOS, HECHOS[id_conjunto]=2 && HECHOS[clase_predicha]=RELATED(DimClase[clase]))), [Casos de prueba])', '0.0%'),
        'F1 macro global': ('CALCULATE(MAX(MetricasClasificacion[F1_macro]), MetricasClasificacion[modelo]="Logistica")', '0.000'),
        'Silhouette elegido': ('MAX(EvaluacionClusters[silhouette])', '0.000'),
        'Varianza dos PC': ('CALCULATE(SUM(VarianzaPCA[varianza_explicada]), VarianzaPCA[componente] IN {"PC1", "PC2"})', '0.0%'),
    }
    model_tables = []
    for nombre, df in tablas.items():
        columns = []
        for col in df.columns:
            tipo = 'int64' if pd.api.types.is_integer_dtype(df[col]) else ('double' if pd.api.types.is_numeric_dtype(df[col]) else 'string')
            c = {'name': col, 'dataType': tipo, 'sourceColumn': col, 'summarizeBy': 'none',
                 'lineageTag': str(uuid.uuid5(uuid.NAMESPACE_URL, nombre+'.'+col))}
            if tipo == 'double': c['formatString'] = '0.00'
            if tipo == 'int64': c['formatString'] = '0'
            columns.append(c)
        m = [f'let', f'    Origen = Sql.Database("localhost", "{BASE}", [CreateNavigationProperties=false]),',
             f'    Tabla = Origen{{[Schema="dbo",Item="{nombre}"]}}[Data]', 'in', '    Tabla']
        t = {'name': nombre, 'lineageTag': str(uuid.uuid5(uuid.NAMESPACE_URL,nombre)), 'columns': columns,
             'partitions': [{'name': nombre, 'mode': 'import', 'source': {'type': 'm', 'expression': m}}]}
        if nombre == 'HECHOS':
            t['description'] = 'Una simulación por fila. Predicciones solo en 231 casos de prueba futura simulada. Cargas no aditivas: usar medias.'
            t['measures'] = [{'name': n, 'expression': e, 'formatString': f} for n, (e,f) in medidas.items()]
        model_tables.append(t)
    relationships = [{'name': f'{h}_{p}', 'fromTable': h, 'fromColumn': fk, 'toTable': p, 'toColumn': pk,
                      'crossFilteringBehavior': 'oneDirection', 'fromCardinality': 'many', 'toCardinality': 'one'}
                     for h, fk, p, pk in RELACIONES]
    escribir(MODEL / 'definition.pbism', {'version': '1.0', 'settings': {}})
    escribir(MODEL / 'model.bim', {'name': 'Energia', 'compatibilityLevel': 1567,
        'model': {'culture': 'es-MX', 'defaultPowerBIDataSourceVersion': 'powerBI_V3',
                  'sourceQueryCulture': 'es-MX', 'tables': model_tables, 'relationships': relationships,
                  'annotations': [{'name': 'PBI_QueryOrder', 'value': json.dumps(list(tablas))},
                                  {'name': 'PBI_ProTooling', 'value': '["DevMode"]'}]}})
    escribir(DASH / 'Energia.pbip', {'version': '1.0', 'artifacts': [{'report': {'path': 'Energia.Report'}}],
                                    'settings': {'enableAutoRecovery': True}})
    escribir(REPORT / 'definition.pbir', {'version': '4.0', 'datasetReference': {'byPath': {'path': '../Energia.SemanticModel'}}})
    escribir(REPORT / 'definition/version.json', {'$schema': SCHEMA+'versionMetadata/1.0.0/schema.json', 'version': '2.0.0'})
    escribir(REPORT / 'definition/report.json', {'$schema': SCHEMA+'report/1.0.0/schema.json',
        'themeCollection': {}, 'layoutOptimization': 'None'})
    nombres = ['01_resumen', '02_supervisado', '03_patrones', '04_modelo']
    escribir(REPORT / 'definition/pages/pages.json', {'$schema': SCHEMA+'pagesMetadata/1.0.0/schema.json',
        'pageOrder': nombres, 'activePageName': nombres[0]})
    p=nombres[0]
    pagina(p, '01 | Edificios y demanda energética', 'Explora promedios de carga por diseño. Los filtros cambian todos los visuales; la fecha es sintética y se usa para demostrar el ETL temporal.')
    for i,(m,t) in enumerate([('Simulaciones','Simulaciones'),('Geometrias','Geometrías'),('Calefaccion media','Y1 | calefacción media'),('Refrigeracion media','Y2 | refrigeración media')]):
        visual(p,'kpi'+str(i),'card',24+i*220,130,206,106,{'Values':[medida(m)]},t)
    visual(p,'fecha','slicer',910,130,170,106,{'Values':[field('DimTime','fecha')]},'Filtrar por fecha')
    visual(p,'altura','slicer',1090,130,166,106,{'Values':[field('DimGeometria','altura')]},'Filtrar por altura')
    visual(p,'cargas_altura','clusteredColumnChart',24,254,600,238,{'Category':[field('DimGeometria','altura')],
        'Y':[medida('Calefaccion media'),medida('Refrigeracion media')]},'Media de Y1 y Y2 por altura')
    visual(p,'cargas_compacidad','lineChart',646,254,610,238,{'Category':[field('DimGeometria','compacidad')],
        'Y':[medida('Calefaccion media'),medida('Refrigeracion media')]},'Media de Y1 y Y2 según compacidad')
    visual(p,'cristal','clusteredColumnChart',24,542,600,184,{'Category':[field('DimAcristalamiento','proporcion_cristal')],
        'Y':[medida('Calefaccion media'),medida('Refrigeracion media')]},'Media de Y1 y Y2 por proporción de cristal')
    texto(p,'nota_altura','QUÉ REPRESENTA: cada barra es la carga promedio de las simulaciones filtradas. Una barra más alta implica mayor carga media; no se deben sumar escenarios.',24,500,600,34,11)
    texto(p,'nota_compacidad','QUÉ REPRESENTA: cada punto resume la carga media para una compacidad. Describe asociación observada, no demuestra causalidad.',646,500,610,34,11)
    texto(p,'nota_cristal','QUÉ REPRESENTA: compara cargas promedio por proporción de cristal bajo los filtros activos.',24,734,600,34,11)
    texto(p,'hallazgo','LECTURA DEL RESULTADO\nLos diseños de altura 7 tienen cargas medias mayores. También cambia su geometría: no se puede aislar un efecto causal de altura o compacidad.\n\nCómo usar esta página: selecciona una fecha o altura y compara los promedios. Las cargas se muestran en la escala original del dataset.',646,542,610,220,15)
    p=nombres[1]
    pagina(p,'02 | Predicción y evaluación','Corte temporal: 231 fechas posteriores como prueba futura simulada · Entrenamiento: 537 casos')
    for i,(m,t) in enumerate([('MAE calefaccion','MAE de Y1'),('MAE refrigeracion','MAE de Y2'),('Accuracy prueba','Accuracy de prueba'),('F1 macro global','F1 macro global')]):
        visual(p,'kpi'+str(i),'card',24+i*310,130,294,100,{'Values':[medida(m)]},t)
    # HECHOS contiene predicciones nulas en entrenamiento: no mezclar evaluaciones.
    visual(p,'regresion','scatterChart',24,248,600,244,{'Category':[field('HECHOS','id_registro')],
        'X':[field('HECHOS','Y1',1)],'Y':[field('HECHOS','Y1_predicha',1)]},'Calefacción real vs. predicha | solo prueba')
    visual(p,'confusion','pivotTable',646,248,610,244,{'Rows':[field('MatrizConfusion','clase_real')],
        'Columns':[field('MatrizConfusion','clase_predicha')],'Values':[field('MatrizConfusion','registros',0)]},'Matriz de confusión | filas reales, columnas predichas')
    texto(p,'nota_regresion','QUÉ REPRESENTA: cada punto es una simulación del 30% futuro simulado. Mientras más se aproxime a la diagonal, menor es el error de Y1.',24,500,600,38,11)
    texto(p,'nota_confusion','QUÉ REPRESENTA: cuenta aciertos y errores de la clase alta/baja. La diagonal contiene los aciertos; fuera de ella están los errores.',646,500,610,38,11)
    visual(p,'metricas','tableEx',24,556,600,210,{'Values':[field('MetricasRegresion',c) for c in ['modelo','objetivo','MAE','RMSE','R2']]},'Métricas de regresión | menor MAE/RMSE y mayor R² es mejor')
    texto(p,'interpretacion','ALCANCE Y EVALUACIÓN\nRidge reduce claramente el MAE frente a la referencia de la media. La clasificación logística obtuvo 100% en este corte temporal sintético; no equivale a desempeño garantizado con datos reales.\n\nAlta significa Y1 ≥ 25: regla didáctica, no certificación. El ajuste se seleccionó dentro del entrenamiento con validación por geometría.',646,556,610,210,14)
    p=nombres[2]
    pagina(p,'03 | Patrones y componentes principales','K-Means y PCA sobre X1, X2, X3, X4, X5 y X7 estandarizadas · Y1/Y2 no participan en el agrupamiento')
    visual(p,'silhouette','card',24,130,270,100,{'Values':[medida('Silhouette elegido')]},'Silhouette | k = 2')
    visual(p,'varianza','card',310,130,270,100,{'Values':[medida('Varianza dos PC')]},'Varianza en PC1 + PC2')
    texto(p,'criterio','Se compararon k = 2 a 8. Dos grupos maximizan silhouette. Tres componentes conservan al menos 95% de la varianza.',600,130,656,100,15)
    visual(p,'pca','scatterChart',24,248,600,260,{'Category':[field('HECHOS','id_registro')],
        'Series':[field('DimCluster','cluster')], 'X':[field('HECHOS','PC1',1)], 'Y':[field('HECHOS','PC2',1)]},'PCA | cada punto es un edificio; color = cluster')
    visual(p,'seleccion','lineChart',646,248,300,260,{'Category':[field('EvaluacionClusters','k')],
        'Y':[field('EvaluacionClusters','silhouette',1)]},'Selección de k | silhouette más alto es mejor')
    visual(p,'varianzas','clusteredColumnChart',966,248,290,260,{'Category':[field('VarianzaPCA','componente')],
        'Y':[field('VarianzaPCA','varianza_explicada',0)]},'Varianza explicada por componente')
    texto(p,'nota_pca','QUÉ REPRESENTA: reducción de seis variables físicas a dos ejes. Puntos cercanos tienen perfiles geométricos semejantes.',24,516,600,38,11)
    texto(p,'nota_k','QUÉ REPRESENTA: se comparan alternativas de 2 a 8 grupos. Se selecciona k = 2 porque obtiene el mayor silhouette.',646,516,300,38,11)
    texto(p,'nota_varianza','QUÉ REPRESENTA: porcentaje de información retenida por cada componente. PC1 + PC2 resume 82.38%.',966,516,290,38,11)
    visual(p,'perfiles','tableEx',24,566,600,204,{'Values':[field('PerfilesClusters',c) for c in ['id_cluster','registros','altura_media','compacidad_media','calefaccion_media']]},'Perfil de los grupos')
    texto(p,'patron','CONOCIMIENTO Y USO\nLos dos clusters separan las alturas y sus geometrías. Ambos tienen 384 casos. La correlación geométrica domina este resultado.\nUsar grupos para comparar diseños similares; validar con datos reales antes de recomendar una construcción.',646,566,610,204,15)
    p=nombres[3]
    pagina(p,'04 | Del Excel al conocimiento','Extracción → validación → dimensiones → HECHOS → SQL Server → Power BI')
    texto(p,'modelo','MODELO ESTRELLA\nDimGeometria (incluye altura) → HECHOS\nDimAcristalamiento (incluye proporción y distribución) → HECHOS\nDimTime (calendario sintético) → HECHOS\nDimOrientacion / DimClase / DimConjunto / DimCluster → HECHOS\n\nGrano: una simulación por id_registro. 768 hechos, 7 relaciones, llaves primarias y foráneas.\nCarga FULL: DELETE de tablas del proyecto → ETL → recarga completa → Actualizar en Power BI.',24,136,720,330,18)
    visual(p,'filas','card',770,136,230,120,{'Values':[medida('Simulaciones')]},'Filas en HECHOS')
    visual(p,'prueba','card',1020,136,236,120,{'Values':[medida('Casos de prueba')]},'Filas de prueba')
    texto(p,'calidad','CALIDAD\nOriginal intacto.\nSin nulos ni duplicados.\nSin imputaciones ni filas eliminadas.\nReconstrucción SQL idéntica al original.',770,276,486,190,17)
    texto(p,'recomendaciones','RECOMENDACIONES\n1. Comparar configuraciones dentro de geometrías semejantes y revisar ambas cargas antes de priorizar diseños.\n2. Revisar los falsos negativos de carga alta antes de utilizar la clasificación como filtro de decisión.\n3. Incorporar mediciones reales, clima y materiales para evaluar generalización.\n\nLIMITACIÓN: simulaciones y solo 12 geometrías. Asociación no equivale a causalidad ni a ahorro real demostrado.',24,488,1232,278,19)
    print('Proyecto Power BI generado:', DASH / 'Energia.pbip')


if __name__ == '__main__':
    generar()

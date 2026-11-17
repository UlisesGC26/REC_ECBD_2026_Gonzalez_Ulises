"""Informes académicos derivados de métricas verificables, con PDF y Markdown."""
import json
from xml.sax.saxutils import escape
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from src.preparacion_datos import ROOT

DOC = ROOT / 'docs'


def diagrama():
    fig, ax = plt.subplots(figsize=(15,9)); ax.set(xlim=(0,15),ylim=(0,9)); ax.axis('off')
    cajas = {
        'DimGeometria': (.5,6.8,3.4,1.5,'PK id_geometria\ncompacidad, superficies, altura'),
        'DimOrientacion': (5.7,7.0,3.1,1.25,'PK id_orientacion\ncódigo nominal'),
        'DimAcristalamiento': (10.6,6.8,3.8,1.5,'PK id_acristalamiento\nproporción de cristal, distribución'),
        'HECHOS': (4.3,3.1,6.3,2.5,'PK id_registro · 768 simulaciones\nFK geometría, orientación, acristalamiento\nFK clase, conjunto, cluster\nY1, Y2, predicciones de prueba\nerrores absolutos, PC1, PC2'),
        'DimClase': (.5,.5,2.9,1.25,'PK id_clase\nbaja / alta (Y1 ≥ 25)'),
        'DimConjunto': (4.5,.5,3.0,1.25,'PK id_conjunto\nentrenamiento / prueba'),
        'DimCluster': (10.6,.5,3.1,1.25,'PK id_cluster\ngrupo K-Means'),
    }
    for name,(x,y,w,h,body) in cajas.items():
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',linewidth=1.4,
            edgecolor='#147d92', facecolor='#173848' if name=='HECHOS' else '#edf4f6'))
        fg='white' if name=='HECHOS' else '#173848'
        ax.text(x+.15,y+h-.28,name,fontsize=11,weight='bold',color=fg,va='center')
        ax.text(x+.15,y+h-.52,body,fontsize=9.5,color=fg,va='top',linespacing=1.6)
    enlaces=[((2.2,6.8),(5.4,5.7)),((7.2,7.0),(7.2,5.7)),((12.5,6.8),(9.8,5.7)),
             ((2.0,1.8),(5.4,3.1)),((6.0,1.8),(6.8,3.1)),((12.1,1.8),(9.8,3.1))]
    for a,b in enlaces:
        ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,color='#ca673b',lw=1.8))
        ax.text(a[0]+.05,a[1]+.1,'1',fontsize=9,color='#a64b26')
        ax.text(b[0]-.12,b[1]-.16,'N',fontsize=9,color='#a64b26')
    ax.set_title('Data Mart en estrella · SQL Server y Power BI',fontsize=19,color='#173848',weight='bold',pad=14)
    fig.tight_layout(); fig.savefig(DOC/'figuras/08_estrella.png',dpi=170,bbox_inches='tight')
    fig.savefig(DOC/'diagrama_estrella.svg',bbox_inches='tight'); plt.close(fig)


def generar():
    diagrama()
    pdfmetrics.registerFont(TTFont('ArialLocal','C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialLocal-Bold','C:/Windows/Fonts/arialbd.ttf'))
    styles=getSampleStyleSheet()
    for name in ['Normal','BodyText','Heading1','Heading2','Title']:
        styles[name].fontName='ArialLocal'
    styles['BodyText'].fontSize=10; styles['BodyText'].leading=15; styles['BodyText'].spaceAfter=9
    styles['Heading1'].fontName='ArialLocal-Bold'; styles['Heading1'].fontSize=17; styles['Heading1'].leading=22
    styles['Heading1'].textColor=colors.HexColor('#147d92'); styles['Heading1'].spaceAfter=14
    styles['Heading2'].fontName='ArialLocal-Bold'; styles['Heading2'].fontSize=12; styles['Heading2'].spaceBefore=12
    styles['Title'].fontSize=26; styles['Title'].leading=32; styles['Title'].textColor=colors.HexColor('#173848')
    styles.add(ParagraphStyle(name='SmallTable',fontName='ArialLocal',fontSize=8,leading=11))
    quality=json.loads((DOC/'reporte_calidad_datos.json').read_text(encoding='utf-8'))
    unsup=json.loads((DOC/'resultados_no_supervisados.json').read_text(encoding='utf-8'))
    raw=pd.read_excel(ROOT/'data/raw/ENB2012_data.xlsx')
    def para(t): return Paragraph(escape(str(t)),styles['BodyText'])
    def tabla(df):
        df=df.copy()
        for c in df.select_dtypes('number'): df[c]=df[c].map(lambda x:f'{x:.4f}' if isinstance(x,float) else str(x))
        rows=[[Paragraph(escape(str(c)),styles['SmallTable']) for c in df.columns]]
        rows += [[Paragraph(escape(str(v)),styles['SmallTable']) for v in row] for row in df.itertuples(index=False,name=None)]
        t=Table(rows,colWidths=[483/len(df.columns)]*len(df.columns),repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcecef')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#147d92'))]))
        return t
    def imagen(ruta, maxwidth=483):
        from PIL import Image as PILImage
        w,h=PILImage.open(DOC/ruta).size
        return Image(str(DOC/ruta),width=maxwidth,height=min(365,maxwidth*h/w),kind='proportional')
    def footer(canvas,doc):
        canvas.setStrokeColor(colors.HexColor('#ccdce0'));canvas.line(56,42,539,42)
        canvas.setFont('ArialLocal',8);canvas.setFillColor(colors.HexColor('#516572'))
        canvas.drawString(56,29,'Ulises González Coronado | ECBD 2026 | Energy Efficiency')
        canvas.drawRightString(539,29,str(doc.page))
    fuente='Fuente: Tsanas, A. y Xifara, A. (2012). Energy Efficiency. UCI Machine Learning Repository. DOI: 10.24432/C51307. Licencia CC BY 4.0. El Excel original conserva su contenido.'
    intro='Pregunta: ¿cómo cambian las cargas de calefacción y refrigeración entre edificios con distinta compacidad relativa y altura total? Se analizan 768 simulaciones de 12 geometrías. Y1 e Y2 son cargas, no años. Los resultados usan la escala original porque la ficha consultada no declara las unidades.'
    secciones={
        'diagnostico':[
            ('h','Origen, estructura y variables'),('p',intro),('p',fuente),
            ('p','Los datos son estructurados: un archivo Excel con diez columnas numéricas. X1-X5 y X7 representan características físicas; X6 y X8 son categorías nominales codificadas. Y1 y Y2 son las respuestas. Los notebooks muestran head, shape, columns, info, dtypes y describe. El diccionario completo está en docs/diccionario_datos.md y en el notebook de exploración.'),
            ('t',raw[['X1','Y1','Y2']].agg(['mean','median','min','max','std']).T.reset_index(names='variable')),
            ('h','Calidad y decisiones'),('p','No se encontraron valores faltantes, duplicados completos ni entradas X1-X8 repetidas. Los tipos son compatibles y los códigos pertenecen a los dominios observados. Se revisan atípicos mediante IQR; una marca estadística no basta para eliminar una simulación válida. Se conservan las 768 filas.'),
            ('page',None),('h','Tres visualizaciones e interpretación'),
            ('img','figuras/01_compacidad_altura.png'),('p','La relación entre compacidad y cargas cambia entre las configuraciones observadas. Ninguna compacidad aparece en ambas alturas; los efectos de ambas variables no se pueden aislar.'),
            ('img','figuras/02_cargas_altura.png'),('p','Las distribuciones por altura muestran mayor carga en el grupo de 7, que además presenta otras diferencias de geometría.'),
            ('page',None),('img','figuras/09_histograma.png'),('p','Los histogramas muestran un rango amplio de calefacción y refrigeración. El promedio resume las simulaciones, pero no describe por sí solo la heterogeneidad de los diseños.'),
            ('h','Propuesta de análisis y conclusión'),('p','Regresión: X1-X8 para predecir Y1/Y2. Clasificación: las mismas entradas para distinguir Y1 alta/baja con corte didáctico de 25. Clustering: X1-X5 y X7 estandarizadas, excluyendo objetivos y códigos nominales. El dataset es viable para practicar estos métodos, con límites de simulación y poca diversidad geométrica.')],
        'etl':[
            ('h','Extracción y preparación'),('p',intro),('p','El ETL lee el Excel en data/raw, crea una copia y valida columnas, tipos, dominios, duplicados, nulos y valores finitos. X6/X8 se conservan como enteros nominales. No hay imputaciones ni eliminaciones. Se agregan id_registro, grupo_geometria y clase_calefaccion; la clase es alta cuando Y1 >= 25. En los modelos se aplica OneHotEncoder a las categorías y escalamiento dentro del Pipeline.'),
            ('t',pd.DataFrame({'Control':['Filas originales','Filas procesadas','Faltantes','Duplicados','Imputaciones','Eliminaciones'],'Resultado':[768,768,0,0,0,0]})),
            ('p','El SHA-256 del original es '+quality['sha256_original']+'. Los valores X1-X8/Y1-Y2 se comparan directamente con el archivo procesado. Los derivados se guardan en data/processed.'),
            ('page',None),('h','Modelo dimensional en estrella'),('img','figuras/08_estrella.png'),
            ('p','Grano: una simulación por fila en HECHOS, con id_registro como llave primaria. La altura se integra en DimGeometria y la proporción/distribución de cristal se integran en DimAcristalamiento. HECHOS referencia directamente seis dimensiones: geometría, orientación, acristalamiento, clase, conjunto y cluster. Se implementan seis llaves foráneas. Las medidas Y1/Y2 se analizan con promedios; sumar cargas de escenarios alternativos no representa consumo real.'),
            ('h','Carga y validación en SQL Server'),('p','La base REC_ECBD_Energia contiene DatasetOriginal, HECHOS, dimensiones y tablas de evaluación. El script sql/datamart.sql crea la base si hace falta y reemplaza únicamente las tablas del proyecto en transacciones con XACT_ABORT y manejo de errores. No modifica otras bases. Se conserva evidencia de la carga real en docs/verificacion_sqlserver.json.'),
            ('p','La vista vDatasetReconstruido vuelve a unir hechos y dimensiones. EXCEPT en ambos sentidos no encuentra diferencias respecto a DatasetOriginal. Se verifican 768 hechos, seis llaves foráneas directas a HECHOS y 192 predicciones. En entrenamiento las predicciones son NULL deliberadamente. Power BI importa estas mismas tablas y reproduce sus relaciones.')],
        'supervisado':[
            ('h','Diseño y prevención de fuga'),('p',intro),('p','Las entradas son X1-X8. La regresión estima Y1/Y2; la clasificación usa alta si Y1 >= 25. El corte se fija antes de entrenar y no es una norma energética. GroupShuffleSplit reserva tres geometrías completas: 576 filas de entrenamiento y 192 de prueba, sin geometrías compartidas. El preprocesamiento se ajusta dentro de cada fold.'),
            ('h','Comparación y optimización justificada'),('p','GroupKFold de tres particiones compara Ridge con Random Forest y logística con Random Forest. Se prueban alpha, C, profundidad máxima y tamaño mínimo de hoja. En validación, el MAE conjunto del bosque con profundidad 8 y hoja 1 es 3.5896, frente a 3.5935 sin límite de profundidad. Se elige la opción ligeramente más simple. En logística, C=1 mejora F1 macro de validación de 0.8413 (C=0.1) a 0.8847; C=10 baja a 0.8500. La prueba no interviene en la elección.'),
            ('t',pd.read_csv(DOC/'metricas_regresion.csv')),('p','El MAE es el error absoluto medio, RMSE penaliza errores grandes y R² compara con la dispersión de la prueba. El bosque mejora la referencia de predecir la media de entrenamiento en ambas cargas. Las métricas no prueban ahorro real.'),
            ('page',None),('h','Clasificación y errores'),('t',pd.read_csv(DOC/'metricas_clasificacion.csv')),('img','figuras/03_matriz_confusion.png'),
            ('p','La logística acierta 152 de 192 casos. Reconoce las 72 cargas bajas y 80 de las 120 altas. Los 40 falsos negativos de carga alta limitan su uso para descartar diseños. Se presentan precisión, recall y F1 por clase en reporte_clasificacion.json; el promedio macro da el mismo peso a cada clase.'),
            ('page',None),('h','Regresión, variables y utilidad'),('img','figuras/04_regresion_prueba.png'),
            ('p','La importancia por permutación posterior a la selección identifica X5 como la variable con mayor deterioro al permutarla en ambas tareas. X4 y X7 también aportan señal. Algunas importancias son negativas: la correlación geométrica y la muestra pequeña pueden producir estos resultados. No se interpretan como efectos causales. Los detalles están en importancia_variables.csv.'),
            ('p','La regresión permite comparar estimaciones entre diseños; la clasificación resume un umbral didáctico. Solo se evalúa una separación de 12 geometrías simuladas, por lo que falta validación externa antes de tomar decisiones reales.')],
        'no_supervisado':[
            ('h','Variables y estandarización'),('p','Se usan X1, X2, X3, X4, X5 y X7 porque representan atributos físicos comparables mediante distancias después de StandardScaler. Se excluyen los códigos nominales X6/X8 y las cargas Y1/Y2. El análisis es exploratorio de las 768 simulaciones y no estima capacidad predictiva fuera de muestra.'),
            ('h','K-Means: elección del número de grupos'),('t',pd.read_csv(DOC/'evaluacion_clusters.csv')),('img','figuras/05_seleccion_clusters.png'),
            ('p',f"Se eligió k={unsup['k_elegido']} por el mayor silhouette ({unsup['silhouette']:.4f}) entre 2 y 8. Se usaron 30 inicializaciones y semilla 42. Silhouette mide separación y cohesión, no exactitud ni porcentaje de aciertos. Con semillas 7, 21 y 84, el ARI respecto a la solución principal fue 1.0."),
            ('page',None),('h','Perfil de los clusters'),('t',pd.read_csv(ROOT/'data/processed/perfiles_clusters.csv')[['id_cluster','registros','altura_media','compacidad_media','calefaccion_media','refrigeracion_media']]),
            ('p','Los clusters coinciden con las dos alturas y sus geometrías asociadas. Cada grupo contiene 384 simulaciones. Ambos tienen la misma proporción media de cristal (0.234375). Las cargas se utilizan solo después para describir los grupos; no determinaron sus etiquetas. La geometría correlacionada domina el agrupamiento.'),
            ('h','PCA: representación y varianza'),('img','figuras/06_pca_clusters.png'),('p','PC1 y PC2 retienen el 82.38% de la varianza estandarizada. Son combinaciones de variables originales, no nuevas unidades físicas. La proyección muestra separación de los grupos, pero pierde el 17.62% de la varianza. Las cargas de los componentes se incluyen en cargas_pca.csv.'),
            ('page',None),('img','figuras/07_varianza_pca.png'),('t',pd.read_csv(DOC/'varianza_pca.csv')),('h','Conocimiento y recomendaciones'),
            ('p','Tres componentes conservan al menos el 95% de la varianza. El análisis permite organizar comparaciones entre diseños semejantes y reconocer que altura, compacidad y superficies no varían de forma independiente. Se recomienda comparar ambas cargas dentro de grupos geométricos y validar patrones con datos de edificios reales. Los clusters no certifican eficiencia; estabilidad de semillas tampoco equivale a validez externa.')],
    }
    fig,axes=plt.subplots(1,2,figsize=(10,3.6))
    for ax,c in zip(axes,['Y1','Y2']):
        ax.hist(raw[c],bins=16,color='#147d92',edgecolor='white');ax.set(title=c,xlabel='Carga (escala original)',ylabel='Simulaciones')
    fig.tight_layout();fig.savefig(DOC/'figuras/09_histograma.png',dpi=170);plt.close(fig)
    final=[('h','Resumen ejecutivo'),('p',intro),('p','El proyecto integra exploración, preparación, SQL Server, un Data Mart en estrella, modelos supervisados, K-Means, PCA y un dashboard de cuatro páginas en Power BI. Se conserva el dataset original y el código permite reconstruir las evidencias.'),
        ('h','Tres conclusiones sustentadas'),('p','1. La calefacción media es 13.34 para altura 3.5 y 31.28 para altura 7; refrigeración media 16.07 y 33.10. Las geometrías también cambian, por lo que no puede aislarse causalmente la altura.'),
        ('p','2. Random Forest obtiene MAE 3.3304 en calefacción y 4.3288 en refrigeración, inferiores a 8.2677 y 8.5548 de la referencia de la media. La logística logra 79.17% de exactitud y deja 40 cargas altas como bajas.'),
        ('p','3. K-Means selecciona dos grupos de 384 casos, con silhouette 0.5244. Coinciden con alturas y geometrías distintas. PC1/PC2 explican 82.38% de la varianza; tres componentes superan el 95%.'),
        ('h','Recomendaciones de decisión'),('p','Comparar configuraciones dentro de geometrías semejantes y considerar simultáneamente calefacción y refrigeración. Revisar falsos negativos antes de usar la clasificación para descartar diseños. Incorporar clima, materiales y mediciones reales antes de extrapolar a construcción.'),('page',None)]
    final += secciones['etl'] + [('page',None)] + secciones['supervisado'] + [('page',None)] + secciones['no_supervisado']
    final += [('page',None),('h','Dashboard y storytelling'),('p','Abrir dashboard/Energia.pbip (proyecto editable) o el PBIX guardado, y actualizar desde SQL Server. Página 1: problema y datos, indicadores, altura, compacidad y cristal. Página 2: predicciones, métricas y matriz de confusión. Página 3: elección de k, perfiles, PCA y varianza. Página 4: ETL, estrella, conclusiones y recomendaciones. La Vista de modelo permite inspeccionar las relaciones reales.'),
        ('h','Reproducibilidad y defensa'),('p','Instalar requirements_notebooks.txt, ejecutar python -m src.ejecutar_proyecto, después python -m src.etl_sqlserver --cargar y ejecutar todos los notebooks. Las evidencias automáticas están en docs/verificacion_sqlserver.json y docs/verificacion_notebooks.json. El guion de defensa explica el orden y las decisiones. No se acredita una defensa oral ni observaciones futuras por generar estos archivos.'),
        ('h','Calendario y observaciones'),('p','Los dos documentos recibidos difieren: el programa de trabajo continuo fija revisión formal el 17 de noviembre, mientras el programa de actividades restantes indica revisión integradora el 18. Ambos fijan cierre el 20 de noviembre de 2026. Se conserva esa diferencia en la matriz de cumplimiento. Las observaciones del docente se registrarán cuando ocurran y deberán resolverse antes del cierre.'),
        ('h','Fuentes'),('p',fuente),('p','Scikit-learn: documentación de GroupKFold, GridSearchCV, KMeans, silhouette_score y PCA, https://scikit-learn.org/stable/. Microsoft Learn: proyectos Power BI, https://learn.microsoft.com/power-bi/developer/projects/projects-overview. Los requisitos académicos proceden de los dos programas proporcionados por el estudiante. Repositorio: https://github.com/UlisesGC26/REC_ECBD_2026_Gonzalez_Ulises.')]
    informes=[('Gonzalez_Coronado_Ulises_U2_AE1_Diagnostico','Unidad II · Exploración y diagnóstico','diagnostico'),
        ('Gonzalez_Coronado_Ulises_U2_AE2_PreparacionDatos','Unidad II · ETL y Data Mart','etl'),
        ('Gonzalez_Coronado_Ulises_U3_Informe','Unidad III · Análisis supervisado','supervisado'),
        ('Gonzalez_Coronado_Ulises_U4_Informe','Unidad IV · Análisis no supervisado','no_supervisado'),
        ('Informe_Final','Proyecto Integrador · Informe final','final')]
    for filename,title,key in informes:
        elementos=final if key=='final' else secciones[key]
        story=[Paragraph(title,styles['Title']),Spacer(1,12),para('Evaluación de eficiencia energética de edificios'),
               para('Ulises González Coronado · Universidad Tecnológica de Tula-Tepeji'),
               para('Extracción de Conocimiento en Bases de Datos · Recursamiento 2026'),para('Actualización técnica: 16 de noviembre de 2026'),Spacer(1,18)]
        md=['# '+title,'','Ulises González Coronado · Actualización técnica: 16 de noviembre de 2026','']
        for tipo,valor in elementos:
            if tipo=='h':story.append(Paragraph(escape(valor),styles['Heading1']));md.extend(['## '+valor,''])
            elif tipo=='p':story.append(para(valor));md.extend([valor,''])
            elif tipo=='t':story.extend([tabla(valor),Spacer(1,12)]);md.extend([valor.to_markdown(index=False),''])
            elif tipo=='img':story.extend([imagen(valor, 360 if key=='no_supervisado' and '05_seleccion' in valor else 483),Spacer(1,10)]);md.extend([f'![Figura]({valor})',''])
            elif tipo=='page':story.append(PageBreak())
        SimpleDocTemplate(str(DOC/(filename+'.pdf')),pagesize=A4,rightMargin=56,leftMargin=56,topMargin=48,bottomMargin=58,title=title,author='Ulises González Coronado').build(story,onFirstPage=footer,onLaterPages=footer)
        (DOC/(filename+'.md')).write_text('\n'.join(md),encoding='utf-8')
        print(filename+'.pdf',flush=True)


if __name__ == '__main__': generar()

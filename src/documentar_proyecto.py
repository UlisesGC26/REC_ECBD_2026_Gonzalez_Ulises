"""Documentación operativa y matriz de trazabilidad de la entrega."""
from src.preparacion_datos import ROOT


def generar():
    archivos={
'README.md':r'''# Evaluación de eficiencia energética de edificios

**Ulises González Coronado · Recursamiento ECBD 2026**  
Universidad Tecnológica de Tula-Tepeji · Docente: Ing. José Luis Herrera Gallardo.  
Actualización técnica: **16 de noviembre de 2026**.

Repositorio: https://github.com/UlisesGC26/REC_ECBD_2026_Gonzalez_Ulises

## Pregunta y alcance

¿Cómo cambian las cargas de calefacción y refrigeración entre edificios con distinta compacidad relativa y altura total?

Se utilizan 768 simulaciones de Energy Efficiency (UCI), ocho entradas X1-X8 y dos respuestas Y1/Y2. Las cargas se muestran en la escala original: la ficha consultada no declara unidades. Los resultados no demuestran ahorro real ni causalidad. Ningún valor de compacidad aparece en ambas alturas.

## Evidencias y estado

| Componente | Evidencia |
|---|---|
| Dataset original intacto | `data/raw/ENB2012_data.xlsx` |
| Preparación y dataset procesado | `src/preparacion_datos.py`, `data/processed/eficiencia_energetica_procesada.csv` |
| SQL Server ejecutado | Base `REC_ECBD_Energia` en `localhost`; `docs/verificacion_sqlserver.json` |
| Modelo estrella | `sql/datamart.sql`, `docs/diagrama_estrella.svg`, `data/processed/estrella/` |
| Regresión y clasificación | `src/modelos_supervisados.py`, `modelos/`, `docs/metricas_*.csv` |
| K-Means y PCA | `src/modelos_no_supervisados.py`, `docs/resultados_no_supervisados.json` |
| Power BI | `dashboard/Energia.pbip` y sus carpetas Report/SemanticModel |
| Notebooks ejecutados | Seis notebooks; `docs/verificacion_notebooks.json` registra cero errores |
| Informes | Cuatro PDF por actividad y `docs/Informe_Final.pdf` |
| Defensa y requisitos | `docs/guia_revision_proyecto.md`, `docs/matriz_cumplimiento.md` |

Los archivos de `docs/entregas_previas/` y el informe U2_U3 conservan evidencias anteriores. El panel Streamlit y SQLite se mantienen como complemento; el modelo final solicitado es SQL Server + Power BI. Las observaciones de una revisión futura y la defensa oral deben realizarlas el estudiante y el docente; no se acreditan por generar archivos.

## Ejecución en Windows

Requisitos: Python 3.13 (verificado), SQL Server 2022 local activo, `sqlcmd`, Power BI Desktop y una cuenta Windows con acceso a la base. No hay contraseñas en el repositorio. Ejecutar desde esta carpeta:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements_notebooks.txt
.\.venv\Scripts\python.exe -m src.ejecutar_proyecto
.\.venv\Scripts\python.exe -m src.etl_sqlserver --cargar
.\.venv\Scripts\python.exe -m src.verificar_notebooks
```

El análisis genera datos, figuras, métricas y modelos. La carga crea la base `REC_ECBD_Energia` si falta y reconstruye **solo sus tablas del proyecto** en una transacción. No modifica otras bases. Para otro servidor: `python -m src.etl_sqlserver --cargar --servidor NOMBRE` y cambiar el servidor en Power Query.

También puede ejecutarse el SQL autocontenido, sin Python:

```powershell
sqlcmd -S localhost -E -C -b -f 65001 -i sql/datamart.sql
sqlcmd -S localhost -E -C -b -f 65001 -i sql/validar_datamart.sql
```

`-E` usa autenticación Windows. `-C` permite el certificado local de la instancia de desarrollo. Los scripts se destinan exclusivamente a la base del proyecto.

## Abrir Power BI

Abrir `dashboard/Energia.pbip`. Mantener junto al archivo las carpetas `Energia.Report` y `Energia.SemanticModel`. Actualizar datos desde SQL Server con autenticación Windows. Si se requiere el formato monolítico, usar **Archivo > Guardar como > PBIX**. Consultar `dashboard/README.md` para las páginas y comprobaciones.

El modelo tiene **HECHOS** con 768 filas y seis relaciones 1:N de filtro simple. Todas las dimensiones se conectan directamente con HECHOS; altura se integra en geometría y los atributos de cristal en acristalamiento. Las tablas de métricas globales quedan separadas para no confundir medidas del conjunto de prueba con filtros exploratorios.

## Resultados reproducidos

| Modelo / medida | Resultado |
|---|---:|
| Random Forest, MAE Y1 | 3.3304 |
| Random Forest, MAE Y2 | 4.3288 |
| R² Y1 / Y2 | 0.8064 / 0.6958 |
| Logística, accuracy | 79.17% |
| Precision macro / Recall macro | 0.8214 / 0.8333 |
| F1 macro | 0.7913 |
| K-Means, k seleccionado | 2 |
| Silhouette | 0.5244 |
| Varianza PC1 + PC2 | 82.38% |

Entrenamiento: 576 filas de nueve geometrías. Prueba: 192 filas de tres geometrías, sin compartir diseños. Se seleccionan y ajustan modelos mediante GroupKFold de tres particiones exclusivamente en entrenamiento. La clasificación alta/baja usa un corte didáctico fijo Y1 >= 25. Los 40 falsos negativos de carga alta son una limitación relevante.

K-Means y PCA utilizan X1-X5 y X7 estandarizadas, sin las cargas ni los códigos nominales. Se comparan k=2..8. Los dos grupos contienen 384 casos cada uno y separan alturas y geometrías correlacionadas. La estabilidad entre semillas no demuestra validez externa.

## Notebooks y documentos

- `Gonzalez_Coronado_Ulises_U2_AE1_Exploracion.ipynb`: diagnóstico, diccionario, estadística y gráficos interpretados.
- `Gonzalez_Coronado_Ulises_U2_AE2_ETL.ipynb`: comparación original/procesado, carga SQL y modelo estrella.
- `Gonzalez_Coronado_Ulises_U3_AnalisisSupervisado.ipynb`: selección, ajuste, métricas, importancia e interpretación.
- `Gonzalez_Coronado_Ulises_U4_AnalisisNoSupervisado.ipynb`: selección de k, perfiles, PCA y conclusiones.
- `01_preparacion_datos.ipynb` y `02_analisis_supervisado.ipynb`: evidencias iniciales conservadas y verificadas.

Los cuatro informes de actividad están en `docs/`, junto con `Informe_Final.pdf` y sus fuentes Markdown. Para regenerar informes: instalar `requirements_informes.txt` y ejecutar `python -m src.generar_informes`. El generador usa Arial de Windows. La revisión visual se apoya en `python -m src.revisar_pdfs`.

## Organización

```text
data/raw/                 Dataset original
data/processed/           Derivados, predicciones y exportaciones del modelo estrella
notebooks/                Evidencias ejecutables por actividad
src/                      Análisis, ETL, validación y generadores
sql/                      Creación, carga y validación del Data Mart
modelos/                  Pipelines supervisados y paquete K-Means/PCA
dashboard/                Power BI y panel complementario
docs/                     Informes, diagramas, resultados y guía de defensa
```

## Historial y calendario

Se conserva el historial existente de GitHub. Los commits nuevos registran trabajo real de la fecha actual; no se recrean entregas atrasadas ni se alteran fechas. Los dos programas recibidos difieren entre revisión del 17 y revisión integradora del 18 de noviembre. Ambos fijan entrega y defensa final el **20 de noviembre de 2026**. Ver `docs/matriz_cumplimiento.md` y `docs/observaciones_docente.md`.

## Fuentes

- Tsanas, A. y Xifara, A. (2012). [Energy Efficiency, UCI](https://doi.org/10.24432/C51307), CC BY 4.0.
- [Scikit-learn: validación cruzada](https://scikit-learn.org/stable/modules/cross_validation.html), [K-Means y silhouette](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html), [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
- [Microsoft Learn: proyectos Power BI](https://learn.microsoft.com/power-bi/developer/projects/projects-overview) y [formato PBIR](https://learn.microsoft.com/power-bi/developer/projects/projects-report).
- Programas de trabajo y actividades restantes proporcionados por el estudiante, conservados en `docs/requisitos/`.
''',
'docs/etl_y_datamart.md':'''# ETL y Data Mart final

La base final es **REC_ECBD_Energia**, en SQL Server. `src/etl_sqlserver.py` genera el esquema y la carga autocontenida `sql/datamart.sql`. `DatasetOriginal` conserva las diez variables y un identificador por fila. El archivo Excel no se modifica.

## Flujo

1. Extraer Excel con Pandas y verificar SHA-256.
2. Validar columnas, tipos, valores finitos, categorías, faltantes y duplicados.
3. Conservar 768 filas: no hay motivos para imputar o eliminar. Crear identificadores, grupo de geometría y clase alta/baja.
4. Generar modelos y resultados: predicciones exclusivamente de prueba, cluster y componentes PCA.
5. Normalizar dimensiones, asignar llaves y cargar SQL Server dentro de una transacción.
6. Validar llaves, conteos y reconstrucción exacta del dataset original mediante EXCEPT en ambos sentidos.
7. Importar las tablas a Power BI; reproducir relaciones 1:N, con filtro del lado 1 al lado N.

## Relaciones

```mermaid
erDiagram
    DimGeometria ||--o{ HECHOS : id_geometria
    DimAcristalamiento ||--o{ HECHOS : id_acristalamiento
    DimOrientacion ||--o{ HECHOS : id_orientacion
    DimClase ||--o{ HECHOS : id_clase
    DimConjunto ||--o{ HECHOS : id_conjunto
    DimCluster ||--o{ HECHOS : id_cluster
```

El grano de HECHOS es una simulación por `id_registro`. Contiene Y1/Y2, predicciones, errores absolutos y PC1/PC2. Las predicciones de las 576 filas de entrenamiento son NULL por diseño; las 192 filas de prueba sí tienen predicción. Esto evita presentar evaluación de entrenamiento como prueba.

Las cargas son medidas no aditivas entre escenarios alternativos: se muestran medias. DimGeometria incluye altura y DimAcristalamiento incluye proporción y distribución; esto mantiene un esquema estrella. Los códigos X6/X8 se conservan sin inventar etiquetas cardinales. Las tablas de métricas son auxiliares, con grano propio por algoritmo/objetivo o componente; no se mezclan con HECHOS.

La carga es idempotente: reconstruye únicamente las tablas dedicadas de la base del proyecto. `SET XACT_ABORT ON` y TRY/CATCH revierten cambios ante fallos. `sql/validar_datamart.sql` comprueba el resultado. La evidencia de ejecución real está en `verificacion_sqlserver.json`.

El SQLite y los scripts antiguos se conservan como antecedente. El esquema final y la defensa utilizan `sql/datamart.sql` y `diagrama_estrella.svg`.
''',
'docs/guia_revision_proyecto.md':r'''# Guion para ejecutar y defender el proyecto

## Demostración de 10-12 minutos

1. **Problema (1 min).** Explicar la relación entre geometría y cargas. Cada fila es una simulación; Y1/Y2 no son años. No prometer ahorro real.
2. **Datos y calidad (1 min).** Abrir el Excel original y el notebook AE1. Mostrar 768 filas, diez variables, ausencia de nulos/duplicados y una gráfica interpretada.
3. **ETL (2 min).** Abrir AE2. Comparar columnas originales y derivadas. Explicar por qué se conservan los atípicos sin justificación para borrarlos.
4. **SQL Server (2 min).** En SSMS conectar a `localhost` con Windows. Abrir la base `REC_ECBD_Energia`, expandir Tablas y mostrar `dbo.HECHOS`, `dbo.DimGeometria` y `dbo.DimAcristalamiento`. Ejecutar `sql/consulta_defensa.sql` y mostrar las seis llaves 1:N y 768 hechos.
5. **Supervisado (2 min).** Explicar X/y, separación por geometría, optimización dentro de entrenamiento y diferencia entre MAE y accuracy. Reconocer 40 falsos negativos de clase alta.
6. **No supervisado (2 min).** Explicar StandardScaler, por qué no usar Y1/Y2 ni códigos nominales, selección k=2 por silhouette y varianza 82.38% de PC1/PC2.
7. **Power BI y decisiones (2 min).** Recorrer las cuatro páginas. Filtrar por altura; abrir Vista de modelo para mostrar la estrella. Presentar tres conclusiones y dos recomendaciones del informe final.

## Preguntas esenciales

- **¿Por qué estrella?** Las dimensiones se desnormalizan para consulta y visualización: altura está en geometría y los atributos de cristal en acristalamiento. Todas se conectan directamente a HECHOS.
- **¿Cuál es el grano?** Una configuración simulada por id_registro. No existen fechas de consumo real.
- **¿Por qué no sumar Y1/Y2?** Son cargas de diseños alternativos, no consumos aditivos de un edificio durante varios periodos.
- **¿Por qué no eliminaste filas?** Las comprobaciones no identifican errores que lo justifiquen; se preserva la fuente.
- **¿Cómo evitas fuga?** Las variantes de la misma geometría permanecen juntas. Escalamiento y codificación se ajustan en cada fold. La prueba no selecciona hiperparámetros.
- **¿Alta significa ineficiente?** No necesariamente. Es una clase didáctica si Y1 >= 25; no una certificación.
- **¿Qué representa silhouette?** Cohesión y separación de clusters; no precisión supervisada.
- **¿Qué representa PCA?** Combinaciones lineales de variables estandarizadas; la proyección 2D conserva 82.38% de la varianza.
- **¿Qué limitaciones hay?** Solo 12 geometrías simuladas; altura y compacidad están confundidas; clasificación con falsos negativos; falta validación externa.

## Antes de la revisión

Ejecutar los notebooks y abrir Power BI con SQL Server activo. Comprobar el último commit en GitHub y tener los PDF accesibles. Registrar las observaciones reales en `observaciones_docente.md`; preparar explicación propia de las decisiones. Los archivos no sustituyen la defensa oral.
''',
'docs/matriz_cumplimiento.md':'''# Matriz de cumplimiento y trazabilidad

Actualización: 16 de noviembre de 2026. Esta matriz describe evidencias técnicas, no calificaciones ni entregas acreditadas.

| Requisito | Evidencia verificable |
|---|---|
| Mismo proyecto y dataset | Energy Efficiency; raw original conservado; mismo repositorio GitHub |
| Exploración con Pandas | Notebook U2_AE1, 22 celdas de código |
| Diccionario, tipo, clasificación, unidad y utilidad | Notebook U2_AE1 y docs/diccionario_datos.md |
| Nulos, duplicados, inconsistencias, atípicos | U2_AE1; reporte_calidad_datos.json |
| Estadística de 3 variables y 3 gráficas interpretadas | U2_AE1 e informe de diagnóstico |
| Limpieza y transformación justificadas | U2_AE2; no imputaciones/eliminaciones injustificadas |
| Original frente a procesado | assert_frame_equal en U2_AE2 y SHA-256 |
| ETL y dataset procesado | src/preparacion_datos.py, src/etl_sqlserver.py, data/processed/ |
| HECHOS, dimensiones, PK/FK, medidas | SQL Server REC_ECBD_Energia; sql/datamart.sql |
| Modelo estrella y diagrama | docs/diagrama_estrella.svg; 6 relaciones SQL y Power BI |
| Regresión con MAE y RMSE/R² | U3; metricas_regresion.csv |
| Clasificación con accuracy, precision, recall, F1 y matriz | U3; metricas_clasificacion.csv; reporte_clasificacion.json |
| Comparación, optimización y relevancia | GridSearchCV/GroupKFold; validacion_*.csv; importancia_variables.csv |
| K-Means, elección k, estandarización | U4; evaluacion_clusters.csv; k=2 y silhouette=0.5244 |
| Perfiles e interpretación | perfiles_clusters.csv, informe U4 |
| PCA y varianza explicada | U4, varianza_pca.csv, cargas_pca.csv y figuras |
| Modelos serializados | modelos/*.joblib |
| Dashboard Power BI e indicadores | dashboard/Energia.pbip; páginas descriptiva, supervisada, patrones y modelo |
| Storytelling, 3 conclusiones, 2 recomendaciones | Informe_Final.pdf; página 4 del dashboard; guía de defensa |
| Notebooks ejecutables | docs/verificacion_notebooks.json: 6 notebooks, cero errores |
| Informes PDF por actividad y final | docs/Gonzalez_Coronado_Ulises_U*.pdf y docs/Informe_Final.pdf |
| README y repositorio | README.md y commits reales de avance |
| Observaciones del docente | Pendientes de recibir; observaciones_docente.md |
| Defensa y dominio personal | Debe realizarla el estudiante; guía de práctica preparada |

## Fechas de los documentos

El programa de trabajo continuo indica revisión 1 el 10, corte el 16 a las 23:59, revisión 2 el 17 y cierre el 20. El programa de actividades restantes fija UIV el 18 a las 12:00 y revisión integradora el mismo 18. No se elimina esta discrepancia ni se inventa una fecha confirmada. El cierre coincide en el 20 de noviembre de 2026. Confirmar con el docente cuál convocatoria aplica; preparar el proyecto para la fecha más temprana.
''',
'docs/observaciones_docente.md':'''# Registro de observaciones y correcciones

No se han proporcionado observaciones de la revisión del 17/18 de noviembre de 2026. Este registro no acredita que la revisión ni la defensa hayan ocurrido.

| Fecha real | Observación del docente | Cambio realizado | Evidencia / commit | Estado |
|---|---|---|---|---|

Completar después de la revisión con observaciones reales. Registrar la corrección y su verificación antes de la entrega final del 20 de noviembre.
''',
'dashboard/README.md':r'''# Dashboard principal en Power BI

El proyecto editable es `Energia.pbip`, con `Energia.Report/` (PBIR) y `Energia.SemanticModel/` (modelo tabular). Las tablas se importan desde **SQL Server localhost, base REC_ECBD_Energia**, mediante Power Query. No contiene contraseñas.

## Abrir y actualizar

1. Ejecutar `python -m src.etl_sqlserver --cargar` desde la raíz, con SQL Server activo.
2. Abrir `dashboard/Energia.pbip` en Power BI Desktop. Conservar las dos carpetas junto al PBIP.
3. Usar **Actualizar**. Conectar mediante la cuenta Windows con acceso a SQL Server.
4. Si cambias de equipo/instancia, editar el servidor en Power Query; todas las consultas comparten la misma base.
5. Guardar como PBIX para llevar una copia con los datos importados. El PBIP conserva el código del informe y del modelo para GitHub; su caché local `.pbi/` no se versiona.

## Páginas

1. **Edificios y demanda energética:** 768 simulaciones, 12 geometrías, medias de cargas, altura, compacidad y acristalamiento; segmentación por altura.
2. **Predicción y evaluación:** MAE, accuracy, F1, real frente a predicho, matriz de confusión y referencia de regresión. Las predicciones de entrenamiento son nulas; solo se evalúan 192 casos de prueba.
3. **Patrones y componentes:** selección de k, silhouette, perfiles, dispersión PCA y varianza explicada.
4. **Del Excel al conocimiento:** ETL, estructura estrella, controles de calidad, conclusiones y recomendaciones.

## Modelo real

Abrir **Vista de modelo**. HECHOS se conecta directamente a DimGeometria, DimOrientacion, DimAcristalamiento, DimClase, DimConjunto y DimCluster. Son seis relaciones 1:N con filtro simple, iguales a las llaves de SQL Server.

Las tablas de métricas globales permanecen separadas: muestran la evaluación fija sobre prueba, no métricas recalculadas por cada filtro exploratorio. Las medidas de cargas utilizan medias. `F1 macro global` se etiqueta como global para evitar una interpretación filtrada.

El generador `src/generar_powerbi.py` permite reconstruir el proyecto. **Regenerarlo reemplaza los archivos fuente del informe**: guardar primero cualquier personalización manual. `src/validar_powerbi.py` verifica los JSON contra esquemas públicos de Microsoft; esta validación no sustituye abrir, actualizar y revisar los gráficos.

## Panel complementario

`app.py` es el panel Streamlit anterior. Puede abrirse con `python -m src.iniciar_panel`, pero el dashboard principal de la entrega es Power BI. El SQLite se conserva como evidencia local histórica, no como sustituto de SQL Server.
''',
'sql/consulta_defensa.sql':'''USE [REC_ECBD_Energia];
GO
-- 1. Hechos y medidas al grano de una simulacion.
SELECT TOP (10) * FROM dbo.HECHOS ORDER BY id_registro;
SELECT COUNT(*) simulaciones, AVG(Y1) calefaccion_media, AVG(Y2) refrigeracion_media FROM dbo.HECHOS;
-- 2. Estrella: Altura dentro de DimGeometria -> HECHOS.
SELECT g.altura, COUNT(*) simulaciones, AVG(h.Y1) calefaccion_media, AVG(h.Y2) refrigeracion_media
FROM dbo.HECHOS h JOIN dbo.DimGeometria g ON h.id_geometria=g.id_geometria
GROUP BY g.altura;
-- 3. Relaciones físicas; las seis FK directas a HECHOS están implementadas.
SELECT fk.name, OBJECT_NAME(fk.parent_object_id) tabla_hija,
OBJECT_NAME(fk.referenced_object_id) tabla_padre, fk.is_disabled, fk.is_not_trusted
FROM sys.foreign_keys fk;
-- 4. Comparacion original contra reconstruccion dimensional.
SELECT * FROM dbo.DatasetOriginal EXCEPT SELECT * FROM dbo.vDatasetReconstruido;
SELECT * FROM dbo.vDatasetReconstruido EXCEPT SELECT * FROM dbo.DatasetOriginal;
-- 5. Prueba supervisada y agrupamiento.
SELECT * FROM dbo.MetricasRegresion;
SELECT * FROM dbo.MetricasClasificacion;
SELECT * FROM dbo.PerfilesClusters;
'''
    }
    for ruta, texto in archivos.items():
        p=ROOT/ruta;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(texto,encoding='utf-8')
    print('README, guías y matriz de cumplimiento actualizados.')

if __name__=='__main__': generar()

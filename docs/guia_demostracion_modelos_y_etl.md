# Guía de demostración: modelos, Data Warehouse, ETL y Power BI

Esta guía indica qué abrir y qué explicar durante la revisión. Las fechas usadas para el corte 70/30 son sintéticas: demuestran el flujo temporal, no fechas de consumo reales.

## 1. Los tres modelos finales

| Propuesta | Nombre exacto | Tipo y función | Resultado / archivo |
|---|---|---|---|
| Regresión | `Ridge(alpha=10.0)` | Modelo supervisado de regresión lineal con regularización L2. Recibe X1-X8 y estima dos valores continuos: Y1 (carga de calefacción) y Y2 (carga de refrigeración). | MAE: Y1=2.2025, Y2=2.3316. `modelos/modelo_regresion_cargas.joblib` |
| Clasificación | `LogisticRegression(C=0.1)` | Modelo supervisado de clasificación binaria. Recibe X1-X8 y predice `baja` o `alta`; `alta` significa Y1 >= 25, una regla didáctica. | Accuracy/F1=1.000 en la prueba futura simulada. `modelos/modelo_clasificacion_calefaccion.joblib` |
| Patrones | `KMeans(n_clusters=2, n_init=30, random_state=42)` + `PCA()` | Modelo no supervisado. K-Means agrupa diseños físicamente semejantes sin usar Y1/Y2. PCA reduce las seis variables físicas estandarizadas a componentes para visualizar y resumir la información. | k=2, silhouette=0.5244; PC1+PC2=82.38%. `modelos/modelo_kmeans_pca.joblib` |

Los modelos supervisados son `Pipeline`: estandarizan X1-X5/X7 y convierten X6/X8 con `OneHotEncoder`. Así los códigos nominales no se tratan como escalas numéricas.

`RandomForest` se comparó durante la selección, pero no es el modelo final serializado: Ridge y Logística tuvieron el mejor resultado de validación dentro del entrenamiento.

## 2. Dónde se ve cada evidencia

| Qué quieres ver | Ubicación |
|---|---|
| Código y selección supervisada | `src/modelos_supervisados.py` y `notebooks/Gonzalez_Coronado_Ulises_U3_AnalisisSupervisado.ipynb` |
| Código K-Means/PCA | `src/modelos_no_supervisados.py` y `notebooks/Gonzalez_Coronado_Ulises_U4_AnalisisNoSupervisado.ipynb` |
| Archivos entrenados | Carpeta `modelos/` (`.joblib`) |
| Métricas, matriz y gráficas | `docs/metricas_*.csv`, `docs/reporte_clasificacion.json`, `docs/figuras/` |
| Predicción reproducible de un caso reservado | `src/predecir_cargas.py` |
| Tablas y gráficas de exposición | `dashboard/Energia.pbip` |

## 3. Mostrar que los modelos funcionan

1. Abre el proyecto en VS Code y muestra la carpeta `modelos/`: ahí están los tres artefactos entrenados.
2. Abre el notebook U3. Explica que el 70% inicial (537 filas) entrena y el 30% final (231 filas) es la prueba futura simulada. Muestra la tabla de métricas, la gráfica real-vs-predicha y la matriz de confusión.
3. En una terminal de VS Code ejecuta este ejemplo reproducible:

```powershell
.\.venv\Scripts\python.exe -m src.predecir_cargas
```

El programa abre Ridge y Logística, toma un registro reservado y muestra Y1/Y2 reales frente a predichas, además de la clase real y predicha.

4. Abre el notebook U4. Muestra la tabla de `k=2..8`, explica que se eligió el silhouette más alto, y enseña PCA: cada punto es un edificio y el color es su cluster.
5. Aclara la limitación: los resultados perfectos de clasificación pertenecen a una prueba construida con fechas sintéticas; no son una garantía para edificios reales.

## 4. Dónde está el Data Warehouse y el Data Mart

En este proyecto no hay un servidor en la nube. El **Data Warehouse local** es la base de SQL Server:

```text
Servidor: localhost
Base de datos: REC_ECBD_Energia
```

El **Data Mart** es el modelo estrella dentro de esa base. Su tabla central es `dbo.HECHOS`; sus siete dimensiones son `DimGeometria`, `DimOrientacion`, `DimAcristalamiento`, `DimClase`, `DimConjunto`, `DimCluster` y `DimTime`. `DatasetOriginal` conserva la copia cargada del origen y las tablas `Metricas*`, `MatrizConfusion`, `VarianzaPCA` y `PerfilesClusters` son evidencia de los análisis.

En SSMS abre: `localhost` > **Databases** > **REC_ECBD_Energia** > **Tables**. Para mostrar el diagrama, abre **Database Diagrams**; para demostrar el contenido ejecuta `sql/consulta_defensa.sql`.

## 5. Demostrar la carga FULL del ETL

1. Confirma que SQL Server está activo y abre una terminal en la raíz del repositorio.
2. Ejecuta la limpieza, que solo usa `DELETE` en la base del proyecto y respeta el orden de llaves foráneas:

```powershell
sqlcmd -S localhost -E -C -b -f 65001 -i sql/limpiar_datamart_full.sql
```

3. Ejecuta el análisis y la recarga completa:

```powershell
.\.venv\Scripts\python.exe -m src.ejecutar_proyecto
.\.venv\Scripts\python.exe -m src.etl_sqlserver --cargar
```

4. Enseña la salida: debe indicar `HECHOS|768`, `Llaves foraneas activas|7`, `Predicciones de prueba|231` y `RECONSTRUCCION_EXACTA_OK`.
5. En SSMS ejecuta `sql/consulta_defensa.sql`: muestra HECHOS, las siete relaciones, métricas y el rango de `DimTime`.

El Job de SQL Server Agent se llama `ECBD_Carga_FULL_Energia` y automatiza exactamente la secuencia **DELETE → análisis → ETL → recarga**. Para ejecutarlo desde SQL Server Agent, el servicio Agent debe estar iniciado.

## 6. Demostrar Power BI

1. Abre `dashboard/Energia.pbip` y pulsa **Actualizar** después de la carga FULL.
2. Página 1: usa los slicers **fecha** y **altura**. Explica que cada gráfica muestra promedios de Y1/Y2; lee el texto **QUÉ REPRESENTA** debajo de cada visual.
3. Página 2: muestra el MAE, la dispersión real-vs-predicha, la matriz de confusión y la tabla ampliada de métricas. Explica que las métricas pertenecen a las 231 filas de prueba futura simulada.
4. Página 3: muestra la selección de k, el PCA con colores por cluster, la varianza explicada y la tabla ampliada de perfiles.
5. Página 4: abre la explicación del modelo estrella y el ciclo FULL. Finalmente abre **Vista de modelo** y señala las siete relaciones hacia HECHOS.

No es necesario abrir los `.joblib` con doble clic: se verifican mediante los notebooks y `src/predecir_cargas.py`.

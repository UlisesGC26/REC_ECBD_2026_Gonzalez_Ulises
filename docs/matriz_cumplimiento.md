# Matriz de cumplimiento y trazabilidad

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
| Copo de nieve y diagrama | docs/diagrama_copo_nieve.svg; 9 relaciones SQL y Power BI |
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

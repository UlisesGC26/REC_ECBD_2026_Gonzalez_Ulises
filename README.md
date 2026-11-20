# Evaluación de eficiencia energética de edificios

**Ulises González Coronado · Recursamiento ECBD 2026**
Universidad Tecnológica de Tula-Tepeji · Docente: Ing. José Luis Herrera Gallardo.
Actualización técnica: **20 de noviembre de 2026**.

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
| Modelo estrella y carga FULL | `sql/datamart.sql`, `sql/limpiar_datamart_full.sql`, `sql/job_carga_full.sql`, `docs/diagrama_estrella.svg` |
| Regresión y clasificación | `src/modelos_supervisados.py`, `modelos/`, `docs/metricas_*.csv` |
| K-Means y PCA | `src/modelos_no_supervisados.py`, `docs/resultados_no_supervisados.json` |
| Power BI | `dashboard/Energia.pbip` y sus carpetas Report/SemanticModel |
| Notebooks ejecutados | Seis notebooks; `docs/verificacion_notebooks.json` registra cero errores |
| Informes | Cuatro PDF por actividad y `docs/Informe_Final.pdf` |
| Defensa y requisitos | `docs/guia_revision_proyecto.md`, `docs/matriz_cumplimiento.md` |
| Presentación de defensa | `docs/Defensa_Proyecto.pptx` |
| Guía de demostración | `docs/guia_demostracion_modelos_y_etl.md` |

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

Para demostrar la carga FULL solicitada, primero limpia los registros del Data Mart y luego vuelve a ejecutar el ETL. No ejecutar esta limpieza en otra base:

```powershell
sqlcmd -S localhost -E -C -b -f 65001 -i sql/limpiar_datamart_full.sql
.\.venv\Scripts\python.exe -m src.ejecutar_proyecto
.\.venv\Scripts\python.exe -m src.etl_sqlserver --cargar
```

El Job de SQL Server Agent `ECBD_Carga_FULL_Energia` realiza la misma secuencia automáticamente cuando el servicio SQL Server Agent está iniciado.

También puede ejecutarse el SQL autocontenido, sin Python:

```powershell
sqlcmd -S localhost -E -C -b -f 65001 -i sql/datamart.sql
sqlcmd -S localhost -E -C -b -f 65001 -i sql/validar_datamart.sql
```

`-E` usa autenticación Windows. `-C` permite el certificado local de la instancia de desarrollo. Los scripts se destinan exclusivamente a la base del proyecto.

## Abrir Power BI

Abrir `dashboard/Energia.pbip`. Mantener junto al archivo las carpetas `Energia.Report` y `Energia.SemanticModel`. El 17 de noviembre se abrió y actualizó en Power BI Desktop contra SQL Server local: se verificaron sus cuatro páginas y el filtro de altura. Actualizar datos desde SQL Server con autenticación Windows. Si se requiere el formato monolítico, usar **Archivo > Guardar como > PBIX**. Consultar `dashboard/README.md` para las páginas y comprobaciones.

El modelo tiene **HECHOS** con 768 filas y siete relaciones 1:N de filtro simple. Es una estrella: todas las dimensiones se conectan directamente a HECHOS; altura está integrada en geometría, los atributos de cristal en acristalamiento y `DimTime` aporta fecha, mes, trimestre y año para el ETL y los slicers. Las fechas son sintéticas: no se presentan como observaciones originales. Las tablas de métricas globales quedan separadas para no confundir medidas del conjunto de prueba con filtros exploratorios.

## Resultados reproducidos

| Modelo / medida | Resultado |
|---|---:|
| Ridge, MAE Y1 | 2.2025 |
| Ridge, MAE Y2 | 2.3316 |
| R² Y1 / Y2 | 0.9186 / 0.8905 |
| Logística, accuracy | 100.00% |
| Precision macro / Recall macro | 1.0000 / 1.0000 |
| F1 macro | 1.0000 |
| K-Means, k seleccionado | 2 |
| Silhouette | 0.5244 |
| Varianza PC1 + PC2 | 82.38% |

Entrenamiento: 537 filas (70% inicial de la fecha sintética). Prueba: 231 filas posteriores (30% futuro simulado). El ajuste se selecciona mediante GroupKFold de tres particiones dentro del entrenamiento. La clasificación alta/baja usa un corte didáctico fijo Y1 >= 25. El 100% observado pertenece a este conjunto sintético y no demuestra generalización con datos reales.

K-Means y PCA utilizan X1-X5 y X7 estandarizadas, sin las cargas ni los códigos nominales. Se comparan k=2..8. Los dos grupos contienen 384 casos cada uno y separan alturas y geometrías correlacionadas. La estabilidad entre semillas no demuestra validez externa.

## Notebooks y documentos

- `Gonzalez_Coronado_Ulises_U2_AE1_Exploracion.ipynb`: diagnóstico, diccionario, estadística y gráficos interpretados.
- `Gonzalez_Coronado_Ulises_U2_AE2_ETL.ipynb`: comparación original/procesado, carga SQL y modelo estrella.
- `Gonzalez_Coronado_Ulises_U3_AnalisisSupervisado.ipynb`: selección, ajuste, métricas, importancia e interpretación.
- `Gonzalez_Coronado_Ulises_U4_AnalisisNoSupervisado.ipynb`: selección de k, perfiles, PCA y conclusiones.
- `01_preparacion_datos.ipynb` y `02_analisis_supervisado.ipynb`: evidencias iniciales conservadas y verificadas.

Los cuatro informes de actividad están en `docs/`, junto con `Informe_Final.pdf`, sus fuentes Markdown y `Defensa_Proyecto.pptx` para presentar el proyecto. Para regenerar informes: instalar `requirements_informes.txt` y ejecutar `python -m src.generar_informes`. El generador usa Arial de Windows. La revisión visual se apoya en `python -m src.revisar_pdfs`.

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

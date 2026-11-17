# Dashboard principal en Power BI

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
4. **Del Excel al conocimiento:** ETL, estructura copo de nieve, controles de calidad, conclusiones y recomendaciones.

## Modelo real

Abrir **Vista de modelo**. HECHOS se conecta a DimGeometria, DimOrientacion, DimAcristalamiento, DimClase, DimConjunto y DimCluster. DimGeometria se conecta a DimAltura. DimAcristalamiento se conecta a DimPorcentajeCristal y DimDistribucion. Son nueve relaciones 1:N con filtro simple, iguales a las llaves de SQL Server.

Las tablas de métricas globales permanecen separadas: muestran la evaluación fija sobre prueba, no métricas recalculadas por cada filtro exploratorio. Las medidas de cargas utilizan medias. `F1 macro global` se etiqueta como global para evitar una interpretación filtrada.

El generador `src/generar_powerbi.py` permite reconstruir el proyecto. **Regenerarlo reemplaza los archivos fuente del informe**: guardar primero cualquier personalización manual. `src/validar_powerbi.py` verifica los JSON contra esquemas públicos de Microsoft; esta validación no sustituye abrir, actualizar y revisar los gráficos.

## Comprobación realizada el 17 de noviembre de 2026

El PBIP se abrió en Power BI Desktop y se actualizó contra `localhost;REC_ECBD_Energia` usando autenticación Windows. Se verificaron las cuatro páginas y las 17 tablas importadas. El filtro de altura respondió correctamente: al seleccionar **3.50**, el tablero pasó de 768 a 384 simulaciones y mostró Y1=13.34 y Y2=16.07. Las capturas están en `docs/evidencia_powerbi/`; el registro está en `docs/verificacion_panel.json`.

## Panel complementario

`app.py` es el panel Streamlit anterior. Puede abrirse con `python -m src.iniciar_panel`, pero el dashboard principal de la entrega es Power BI. El SQLite se conserva como evidencia local histórica, no como sustituto de SQL Server.

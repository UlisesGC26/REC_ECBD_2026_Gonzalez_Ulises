# Dashboard principal en Power BI

`Energia.pbip` es el proyecto editable; `Energia.Report/` contiene el informe y `Energia.SemanticModel/` el modelo tabular. Las tablas se importan desde **SQL Server localhost, base REC_ECBD_Energia**, mediante Power Query y sin contraseñas.

## Abrir y actualizar

1. Ejecutar `python -m src.etl_sqlserver --cargar` desde la raíz con SQL Server activo.
2. Abrir `dashboard/Energia.pbip` en Power BI Desktop, conservando sus dos carpetas junto al PBIP.
3. Elegir **Actualizar** y conectar con la cuenta Windows autorizada para SQL Server.
4. Guardar como PBIX si se necesita una copia portable con los datos importados.

## Páginas

1. Edificios y demanda energética: 768 simulaciones, altura, compacidad y acristalamiento.
2. Predicción y evaluación: MAE, accuracy, F1, valores reales/predichos y matriz de confusión.
3. Patrones y componentes: K-Means, silhouette, perfiles, PCA y varianza.
4. Del Excel al conocimiento: ETL, modelo estrella, calidad, conclusiones y recomendaciones.

## Modelo real en estrella

Abrir la **Vista de modelo**. `HECHOS` se conecta directamente a `DimGeometria`, `DimOrientacion`, `DimAcristalamiento`, `DimClase`, `DimConjunto` y `DimCluster`: son seis relaciones 1:N de filtro simple, iguales a las llaves de SQL Server. `DimGeometria` ya contiene altura y `DimAcristalamiento` ya contiene proporción y distribución de cristal; no hay relaciones entre dimensiones.

Las tablas de métricas globales quedan separadas porque representan la evaluación fija de prueba. Las cargas se muestran como medias. `src/generar_powerbi.py` reconstruye el PBIP y `src/validar_powerbi.py` valida sus JSON; después de regenerar, abrir y actualizar el proyecto para revisarlo visualmente.

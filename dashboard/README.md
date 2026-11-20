# Dashboard principal en Power BI

`Energia.pbip` es el proyecto editable; `Energia.Report/` contiene el informe y `Energia.SemanticModel/` el modelo tabular. Las tablas se importan desde **SQL Server localhost, base REC_ECBD_Energia**, mediante Power Query y sin contraseñas.

## Abrir y actualizar

1. Para una carga FULL demostrable, ejecutar `sql/limpiar_datamart_full.sql` con `sqlcmd` y después `python -m src.etl_sqlserver --cargar` desde la raíz con SQL Server activo.
2. Abrir `dashboard/Energia.pbip` en Power BI Desktop, conservando sus dos carpetas junto al PBIP.
3. Elegir **Actualizar** y conectar con la cuenta Windows autorizada para SQL Server.
4. Guardar como PBIX si se necesita una copia portable con los datos importados.

## Páginas

1. Edificios y demanda energética: promedios de Y1/Y2 por altura, compacidad y acristalamiento. Cada gráfica incluye una nota **QUÉ REPRESENTA** y evita interpretar asociación como causalidad.
2. Predicción y evaluación: MAE, accuracy, F1, valores reales/predichos y matriz de confusión. Las notas aclaran que se trata de las 231 filas de prueba futura simulada y cómo leer el error.
3. Patrones y componentes: K-Means, silhouette, perfiles, PCA y varianza. Las notas definen cada punto, criterio y porcentaje mostrado.
4. Del Excel al conocimiento: ETL FULL, modelo estrella, calidad, conclusiones y recomendaciones.

## Modelo real en estrella

Abrir la **Vista de modelo**. `HECHOS` se conecta directamente a `DimGeometria`, `DimOrientacion`, `DimAcristalamiento`, `DimClase`, `DimConjunto`, `DimCluster` y `DimTime`: son siete relaciones 1:N de filtro simple. `DimTime` contiene fechas sintéticas diarias solo para demostrar el ETL temporal y el slicer de fecha; no son observaciones temporales reales.

La página 1 incluye slicers de **fecha** y **altura**. El corte temporal usa el 70% inicial de fechas para entrenamiento y el 30% final para prueba futura simulada.

Las tablas de métricas globales quedan separadas porque representan la evaluación fija de prueba. Las cargas se muestran como medias. `src/generar_powerbi.py` reconstruye el PBIP y `src/validar_powerbi.py` valida sus JSON; después de regenerar, abrir y actualizar el proyecto para revisarlo visualmente. La página 4 deja explícita la secuencia operativa: **DELETE del Data Mart → ETL → recarga completa → Actualizar en Power BI**.

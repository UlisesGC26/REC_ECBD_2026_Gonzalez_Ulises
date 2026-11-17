# Guion para ejecutar y defender el proyecto

## Demostración de 10-12 minutos

1. **Problema (1 min).** Explicar la relación entre geometría y cargas. Cada fila es una simulación; Y1/Y2 no son años. No prometer ahorro real.
2. **Datos y calidad (1 min).** Abrir el Excel original y el notebook AE1. Mostrar 768 filas, diez variables, ausencia de nulos/duplicados y una gráfica interpretada.
3. **ETL (2 min).** Abrir AE2. Comparar columnas originales y derivadas. Explicar por qué se conservan los atípicos sin justificación para borrarlos.
4. **SQL Server (2 min).** En SSMS conectar a `localhost` con Windows. Abrir la base `REC_ECBD_Energia`, expandir Tablas y mostrar `dbo.HECHOS`, `dbo.DimGeometria` y `dbo.DimAcristalamiento`. Ejecutar `sql/consulta_defensa.sql` y mostrar las seis llaves 1:N directas a HECHOS y 768 hechos.
5. **Supervisado (2 min).** Explicar X/y, separación por geometría, optimización dentro de entrenamiento y diferencia entre MAE y accuracy. Reconocer 40 falsos negativos de clase alta.
6. **No supervisado (2 min).** Explicar StandardScaler, por qué no usar Y1/Y2 ni códigos nominales, selección k=2 por silhouette y varianza 82.38% de PC1/PC2.
7. **Power BI y decisiones (2 min).** Recorrer las cuatro páginas. Filtrar por altura; abrir Vista de modelo para mostrar la estrella. Presentar tres conclusiones y dos recomendaciones del informe final.

## Preguntas esenciales

- **¿Por qué estrella?** Altura está integrada en DimGeometria y proporción/distribución en DimAcristalamiento. Las seis dimensiones se conectan directamente a HECHOS para simplificar consulta y visualización.
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

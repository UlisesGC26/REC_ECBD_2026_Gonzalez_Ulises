/* Limpieza controlada previa a una carga FULL.
   Úsalo SOLO en la base local del proyecto REC_ECBD_Energia.
   Respeta primero las tablas que dependen de dimensiones y después las dimensiones.
   Después ejecutar el ETL FULL: python -m src.ejecutar_proyecto; python -m src.etl_sqlserver --cargar
*/
USE [REC_ECBD_Energia];
GO
SET NOCOUNT ON;
SET XACT_ABORT ON;
GO
BEGIN TRY
    BEGIN TRANSACTION;

    -- Tabla de hechos antes que sus dimensiones (respeta las siete llaves foráneas).
    DELETE FROM dbo.HECHOS;

    -- Resultados y tablas auxiliares generados por los modelos.
    DELETE FROM dbo.MatrizConfusion;
    DELETE FROM dbo.ImportanciaVariables;
    DELETE FROM dbo.PerfilesClusters;
    DELETE FROM dbo.VarianzaPCA;
    DELETE FROM dbo.EvaluacionClusters;
    DELETE FROM dbo.MetricasClasificacion;
    DELETE FROM dbo.MetricasRegresion;

    -- Dimensiones de la estrella.
    DELETE FROM dbo.DimTime;
    DELETE FROM dbo.DimCluster;
    DELETE FROM dbo.DimConjunto;
    DELETE FROM dbo.DimClase;
    DELETE FROM dbo.DimAcristalamiento;
    DELETE FROM dbo.DimOrientacion;
    DELETE FROM dbo.DimGeometria;

    -- Origen cargado dentro de la base del proyecto; el Excel original no se modifica.
    DELETE FROM dbo.DatasetOriginal;

    COMMIT TRANSACTION;
    SELECT 'LIMPIEZA_FULL_OK' AS resultado;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;
GO

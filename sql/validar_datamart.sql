USE [REC_ECBD_Energia];
GO
SET NOCOUNT ON;
IF EXISTS (SELECT * FROM dbo.DatasetOriginal EXCEPT SELECT * FROM dbo.vDatasetReconstruido)
 OR EXISTS (SELECT * FROM dbo.vDatasetReconstruido EXCEPT SELECT * FROM dbo.DatasetOriginal)
 THROW 51002, 'La reconstruccion difiere del dataset original', 1;
IF (SELECT COUNT(*) FROM sys.foreign_keys WHERE parent_object_id=OBJECT_ID(N'dbo.HECHOS') AND is_disabled=0 AND is_not_trusted=0) <> 6
 THROW 51003, 'HECHOS debe tener seis llaves foraneas activas', 1;
SELECT 'HECHOS' tabla, COUNT(*) filas FROM dbo.HECHOS;
SELECT 'DatasetOriginal' tabla, COUNT(*) filas FROM dbo.DatasetOriginal;
SELECT 'Llaves foraneas activas' control, COUNT(*) valor FROM sys.foreign_keys WHERE is_disabled=0 AND is_not_trusted=0;
SELECT 'Predicciones de prueba' control, COUNT(Y1_predicha) valor FROM dbo.HECHOS;
SELECT AVG(Y1) calefaccion_media, AVG(Y2) refrigeracion_media FROM dbo.HECHOS;
SELECT 'RECONSTRUCCION_EXACTA_OK' resultado;

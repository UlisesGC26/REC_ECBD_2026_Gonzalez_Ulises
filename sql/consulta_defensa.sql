USE [REC_ECBD_Energia];
GO
-- 1. Hechos y medidas al grano de una simulacion.
SELECT TOP (10) * FROM dbo.HECHOS ORDER BY id_registro;
SELECT COUNT(*) simulaciones, AVG(Y1) calefaccion_media, AVG(Y2) refrigeracion_media FROM dbo.HECHOS;
-- 2. Recorrido del copo de nieve: Altura -> Geometria -> HECHOS.
SELECT a.altura, COUNT(*) simulaciones, AVG(h.Y1) calefaccion_media, AVG(h.Y2) refrigeracion_media
FROM dbo.HECHOS h JOIN dbo.DimGeometria g ON h.id_geometria=g.id_geometria
JOIN dbo.DimAltura a ON g.id_altura=a.id_altura GROUP BY a.altura;
-- 3. Relaciones fisicas; las nueve FK estan implementadas.
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

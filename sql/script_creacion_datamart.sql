-- Esquema de referencia. Para crear y cargar ejecutar datamart.sql.
USE [REC_ECBD_Energia];
GO
CREATE TABLE dbo.[DatasetOriginal] (
    [id_registro] INT NOT NULL,
    [X1] FLOAT NOT NULL,
    [X2] FLOAT NOT NULL,
    [X3] FLOAT NOT NULL,
    [X4] FLOAT NOT NULL,
    [X5] FLOAT NOT NULL,
    [X6] INT NOT NULL,
    [X7] FLOAT NOT NULL,
    [X8] INT NOT NULL,
    [Y1] FLOAT NOT NULL,
    [Y2] FLOAT NOT NULL,
    CONSTRAINT [PK_DatasetOriginal] PRIMARY KEY ([id_registro])
);
CREATE TABLE dbo.[DimGeometria] (
    [id_geometria] INT NOT NULL,
    [compacidad] FLOAT NOT NULL,
    [superficie] FLOAT NOT NULL,
    [area_pared] FLOAT NOT NULL,
    [area_techo] FLOAT NOT NULL,
    [altura] FLOAT NOT NULL,
    CONSTRAINT [PK_DimGeometria] PRIMARY KEY ([id_geometria])
);
CREATE TABLE dbo.[DimOrientacion] (
    [id_orientacion] INT NOT NULL,
    [orientacion] NVARCHAR(120) NOT NULL,
    CONSTRAINT [PK_DimOrientacion] PRIMARY KEY ([id_orientacion])
);
CREATE TABLE dbo.[DimAcristalamiento] (
    [id_acristalamiento] INT NOT NULL,
    [proporcion_cristal] FLOAT NOT NULL,
    [distribucion_codigo] INT NOT NULL,
    CONSTRAINT [PK_DimAcristalamiento] PRIMARY KEY ([id_acristalamiento])
);
CREATE TABLE dbo.[DimClase] (
    [id_clase] INT NOT NULL,
    [clase] NVARCHAR(120) NOT NULL,
    [regla] NVARCHAR(120) NOT NULL,
    CONSTRAINT [PK_DimClase] PRIMARY KEY ([id_clase])
);
CREATE TABLE dbo.[DimConjunto] (
    [id_conjunto] INT NOT NULL,
    [conjunto] NVARCHAR(120) NOT NULL,
    CONSTRAINT [PK_DimConjunto] PRIMARY KEY ([id_conjunto])
);
CREATE TABLE dbo.[DimCluster] (
    [id_cluster] INT NOT NULL,
    [cluster] NVARCHAR(120) NOT NULL,
    CONSTRAINT [PK_DimCluster] PRIMARY KEY ([id_cluster])
);
CREATE TABLE dbo.[DimTime] (
    [id_tiempo] INT NOT NULL,
    [fecha] NVARCHAR(120) NOT NULL,
    [anio] INT NOT NULL,
    [trimestre] INT NOT NULL,
    [mes_numero] INT NOT NULL,
    [mes_nombre] NVARCHAR(120) NOT NULL,
    [dia] INT NOT NULL,
    [origen] NVARCHAR(120) NOT NULL,
    CONSTRAINT [PK_DimTime] PRIMARY KEY ([id_tiempo])
);
CREATE TABLE dbo.[HECHOS] (
    [id_registro] INT NOT NULL,
    [id_geometria] INT NOT NULL,
    [id_orientacion] INT NOT NULL,
    [id_acristalamiento] INT NOT NULL,
    [id_clase] INT NOT NULL,
    [id_conjunto] INT NOT NULL,
    [id_cluster] INT NOT NULL,
    [id_tiempo] INT NOT NULL,
    [Y1] FLOAT NOT NULL,
    [Y2] FLOAT NOT NULL,
    [Y1_predicha] FLOAT NULL,
    [Y2_predicha] FLOAT NULL,
    [clase_predicha] NVARCHAR(120) NULL,
    [error_absoluto_Y1] FLOAT NULL,
    [error_absoluto_Y2] FLOAT NULL,
    [PC1] FLOAT NOT NULL,
    [PC2] FLOAT NOT NULL,
    CONSTRAINT [PK_HECHOS] PRIMARY KEY ([id_registro]),
    CONSTRAINT [FK_HECHOS_DimGeometria] FOREIGN KEY ([id_geometria]) REFERENCES dbo.[DimGeometria]([id_geometria]),
    CONSTRAINT [FK_HECHOS_DimOrientacion] FOREIGN KEY ([id_orientacion]) REFERENCES dbo.[DimOrientacion]([id_orientacion]),
    CONSTRAINT [FK_HECHOS_DimAcristalamiento] FOREIGN KEY ([id_acristalamiento]) REFERENCES dbo.[DimAcristalamiento]([id_acristalamiento]),
    CONSTRAINT [FK_HECHOS_DimClase] FOREIGN KEY ([id_clase]) REFERENCES dbo.[DimClase]([id_clase]),
    CONSTRAINT [FK_HECHOS_DimConjunto] FOREIGN KEY ([id_conjunto]) REFERENCES dbo.[DimConjunto]([id_conjunto]),
    CONSTRAINT [FK_HECHOS_DimCluster] FOREIGN KEY ([id_cluster]) REFERENCES dbo.[DimCluster]([id_cluster]),
    CONSTRAINT [FK_HECHOS_DimTime] FOREIGN KEY ([id_tiempo]) REFERENCES dbo.[DimTime]([id_tiempo]),
    CONSTRAINT CK_HECHOS_cargas CHECK (Y1 > 0 AND Y2 > 0),
    CONSTRAINT CK_HECHOS_prueba CHECK ((id_conjunto=1 AND Y1_predicha IS NULL AND Y2_predicha IS NULL AND clase_predicha IS NULL) OR (id_conjunto=2 AND Y1_predicha IS NOT NULL AND Y2_predicha IS NOT NULL AND clase_predicha IS NOT NULL))
);
CREATE TABLE dbo.[MetricasRegresion] (
    [modelo] NVARCHAR(120) NOT NULL,
    [objetivo] NVARCHAR(120) NOT NULL,
    [MAE] FLOAT NOT NULL,
    [RMSE] FLOAT NOT NULL,
    [R2] FLOAT NOT NULL
);
CREATE TABLE dbo.[MetricasClasificacion] (
    [modelo] NVARCHAR(120) NOT NULL,
    [accuracy] FLOAT NOT NULL,
    [precision_macro] FLOAT NOT NULL,
    [recall_macro] FLOAT NOT NULL,
    [F1_macro] FLOAT NOT NULL
);
CREATE TABLE dbo.[EvaluacionClusters] (
    [k] INT NOT NULL,
    [inercia] FLOAT NOT NULL,
    [silhouette] FLOAT NOT NULL
);
CREATE TABLE dbo.[VarianzaPCA] (
    [componente] NVARCHAR(120) NOT NULL,
    [varianza_explicada] FLOAT NOT NULL,
    [varianza_acumulada] FLOAT NOT NULL
);
CREATE TABLE dbo.[PerfilesClusters] (
    [id_cluster] INT NOT NULL,
    [registros] INT NOT NULL,
    [compacidad_media] FLOAT NOT NULL,
    [superficie_media] FLOAT NOT NULL,
    [pared_media] FLOAT NOT NULL,
    [techo_medio] FLOAT NOT NULL,
    [altura_media] FLOAT NOT NULL,
    [cristal_medio] FLOAT NOT NULL,
    [calefaccion_media] FLOAT NOT NULL,
    [refrigeracion_media] FLOAT NOT NULL
);
CREATE TABLE dbo.[ImportanciaVariables] (
    [tarea] NVARCHAR(120) NOT NULL,
    [variable] NVARCHAR(120) NOT NULL,
    [importancia_media] FLOAT NOT NULL,
    [desviacion] FLOAT NOT NULL
);
CREATE TABLE dbo.[MatrizConfusion] (
    [clase_real] NVARCHAR(120) NOT NULL,
    [clase_predicha] NVARCHAR(120) NOT NULL,
    [registros] INT NOT NULL
);
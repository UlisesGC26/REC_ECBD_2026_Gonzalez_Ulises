-- Ejecutar en una base de trabajo VACIA elegida en SQL Server.
-- Antecedente historico. Esquema vigente: ../datamart.sql (estrella).

    CREATE TABLE dim_geometria (id_geometria INT PRIMARY KEY,
        X1 FLOAT NOT NULL, X2 FLOAT NOT NULL, X3 FLOAT NOT NULL, X4 FLOAT NOT NULL, X5 FLOAT NOT NULL);
    CREATE TABLE dim_orientacion (id_orientacion INT PRIMARY KEY);
    CREATE TABLE dim_acristalamiento (id_acristalamiento INT PRIMARY KEY, X7 FLOAT NOT NULL, X8 INT NOT NULL);
    CREATE TABLE hecho_simulacion (id_registro INT PRIMARY KEY,
        id_geometria INT NOT NULL REFERENCES dim_geometria(id_geometria),
        id_orientacion INT NOT NULL REFERENCES dim_orientacion(id_orientacion),
        id_acristalamiento INT NOT NULL REFERENCES dim_acristalamiento(id_acristalamiento),
        Y1 FLOAT NOT NULL, Y2 FLOAT NOT NULL, clase_calefaccion VARCHAR(10) NOT NULL);
    
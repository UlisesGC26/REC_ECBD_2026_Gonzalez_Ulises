SELECT g.X1, g.X5, COUNT(*) AS registros,
        AVG(h.Y1) AS calefaccion_media, AVG(h.Y2) AS refrigeracion_media
        FROM hecho_simulacion h JOIN dim_geometria g ON g.id_geometria=h.id_geometria
        GROUP BY g.X1, g.X5 ORDER BY g.X1;
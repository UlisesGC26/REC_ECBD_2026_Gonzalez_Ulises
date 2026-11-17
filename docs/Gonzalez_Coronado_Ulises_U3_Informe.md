# Unidad III · Análisis supervisado

Ulises González Coronado · Actualización técnica: 16 de noviembre de 2026

## Diseño y prevención de fuga

Pregunta: ¿cómo cambian las cargas de calefacción y refrigeración entre edificios con distinta compacidad relativa y altura total? Se analizan 768 simulaciones de 12 geometrías. Y1 e Y2 son cargas, no años. Los resultados usan la escala original porque la ficha consultada no declara las unidades.

Las entradas son X1-X8. La regresión estima Y1/Y2; la clasificación usa alta si Y1 >= 25. El corte se fija antes de entrenar y no es una norma energética. GroupShuffleSplit reserva tres geometrías completas: 576 filas de entrenamiento y 192 de prueba, sin geometrías compartidas. El preprocesamiento se ajusta dentro de cada fold.

## Comparación y optimización justificada

GroupKFold de tres particiones compara Ridge con Random Forest y logística con Random Forest. Se prueban alpha, C, profundidad máxima y tamaño mínimo de hoja. En validación, el MAE conjunto del bosque con profundidad 8 y hoja 1 es 3.5896, frente a 3.5935 sin límite de profundidad. Se elige la opción ligeramente más simple. En logística, C=1 mejora F1 macro de validación de 0.8413 (C=0.1) a 0.8847; C=10 baja a 0.8500. La prueba no interviene en la elección.

| modelo           | objetivo   |     MAE |    RMSE |        R2 |
|:-----------------|:-----------|--------:|--------:|----------:|
| RandomForest     | Y1         | 3.33042 | 3.61722 |  0.806371 |
| RandomForest     | Y2         | 4.32878 | 4.7784  |  0.695788 |
| Referencia_media | Y1         | 8.26768 | 8.87769 | -0.166332 |
| Referencia_media | Y2         | 8.55478 | 9.09301 | -0.101609 |

El MAE es el error absoluto medio, RMSE penaliza errores grandes y R² compara con la dispersión de la prueba. El bosque mejora la referencia de predecir la media de entrenamiento en ambas cargas. Las métricas no prueban ahorro real.

## Clasificación y errores

| modelo             |   accuracy |   precision_macro |   recall_macro |   F1_macro |
|:-------------------|-----------:|------------------:|---------------:|-----------:|
| Logistica          |   0.791667 |          0.821429 |       0.833333 |   0.791304 |
| Referencia_mayoria |   0.375    |          0.1875   |       0.5      |   0.272727 |

![Figura](figuras/03_matriz_confusion.png)

La logística acierta 152 de 192 casos. Reconoce las 72 cargas bajas y 80 de las 120 altas. Los 40 falsos negativos de carga alta limitan su uso para descartar diseños. Se presentan precisión, recall y F1 por clase en reporte_clasificacion.json; el promedio macro da el mismo peso a cada clase.

## Regresión, variables y utilidad

![Figura](figuras/04_regresion_prueba.png)

La importancia por permutación posterior a la selección identifica X5 como la variable con mayor deterioro al permutarla en ambas tareas. X4 y X7 también aportan señal. Algunas importancias son negativas: la correlación geométrica y la muestra pequeña pueden producir estos resultados. No se interpretan como efectos causales. Los detalles están en importancia_variables.csv.

La regresión permite comparar estimaciones entre diseños; la clasificación resume un umbral didáctico. Solo se evalúa una separación de 12 geometrías simuladas, por lo que falta validación externa antes de tomar decisiones reales.

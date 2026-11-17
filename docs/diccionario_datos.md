# Diccionario de datos

Fuente: Energy Efficiency (Tsanas y Xifara, 2012), UCI. https://doi.org/10.24432/C51307.

El archivo original tiene 768 filas, ocho entradas y dos objetivos. Se conservan los nombres para poder compararlo con la fuente. La ficha UCI consultada no incluye unidades; los resultados se presentan en su escala original. Los rangos siguientes son valores observados, no límites universales de un edificio.

- **X1, compacidad relativa.** Entrada numérica; de 0.62 a 0.98. Describe la compacidad del diseño. Es una variable central de la pregunta.
- **X2, área de superficie.** Entrada numérica; de 514.5 a 808.5.
- **X3, área de muros.** Entrada numérica; de 245 a 416.5.
- **X4, área de techo.** Entrada numérica; de 110.25 a 220.5.
- **X5, altura total.** Entrada numérica; valores 3.5 y 7. Se usa para comparar grupos.
- **X6, orientación.** Categoría codificada con enteros 2, 3, 4 y 5. El modelo usa OneHotEncoder, por lo que no interpreta estos códigos como una escala de intensidad. Se conservan sin asignar direcciones cardinales no documentadas en la ficha.
- **X7, área de acristalamiento.** Entrada numérica; valores 0, 0.1, 0.25 y 0.4.
- **X8, distribución del acristalamiento.** Categoría con códigos enteros 0, 1, 2, 3, 4 y 5. También utiliza OneHotEncoder. No se supone una distancia numérica entre códigos.
- **Y1, carga de calefacción.** Objetivo numérico; de 6.01 a 43.1. No significa año 1.
- **Y2, carga de refrigeración.** Objetivo numérico; de 10.9 a 48.03. No significa año 2.

## Columnas añadidas al archivo procesado

- **id_registro.** Identificador de 1 a 768 según el orden original. No entra en los modelos.
- **grupo_geometria.** Identifica cada combinación de X1-X5; hay 12 grupos de 64 filas. Permite mantener las variantes del mismo diseño en un único conjunto. No entra como predictor.
- **clase_calefaccion.** `alta` si Y1 >= 25 y `baja` si Y1 < 25. Es el objetivo de clasificación y no una entrada. El corte se fija antes del entrenamiento y no se obtiene de la prueba. La regla es didáctica y está pendiente de revisión con el profesor.

Los archivos de predicciones añaden Y1_predicha, Y2_predicha, clase_real y clase_predicha. Son resultados derivados para evaluar los modelos.

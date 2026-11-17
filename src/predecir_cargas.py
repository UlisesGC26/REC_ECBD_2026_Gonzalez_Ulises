"""Compara una predicción con una observación reservada para prueba."""
import joblib
import pandas as pd
from src.preparacion_datos import ROOT, ENTRADAS

if __name__ == "__main__":
    casos = pd.read_csv(ROOT / "data/processed/predicciones_prueba.csv")
    ejemplo = casos.iloc[[0]]
    reg = joblib.load(ROOT / "modelos/modelo_regresion_cargas.joblib")
    cls = joblib.load(ROOT / "modelos/modelo_clasificacion_calefaccion.joblib")
    pred = reg.predict(ejemplo[ENTRADAS])[0]
    print("Ejemplo reservado para prueba. Registro:", int(ejemplo.id_registro.iloc[0]))
    print(ejemplo[ENTRADAS].to_string(index=False))
    print(f"Y1 real: {ejemplo.Y1.iloc[0]:.2f}. Predicha: {pred[0]:.2f}")
    print(f"Y2 real: {ejemplo.Y2.iloc[0]:.2f}. Predicha: {pred[1]:.2f}")
    print("Clase real:", ejemplo.clase_real.iloc[0], "Clase predicha:", cls.predict(ejemplo[ENTRADAS])[0])

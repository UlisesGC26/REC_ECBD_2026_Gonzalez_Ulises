"""Comparación y ajuste de modelos con separación por geometría de edificio."""
from pathlib import Path
import json
import platform

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             ConfusionMatrixDisplay, f1_score, mean_absolute_error,
                             mean_squared_error, r2_score, precision_score, recall_score)
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV, GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.preparacion_datos import ROOT, ENTRADAS, OBJETIVOS, UMBRAL_CALOR, guardar_json


def preprocesador():
    return ColumnTransformer([
        ("numericas", StandardScaler(), ["X1", "X2", "X3", "X4", "X5", "X7"]),
        ("categoricas", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["X6", "X8"])
    ])


def ajustar_modelos():
    archivo = ROOT / "data/processed/eficiencia_energetica_procesada.csv"
    if not archivo.exists():
        raise FileNotFoundError("Primero ejecuta: python -m src.ejecutar_proyecto")
    df = pd.read_csv(archivo)
    X, y = df[ENTRADAS], df[OBJETIVOS]
    grupos = df.grupo_geometria
    # Corte temporal 70/30: la última porción simula predicciones futuras.
    df = df.sort_values('fecha_simulada').reset_index(drop=True)
    X, y, grupos = df[ENTRADAS], df[OBJETIVOS], df.grupo_geometria
    corte = int(len(df) * .70)
    entrenamiento, prueba = np.arange(corte), np.arange(corte, len(df))
    X_train, X_test = X.iloc[entrenamiento], X.iloc[prueba]
    y_train, y_test = y.iloc[entrenamiento], y.iloc[prueba]
    grupos_train = grupos.iloc[entrenamiento]
    folds = list(GroupKFold(n_splits=3).split(X_train, y_train, grupos_train))
    clases = df.clase_calefaccion
    c_train, c_test = clases.iloc[entrenamiento], clases.iloc[prueba]
    for tr, va in folds:
        assert c_train.iloc[tr].nunique() == 2 and c_train.iloc[va].nunique() == 2
    division = df[["id_registro", "grupo_geometria", "fecha_simulada"]].copy()
    division["conjunto"] = "entrenamiento"
    division.loc[prueba, "conjunto"] = "prueba"
    division.to_csv(ROOT / "data/processed/division_modelos.csv", index=False)

    candidatos_reg = {
        "Ridge": (Ridge(), {"modelo__alpha": [.1, 1., 10.]}),
        "RandomForest": (RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=1),
                         {"modelo__max_depth": [8, None], "modelo__min_samples_leaf": [1, 3]})}
    candidatos_cls = {
        "Logistica": (LogisticRegression(max_iter=2000, random_state=42), {"modelo__C": [.1, 1., 10.]}),
        "RandomForest": (RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=1),
                         {"modelo__max_depth": [6, None], "modelo__min_samples_leaf": [1, 3]})}

    def seleccionar(candidatos, objetivo, metrica, tarea):
        resultados, ajustes = [], {}
        for nombre, (modelo, parametros) in candidatos.items():
            pipe = Pipeline([("preparacion", preprocesador()), ("modelo", modelo)])
            busqueda = GridSearchCV(pipe, parametros, cv=folds, scoring=metrica, n_jobs=1)
            busqueda.fit(X_train, objetivo)
            ajustes[nombre] = busqueda
            for i, params in enumerate(busqueda.cv_results_["params"]):
                score = float(busqueda.cv_results_["mean_test_score"][i])
                resultados.append({"modelo": nombre, "parametros": json.dumps(params),
                                   "metrica_cv": -score if tarea == "regresion" else score,
                                   "desviacion_cv": float(busqueda.cv_results_["std_test_score"][i])})
        mejor_nombre = max(ajustes, key=lambda k: ajustes[k].best_score_)
        pd.DataFrame(resultados).to_csv(ROOT / f"docs/validacion_{tarea}.csv", index=False)
        elegido = ajustes[mejor_nombre]
        return mejor_nombre, elegido.best_estimator_, elegido.best_params_, float(elegido.best_score_)

    nombre_reg, reg, parametros_reg, cv_reg = seleccionar(candidatos_reg, y_train, "neg_mean_absolute_error", "regresion")
    nombre_cls, cls, parametros_cls, cv_cls = seleccionar(candidatos_cls, c_train, "f1_macro", "clasificacion")
    pred_reg, pred_cls = reg.predict(X_test), cls.predict(X_test)
    referencia_reg = DummyRegressor(strategy="mean").fit(X_train, y_train).predict(X_test)
    referencia_cls = DummyClassifier(strategy="most_frequent").fit(X_train, c_train).predict(X_test)
    filas = []
    for nombre, pred in [(nombre_reg, pred_reg), ("Referencia_media", referencia_reg)]:
        for i, target in enumerate(OBJETIVOS):
            filas.append({"modelo": nombre, "objetivo": target,
                          "MAE": mean_absolute_error(y_test[target], pred[:, i]),
                          "RMSE": float(np.sqrt(mean_squared_error(y_test[target], pred[:, i]))),
                          "R2": r2_score(y_test[target], pred[:, i])})
    metricas_reg = pd.DataFrame(filas)
    metricas_reg.to_csv(ROOT / "docs/metricas_regresion.csv", index=False)
    metricas_cls = pd.DataFrame([
        {"modelo": nombre, "accuracy": accuracy_score(c_test, pred),
         "precision_macro": precision_score(c_test, pred, average="macro", zero_division=0),
         "recall_macro": recall_score(c_test, pred, average="macro", zero_division=0),
         "F1_macro": f1_score(c_test, pred, average="macro", zero_division=0)}
        for nombre, pred in [(nombre_cls, pred_cls), ("Referencia_mayoria", referencia_cls)]])
    metricas_cls.to_csv(ROOT / "docs/metricas_clasificacion.csv", index=False)
    detalle = classification_report(c_test, pred_cls, labels=["baja", "alta"], output_dict=True, zero_division=0)
    guardar_json(ROOT / "docs/reporte_clasificacion.json", detalle)
    # Interpretación posterior a la selección; no se usa para volver a ajustar.
    importancia = []
    for tarea, estimador, objetivo, scoring in [
        ('regresion', reg, y_test, 'neg_mean_absolute_error'),
        ('clasificacion', cls, c_test, 'f1_macro')]:
        imp = permutation_importance(estimador, X_test, objetivo, scoring=scoring,
                                     n_repeats=10, random_state=42, n_jobs=1)
        for variable, media, sd in zip(ENTRADAS, imp.importances_mean, imp.importances_std):
            importancia.append({'tarea': tarea, 'variable': variable,
                                'importancia_media': media, 'desviacion': sd})
    pd.DataFrame(importancia).to_csv(ROOT / 'docs/importancia_variables.csv', index=False)
    predicciones = df.iloc[prueba][["id_registro"] + ENTRADAS + OBJETIVOS].copy()
    predicciones["Y1_predicha"], predicciones["Y2_predicha"] = pred_reg[:, 0], pred_reg[:, 1]
    predicciones["clase_real"], predicciones["clase_predicha"] = c_test.to_numpy(), pred_cls
    predicciones.to_csv(ROOT / "data/processed/predicciones_prueba.csv", index=False)
    joblib.dump(reg, ROOT / "modelos/modelo_regresion_cargas.joblib")
    joblib.dump(cls, ROOT / "modelos/modelo_clasificacion_calefaccion.joblib")
    cm = confusion_matrix(c_test, pred_cls, labels=["baja", "alta"])
    fig, ax = plt.subplots(figsize=(5, 4.3))
    ConfusionMatrixDisplay(cm, display_labels=["Baja", "Alta"]).plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set(xlabel="Clase predicha", ylabel="Clase real", title="Clasificación de calefacción: prueba")
    fig.tight_layout()
    fig.savefig(ROOT / "docs/figuras/03_matriz_confusion.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.3))
    for i, ax in enumerate(axes):
        real = y_test.iloc[:, i]
        ax.scatter(real, pred_reg[:, i], alpha=.6, s=18, color="#137f86")
        limites = [min(real.min(), pred_reg[:, i].min()), max(real.max(), pred_reg[:, i].max())]
        ax.plot(limites, limites, "--", color="#d87932")
        ax.set(xlabel="Carga real (escala original)", ylabel="Carga predicha", title=OBJETIVOS[i])
    fig.suptitle("Regresión sobre geometrías reservadas para prueba", fontsize=13)
    fig.tight_layout()
    fig.savefig(ROOT / "docs/figuras/04_regresion_prueba.png", dpi=180)
    plt.close(fig)
    resultado = {
        "semilla": 42, "entrenamiento_filas": len(entrenamiento), "prueba_filas": len(prueba),
        "estrategia_particion": "Corte cronológico 70/30 con fecha simulada; prueba representa horizonte futuro simulado",
        "geometrias_entrenamiento": sorted(int(v) for v in grupos_train.unique()),
        "geometrias_prueba": sorted(int(v) for v in grupos.iloc[prueba].unique()),
        "geometrias_compartidas": int(len(set(grupos_train).intersection(grupos.iloc[prueba]))), "validacion": "GroupKFold de 3 particiones solo en entrenamiento",
        "regresion": {"modelo": nombre_reg, "parametros": parametros_reg, "MAE_cv": -cv_reg},
        "clasificacion": {"modelo": nombre_cls, "parametros": parametros_cls, "F1_macro_cv": cv_cls,
                          "umbral_Y1": UMBRAL_CALOR, "matriz_confusion_baja_alta": cm.tolist()},
        "versiones": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                      "pandas": pd.__version__, "numpy": np.__version__, "joblib": joblib.__version__},
        "limite": "La fecha es sintética y solo permite demostrar un flujo temporal. No prueba desempeño futuro ni causalidad en edificios reales."
    }
    guardar_json(ROOT / "docs/resultados_modelos.json", resultado)
    print(f"Separación temporal 70/30: {len(entrenamiento)} entrenamiento / {len(prueba)} prueba.")
    print("Regresión seleccionada mediante validación:", nombre_reg, parametros_reg)
    print(metricas_reg.round(4).to_string(index=False))
    print("Clasificación seleccionada mediante validación:", nombre_cls, parametros_cls)
    print(metricas_cls.round(4).to_string(index=False))
    print("Matriz de confusión [baja, alta]:", cm.tolist())
    return resultado


if __name__ == "__main__":
    ajustar_modelos()

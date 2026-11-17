"""K-Means y PCA exploratorios sobre seis atributos físicos, sin usar Y1/Y2."""
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler
from src.preparacion_datos import ROOT, guardar_json

VARIABLES = ['X1', 'X2', 'X3', 'X4', 'X5', 'X7']


def analizar():
    df = pd.read_csv(ROOT / 'data/processed/eficiencia_energetica_procesada.csv')
    scaler = StandardScaler()
    z = scaler.fit_transform(df[VARIABLES])
    candidatos, modelos = [], {}
    for k in range(2, 9):
        modelo = KMeans(n_clusters=k, random_state=42, n_init=30).fit(z)
        modelos[k] = modelo
        candidatos.append({'k': k, 'inercia': modelo.inertia_,
                           'silhouette': silhouette_score(z, modelo.labels_)})
    evaluacion = pd.DataFrame(candidatos)
    k = int(evaluacion.sort_values(['silhouette', 'k'], ascending=[False, True]).iloc[0]['k'])
    modelo = modelos[k]
    # Etiquetas estables, ordenadas por altura y compacidad de sus centros.
    centros = scaler.inverse_transform(modelo.cluster_centers_)
    orden = sorted(range(k), key=lambda i: (centros[i, 4], centros[i, 0], centros[i, 5]))
    mapa = {anterior: nuevo + 1 for nuevo, anterior in enumerate(orden)}
    etiquetas = np.array([mapa[int(x)] for x in modelo.labels_])
    pca = PCA().fit(z)
    componentes = pca.transform(z)
    salida = df.copy()
    salida['id_cluster'] = etiquetas
    salida['PC1'], salida['PC2'] = componentes[:, 0], componentes[:, 1]
    salida.to_csv(ROOT / 'data/processed/resultados_no_supervisados.csv', index=False)
    perfiles = salida.groupby('id_cluster').agg(
        registros=('id_registro', 'size'), compacidad_media=('X1', 'mean'),
        superficie_media=('X2', 'mean'), pared_media=('X3', 'mean'),
        techo_medio=('X4', 'mean'), altura_media=('X5', 'mean'),
        cristal_medio=('X7', 'mean'), calefaccion_media=('Y1', 'mean'),
        refrigeracion_media=('Y2', 'mean')).reset_index()
    perfiles.to_csv(ROOT / 'data/processed/perfiles_clusters.csv', index=False)
    evaluacion.to_csv(ROOT / 'docs/evaluacion_clusters.csv', index=False)
    varianza = pd.DataFrame({'componente': [f'PC{i+1}' for i in range(len(VARIABLES))],
                            'varianza_explicada': pca.explained_variance_ratio_,
                            'varianza_acumulada': np.cumsum(pca.explained_variance_ratio_)})
    varianza.to_csv(ROOT / 'docs/varianza_pca.csv', index=False)
    pd.DataFrame(pca.components_.T, index=VARIABLES, columns=varianza.componente).to_csv(
        ROOT / 'docs/cargas_pca.csv', index_label='variable')
    estabilidad = [adjusted_rand_score(modelo.labels_, KMeans(n_clusters=k, n_init=30,
                    random_state=s).fit_predict(z)) for s in [7, 21, 84]]
    resultado = {'variables': VARIABLES, 'excluidas': {'X6': 'Código nominal de orientación',
        'X8': 'Código nominal de distribución', 'Y1_Y2': 'Respuestas; solo se usan para describir grupos después'},
        'k_elegido': k, 'criterio': 'Mayor silhouette entre k=2..8; menor k ante empate',
        'silhouette': float(evaluacion.loc[evaluacion.k == k, 'silhouette'].iloc[0]),
        'varianza_PC1_PC2': float(pca.explained_variance_ratio_[:2].sum()),
        'componentes_95_por_ciento': int(np.searchsorted(np.cumsum(pca.explained_variance_ratio_), .95) + 1),
        'ARI_otras_semillas': estabilidad, 'n_registros': len(df),
        'alcance': 'Exploración de las 768 simulaciones, sin evaluación predictiva. La geometría domina y sus variables están correlacionadas.'}
    guardar_json(ROOT / 'docs/resultados_no_supervisados.json', resultado)
    joblib.dump({'scaler': scaler, 'kmeans': modelo, 'pca': pca, 'variables': VARIABLES,
                 'mapa_clusters': mapa}, ROOT / 'modelos/modelo_kmeans_pca.joblib')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(evaluacion.k, evaluacion.inercia, 'o-', color='#147d92')
    axes[0].set(title='Método del codo', xlabel='Número de clusters', ylabel='Inercia')
    axes[1].plot(evaluacion.k, evaluacion.silhouette, 'o-', color='#ca673b')
    axes[1].axvline(k, color='#147d92', linestyle='--')
    axes[1].set(title=f'Selección: k={k}', xlabel='Número de clusters', ylabel='Silhouette')
    fig.tight_layout(); fig.savefig(ROOT / 'docs/figuras/05_seleccion_clusters.png', dpi=170); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    for c in sorted(set(etiquetas)):
        mask = etiquetas == c
        ax.scatter(componentes[mask, 0], componentes[mask, 1], s=22, alpha=.65, label=f'Cluster {c}')
    ax.set(title='PCA de características físicas; color = K-Means',
           xlabel=f'PC1 ({pca.explained_variance_ratio_[0]:.1%})', ylabel=f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    ax.legend(); fig.tight_layout(); fig.savefig(ROOT / 'docs/figuras/06_pca_clusters.png', dpi=170); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(varianza.componente, varianza.varianza_explicada, color='#147d92')
    ax.plot(varianza.componente, varianza.varianza_acumulada, 'o-', color='#ca673b')
    ax.axhline(.95, linestyle='--', color='#555555'); ax.set(ylabel='Proporción de varianza', title='PCA: varianza individual y acumulada')
    fig.tight_layout(); fig.savefig(ROOT / 'docs/figuras/07_varianza_pca.png', dpi=170); plt.close(fig)
    print(resultado)
    return resultado


if __name__ == '__main__':
    analizar()

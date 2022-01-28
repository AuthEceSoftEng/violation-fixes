import numpy as np

def compute_purity_from_cData(clustering_model, clustering_data):
    n_observations = len(np.where(clustering_model.labels_>=0)[0])
    purity_sum = 0
    for cluster in clustering_data:
        purity_sum  += cluster['rules-freq'][0][1]

    purity = purity_sum / n_observations

    return purity

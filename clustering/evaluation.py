import numpy as np

def compute_purity_from_cData(clustering_model, clustering_data):
    '''
    Computes and returns the purity of the whole clustering process.
    
    param clustering_model: the clustering model corresponds to the clustering process.
    param clustering_data: the data of the clusters' as extracted with clusters_sub_dfs_and_data(...) function.
    '''
    n_observations = len(np.where(clustering_model.labels_>=0)[0])
    purity_sum = 0
    for cluster in clustering_data:
        purity_sum  += cluster['rules-freq'][0][1]

    purity = purity_sum / n_observations

    return purity

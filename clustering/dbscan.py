##### # # # # # # # # # # # # # # # #
from sklearn.cluster import DBSCAN
from clustering.preprocessing import distance_matrix_from_0_to_1_sim_matrix
import numpy as np
from clustering.evaluation import compute_purity_from_cData
from clustering.tools import clusters_sub_dfs_and_data
import matplotlib.pyplot as plt

def DBSCAN_execution(input_X, eps=0.1, min_samples=15, metric='precomputed', metric_params=None,\
     algorithm='auto', leaf_size=30, p=None, n_jobs=None):

    # import plotly.express as px
    clustering_model_dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, metric_params=metric_params,\
        algorithm = algorithm, leaf_size=leaf_size, p = p, n_jobs = n_jobs  ).fit(input_X)

    return clustering_model_dbscan

# External Evaluation
def kmedoids_purity_plot(input_X, input_df, min_eps = 0.1,max_eps=0.2,step = 0.01,min_samples=15,\
   metric='precomputed', metric_params=None, algorithm='auto', leaf_size=30, p=None, n_jobs=None):
    '''
    Executes kmedoids for k from min_clusters to max_clusters with a certain step (step), and
    plots the purity plot.
    '''
    purity_values = []

    eps_vals = np.arange(min_eps, max_eps, step)
    
    for i in eps_vals:
        clustering_model = DBSCAN_execution(input_X, eps=i, min_samples=min_samples, metric='precomputed')
        clustering_data = clusters_sub_dfs_and_data(input_df, clustering_model)
        purity = compute_purity_from_cData(clustering_model, clustering_data)   

        purity_values.append(purity)
        print(i)
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
    plt.plot(eps_vals, purity_values, color='red')
    plt.xlabel('EPS', fontsize=15)
    plt.ylabel('Purity', fontsize=15)
    plt.title('Purity / EPS (DBSCAN)', fontsize=15)
    plt.grid()
    plt.show()

    return purity_values
# # Print DBSCAN clusters' rules
# for i_cluster in range(-1, max(clustering_model_dbscan.labels_) + 1 ):
#     print("CLUSTER: " + str(i_cluster) + " RULES:")
#     for point in np.where(clustering_model_dbscan.labels_ == i_cluster)[0]:
#         print(sample_df.iloc[point]["Rule"])
#     print("-----------------------------------------------")
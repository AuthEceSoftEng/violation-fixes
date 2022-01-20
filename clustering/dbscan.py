##### # # # # # # # # # # # # # # # #
from sklearn.cluster import DBSCAN
from clustering.preprocessing import distance_matrix_from_0_to_1_sim_matrix
import numpy as np

def DBSCAN_execution(input_X, eps=0.1, min_samples=15, metric='precomputed', metric_params=None,\
     algorithm='auto', leaf_size=30, p=None, n_jobs=None):

    # import plotly.express as px
    clustering_model_dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, metric_params=metric_params,\
        algorithm = algorithm, leaf_size=leaf_size, p = p, n_jobs = n_jobs  ).fit(input_X)

    return clustering_model_dbscan

# # Print DBSCAN clusters' rules
# for i_cluster in range(-1, max(clustering_model_dbscan.labels_) + 1 ):
#     print("CLUSTER: " + str(i_cluster) + " RULES:")
#     for point in np.where(clustering_model_dbscan.labels_ == i_cluster)[0]:
#         print(sample_df.iloc[point]["Rule"])
#     print("-----------------------------------------------")
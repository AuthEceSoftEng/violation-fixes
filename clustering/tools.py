import pandas as pd
import numpy as np
from pmdTools import get_column_val_frequencies

def clusters_sub_dfs_and_data(initial_df, clustering_model):
    '''
    Receives as input the initial dataframe and the clustering model, and returns
    a list (lets assume it as subdf_list) of dictionaries where:

    subdf_list[i]['df']: corresponds to the rows of initial_df that clustered to cluster i.
    subdf_list[i]['rules-freq']: The rules' frequencies of the rows of the subdf_list[i]['df'] .
    '''

    # A list of dictionaries where the sub-dataframes corresponding to each cluster will be stored
    # clusters_dataframes[i]["df"], corresponds to the rows of initial_df, that clustered on i.
    clusters_dataframes = []

    # This if statements, is added for clustering models, where n_clusters attribute is absent.
    # (e.g. for sklearn's DBSCAN model)
    if hasattr(clustering_model, "n_clusters"):
        n_clusters = clustering_model.n_clusters
    else: 
        n_clusters =  max(clustering_model.labels_) + 1


    # Loop through clusters
    for cluster in range(0, n_clusters, 1):
        
        #The dataframe where the rows of current cluster will be stored.
        curr_cluster_df = pd.DataFrame(columns=initial_df.columns)

        for row in np.where(clustering_model.labels_== cluster)[0]:          
            curr_cluster_df = curr_cluster_df.append( initial_df.iloc[row])
            # curr_cluster_df = curr_cluster_df.append( initial_df.iloc[row], ignore_index = True)

        rules_freq_sub_df = get_column_val_frequencies(curr_cluster_df, "Rule")

        curr_cluster_info = 	{
		    'df' : curr_cluster_df,
            'rules-freq': rules_freq_sub_df,
	    }

        clusters_dataframes.append(curr_cluster_info)
    
    return clusters_dataframes

def print_cluster_rule_frequencies(cluster_info, clustering_model):
       # This if statements, is added for clustering models, where n_clusters attribute is absent.
    # (e.g. for sklearn's DBSCAN model)
    if hasattr(clustering_model, "n_clusters"):
        n_clusters = clustering_model.n_clusters
    else: 
        n_clusters =  max(clustering_model.labels_) + 1

    for cluster in range(n_clusters):
        print("CLUSTER: " + str(cluster) +", frequencies:" )
        for freq in cluster_info[cluster]['rules-freq']:
            print(freq)
        print("--------------------------------------")


# # Check cluster's, input update script and rules.
# # cluster = 2
# # print("SIZE:")
# # print(len(np.where(clustering_model.labels_== cluster)[0]))
# # for i in np.where(clustering_model.labels_== cluster)[0]:
# #     print(sample_df_up_vectors[i])
# # for i in np.where(clustering_model.labels_== cluster)[0]:
# #     print(sample_df.iloc[i]["Rule"])
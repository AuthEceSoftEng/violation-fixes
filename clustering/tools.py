import pandas as pd
import numpy as np
from pmdTools import get_column_val_frequencies
import collections

def repos_from_commit_urls(commit_urls_list):
    repos_list =[]
    
    for url in commit_urls_list:
        commit_part = url.split("https://github.com/")[1]
    
        repo_name = commit_part.split("/commit/")[0]
    
        repos_list.append(repo_name)
    
    repos_list = list(set(repos_list))

    return repos_list

def cluster_calc_purity(rules_freq, cluster_df):
    '''Function for calculating the purity metric of a cluster.'''
    purity = rules_freq[0][1]/ len(cluster_df)

    return purity
    

def clusters_sub_dfs_and_data(initial_df, clustering_model):
    '''
    Receives as input the initial dataframe and the clustering model, and returns
    a list (lets assume it as subdf_list) of dictionaries where:

    subdf_list[i]['df']: corresponds to the rows of initial_df that clustered to cluster i.
    subdf_list[i]['rules-freq']: The rules' frequencies of the rows of the subdf_list[i]['df'] .
    subdf_list[i]['purity']: The purity of the cluster i.
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
        

        curr_cluster_purity = cluster_calc_purity(rules_freq_sub_df,curr_cluster_df)
        
        repos_in_cluster = repos_from_commit_urls(list(set(list(curr_cluster_df["Commit url"]))))
        curr_cluster_info = {
		    'df' : curr_cluster_df,
            'rules-freq': rules_freq_sub_df,
            'purity' : curr_cluster_purity,
            'commits' : list(set(list(curr_cluster_df["Commit url"]))),
            'repos'  :  repos_in_cluster
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

def print_cluster_rule_frequencies_and_stats(cluster_info, clustering_model):
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
        print("Purity of cluster "+ str(cluster) + " :  " + str(cluster_info[cluster]['purity']) )
        print("--------------------------------------")
        print("Commits in cluster "+ str(cluster) + " :  " + str(len(cluster_info[cluster]['commits'])))
        print("--------------------------------------")
        print("REPOS in cluster "+ str(cluster) + " :  " + str(len(cluster_info[cluster]['repos'])))
        print("--------------------------------------")
        print("--------------------------------------")


# # Check cluster's, input update script and rules.
# # cluster = 2
# # print("SIZE:")
# # print(len(np.where(clustering_model.labels_== cluster)[0]))
# # for i in np.where(clustering_model.labels_== cluster)[0]:
# #     print(sample_df_up_vectors[i])
# # for i in np.where(clustering_model.labels_== cluster)[0]:
# #     print(sample_df.iloc[i]["Rule"])
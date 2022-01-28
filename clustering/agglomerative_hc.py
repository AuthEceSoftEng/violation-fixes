from sklearn.cluster import AgglomerativeClustering
from clustering.preprocessing import  distance_matrix_from_0_to_1_sim_matrix, lcs_similarities
import matplotlib.pyplot as plt
from clustering.evaluation import compute_purity_from_cData
from clustering.tools import clusters_sub_dfs_and_data

def agglomerative_hc_custom_dmatrix(distance_matrix, nclusters = 40, linkage = 'average', computeFullTree  = False, distanceThresshold = None):
    '''
    Applies aglomerative hierarchical clustering, on an input distance matrix.
    '''
    clustering_model = AgglomerativeClustering(n_clusters=nclusters, affinity="precomputed",\
        linkage= linkage, compute_full_tree=computeFullTree, distance_threshold= distanceThresshold)

    clustering_model.fit(distance_matrix)

    return clustering_model

def lcs_similarity_hca_clustering(vectors_of_action_tokens, nclusters = 40, linkage = 'average', computeFullTree  = False, distanceThresshold = None):

    LCS_similarities = lcs_similarities(vectors_of_action_tokens)

    # Get Distance Matrix from similarity matrix
    distance_matrix = distance_matrix_from_0_to_1_sim_matrix(LCS_similarities)

    # apply HC clustering to our distance matrix
    clustering_model = agglomerative_hc_custom_dmatrix(distance_matrix, nclusters = nclusters, linkage = linkage,\
         computeFullTree  = computeFullTree, distanceThresshold = distanceThresshold)

    return clustering_model

# External Evaluation
def kmedoids_purity_plot(input_X, input_df, min_clusters = 2, max_clusters = 8, step = 1,\
    affinity="precomputed", linkage = 'average', computeFullTree  = True, distanceThresshold = None):
    '''
    Executes kmedoids for k from min_clusters to max_clusters with a certain step (step), and
    plots the purity plot.
    '''
    purity_values = []

    numbers_of_clusters = range(min_clusters, max_clusters+1, step)
    
    for i in numbers_of_clusters:
        clustering_model = AgglomerativeClustering(n_clusters=i, affinity=affinity,\
        linkage= linkage, compute_full_tree=computeFullTree, distance_threshold= distanceThresshold)

        clustering_model.fit(input_X)

        clustering_data = clusters_sub_dfs_and_data(input_df, clustering_model)
        purity = compute_purity_from_cData(clustering_model, clustering_data)   

        purity_values.append(purity)
        print(i)
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
    plt.plot(numbers_of_clusters, purity_values, color='red')
    plt.xlabel('Number of Clusters', fontsize=15)
    plt.ylabel('Purity', fontsize=15)
    plt.title('Purity / Number of Clusters (AHC)', fontsize=15)
    plt.grid()
    plt.show()

    return purity_values
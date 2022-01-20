from sklearn.cluster import AgglomerativeClustering
from clustering.preprocessing import  distance_matrix_from_0_to_1_sim_matrix, lcs_similarities

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
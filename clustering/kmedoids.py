from sklearn_extra.cluster import KMedoids
from clustering.preprocessing import lcs_similarities, distance_matrix_from_0_to_1_sim_matrix
import matplotlib.pyplot as plt
from clustering.evaluation import compute_purity_from_cData
from clustering.tools import clusters_sub_dfs_and_data


def distance_matrix_kmedoids_clustering(distance_matrix, nclusters = 40, metric="precomputed", init='k-medoids++',\
     method="alternate", max_iter = 300, random_state = 1):
    '''
    Application of kmedoids clustering, based on input distance_matrix.
    '''
    # apply k-medoids clustering to our distance matrix
    clustering_model = KMedoids(n_clusters = nclusters, metric = metric, init = init, method = method,\
         max_iter = max_iter,random_state = random_state ).fit(distance_matrix)

    return clustering_model

def lcs_similarity_kmedoids_clustering(vectors_of_action_tokens, nclusters = 40, metric="precomputed", init='k-medoids++',\
     method="alternate", max_iter = 300, random_state = 1):

    LCS_similarities = lcs_similarities(vectors_of_action_tokens)

    # apply k-medoids clustering based on similarity matrix
    clustering_model = distance_matrix_kmedoids_clustering(LCS_similarities, n_clusters = nclusters, metric = metric,\
         init = init, method = method, max_iter = max_iter, random_state= random_state)

    return clustering_model

# Internal Evaluation 
def kmedoids_inertia_values_calculate(input_X, min_clusters = 1, max_clusters = 8, step = 1, plot =True,\
    metric="precomputed", method='alternate', init='k-medoids++', max_iter=300, random_state = 1):
    '''
    Executes kmedoids for k from min_clusters to max_clusters with a certain step (step), and
    plots the SAE (sum of absolute errors / insertia) plot.
    '''
    inertia_values = []

    numbers_of_clusters = range(min_clusters, max_clusters+1, step)
    
    for i in numbers_of_clusters:
        km = KMedoids(n_clusters=i,metric=metric, method=method, init=init, max_iter=max_iter, random_state=random_state )
        km.fit(input_X)
        inertia_values.append(km.inertia_ )
    if plot:        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
        plt.plot(numbers_of_clusters, inertia_values, color='red')
        plt.xlabel('Number of Clusters', fontsize=15)
        plt.ylabel('SAE', fontsize=15)
        plt.title('SAE / Number of Clusters (Kmedoids)', fontsize=15)
        plt.grid()
        plt.show()

    return list(numbers_of_clusters), inertia_values
 

# External Evaluation
def kmedoids_purity_plot(input_X, input_df, min_clusters = 1, max_clusters = 8, step = 1,\
    metric="precomputed", method='alternate', init='k-medoids++', max_iter=300, random_state = 1):
    '''
    Executes kmedoids for k from min_clusters to max_clusters with a certain step (step), and
    plots the purity plot.
    '''
    purity_values = []

    numbers_of_clusters = range(min_clusters, max_clusters+1, step)
    
    for i in numbers_of_clusters:
        km = KMedoids(n_clusters=i,metric=metric, method=method, init=init, max_iter=max_iter, random_state=random_state )
        km.fit(input_X)
        clustering_data = clusters_sub_dfs_and_data(input_df, km)
        purity = compute_purity_from_cData(km, clustering_data)   

        purity_values.append(purity)
        print(i)
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=240)
    plt.plot(numbers_of_clusters, purity_values, color='red')
    plt.xlabel('Number of Clusters', fontsize=15)
    plt.ylabel('Purity', fontsize=15)
    plt.title('Purity / Number of Clusters (Kmedoids)', fontsize=15)
    plt.grid()
    plt.show()

    return purity_values
from clustering.preprocessing import tfidfVectorizer_for_tokenized_data, countVectorizer_tokenized_data
import numpy as np

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def kmeans_SSE_plot(input_X, min_clusters = 1, max_clusters = 8, step = 1,\
     max_iter = 300, tol = 1e-04, init = 'k-means++', n_init = 10, algorithm = 'auto', random_state =1):
    '''
    Executes kmeans for k from min_clusters to max_clusters with a certain step (step), and
    plots the SSE (sum of squared errors / insertia) plot.
    '''
    inertia_values = []

    numbers_of_clusters = range(min_clusters, max_clusters+1,step)
    
    for i in numbers_of_clusters:
        km = KMeans(n_clusters=i,  max_iter=max_iter,\
            tol=tol, init=init, n_init=n_init, random_state = random_state, algorithm=algorithm)
        km.fit(input_X)
        inertia_values.append(km.inertia_)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.plot(numbers_of_clusters, inertia_values, color='red')
    plt.xlabel('Number of Clusters', fontsize=15)
    plt.ylabel('SSE', fontsize=15)
    plt.title('SSE /  Number of Clusters (Kmeans)', fontsize=15)
    plt.grid()
    plt.show()

    return inertia_values

def tfidf_kmeans(vectors_of_action_tokens, tf_idf_min_df = 15, n_clusters=40, init='k-means++' ,\
    n_init = 10, max_iter = 300, tol = 0.0001, verbose = 0, random_state = 1, copy_x = True, algorithm = 'auto'):

    ## TF - IDF application to the tokenized update scripts
    # with min_df = 15, only tokens that appear in more than 15 documents
    tfidf_gumtree_diffs_model = tfidfVectorizer_for_tokenized_data(min_df = tf_idf_min_df)

    tf_idf_gt_diffs_matrix = tfidf_gumtree_diffs_model.fit_transform(vectors_of_action_tokens)

    # Apply k-means with selected K from the SSE plot above.
    clustering_model = KMeans(n_clusters, init = init, n_init = n_init, max_iter = max_iter, tol = tol,\
        verbose = verbose, random_state = random_state, copy_x = copy_x, algorithm = algorithm)
    clustering_model.fit(tf_idf_gt_diffs_matrix)

    return clustering_model

def tfidf_kmeans_w_sse(vectors_of_action_tokens, tf_idf_min_df = 15, n_clusters=40, sse_min_clusters = 2, sse_max_clusters = 500,\
    sse_step = 1, init='k-means++' , n_init = 10, max_iter = 300, tol = 0.0001, verbose = 0,\
        random_state = 1, copy_x = True, algorithm = 'auto' ):

    ## TF - IDF application to the tokenized update scripts
    # with min_df = 15, only tokens that appear in more than 15 documents
    tfidf_gumtree_diffs_model = tfidfVectorizer_for_tokenized_data(min_df = tf_idf_min_df)

    tf_idf_gt_diffs_matrix = tfidf_gumtree_diffs_model.fit_transform(vectors_of_action_tokens)

    # # ploting k-means' SSE for different k values.
    kmeans_SSE_plot(tf_idf_gt_diffs_matrix, min_clusters = sse_min_clusters, max_clusters = sse_max_clusters, step = sse_step)

    # Apply k-means with selected K from the SSE plot above.
    clustering_model = KMeans(n_clusters, init = init, n_init = n_init, max_iter = max_iter, tol = tol,\
        verbose = verbose, random_state = random_state, copy_x = copy_x, algorithm = algorithm)
    clustering_model.fit(tf_idf_gt_diffs_matrix)

    return clustering_model
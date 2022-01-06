from pmdTools import get_column_val_frequencies
from gumtreeTools import get_actions_from_gumtree_txt_diff, txt_gummtree_actions_tokenizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import re
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity

########################### Functions for Data Preprocessing & Preparation (START) ###########################
def delete_rows_based_on_col_frequency(df, column_name, minimun_frequency):
    '''
    Checks which values of column column_name, appears less times than a minimun
    frequency (minimun_frequency) on df, and it deletes all the rows have these values. 
    '''
    values_frequencies = get_column_val_frequencies(df, column_name)

    values = [x[0] for x in values_frequencies]

    frequencies = [x[1] for x in values_frequencies]

    values_for_delete = []

    # Take advantage that get_column_val_frequencies(), returns inverse sorted the freqs.
    for i in range(len(frequencies)-1, -1, -1):
        if(frequencies[i] >= minimun_frequency):
           break
        else:
            values_for_delete.append(values[i])
    
    for col_value in values_for_delete:
        df = df[df[column_name] != col_value]

    return df


def camel_case_split(identifier):
    '''
    Splits camel case, it returns the parts of the initialy camel case.
    '''
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0).lower() for m in matches]

def gumtree_tokens_post_proces(tokens, stem = True, removestopwords = True, splitcamelcase = True, lowercase = True):
    '''
    Processing tokens from gumtree actions, before serve as input for tf-idf model. Returns the processed tokens.
    The processing contains:
    1) split of camel case
    2) make all words lowercase
    3) removing stopwords from nltk corpus english stopwords.
    4) stemming the words.

    '''
    if splitcamelcase:
        tokens = [camel_case_split(t) for t in tokens]
        tokens = [item for sublist in tokens for item in sublist]

    if lowercase:
        tokens = [t.lower() for t in tokens]
            
    if removestopwords:
        tokens = [t for t in tokens if t not in stopwords.words('english')]

    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]

    return tokens
    

def violations_df_gumtree_actions_tokenizer(parsed_violations_df, violation_ID_col):
    '''
    Receives as input a dataframe of parsed violations, the violations
    of which, have their before to after code fragment gumtree update script, saved on textual
    format on certain path (param: txt_gumtree_output_path).
    It returns: 1) a list of lists, where each list is a tokenized gumtree update script
                2) a parallel to 1) list , where the IDs of the violations are stored.

    param parsed_violations_df: the parsed violations dataframe
    param violation_ID_col: the column determines the violation ID.
    '''
    # update_scripts_tokens and violations_IDs, are two parallel lists where 
    # update_scripts_tokens[i] is the tokenized version of the update path of 
    # violation with ID equals to violations_IDs[i]
    update_scripts_tokens = []
    violations_IDs = []


    for row_index , row in parsed_violations_df.iterrows():
        
        update_actions = get_actions_from_gumtree_txt_diff(row)

        gumtree_actions_tokens = txt_gummtree_actions_tokenizer(update_actions)

        gumtree_actions_tokens = gumtree_tokens_post_proces(gumtree_actions_tokens)

        update_scripts_tokens.append(gumtree_actions_tokens)
        violations_IDs.append(row[violation_ID_col])

    return update_scripts_tokens, violations_IDs


def tfidfVectorizer_for_tokenized_data(analyzer= 'word', max_df = 1.0, min_df = 1, max_features = None,\
    norm = 'l2', use_idf = True, smooth_idf = True ):
    '''
    Produces tf-idf model for already tokenized and processed data.
    returns the tfidf model.

    param corpus: a list of lists of tokens, each list corresponds
    to the tokens of an observation.
    '''
    # Dummy function to serve as a dummy tokenizer and preprocessor for tf-idf model
    # as already tokenized documents will be provided
    def dummy_func(doc):
        return doc

    tfidf_model = TfidfVectorizer(
        analyzer= analyzer,
        tokenizer = dummy_func,
        preprocessor = dummy_func,
        token_pattern = None,
        max_df = max_df,
        min_df = min_df,
        max_features = max_features,
        norm = norm,
        use_idf = use_idf,
        smooth_idf = smooth_idf)

    return tfidf_model

def countVectorizer_tokenized_data(analyzer= 'word', max_df = 1.0, min_df = 1, max_features = None,\
    norm = 'l2', use_idf = True, smooth_idf = True ):
    '''
    Produces tf-idf model for already tokenized and processed data.
    returns the tfidf model.

    param corpus: a list of lists of tokens, each list corresponds
    to the tokens of an observation.
    '''
    # Dummy function to serve as a dummy tokenizer and preprocessor for tf-idf model
    # as already tokenized documents will be provided
    def dummy_func(doc):
        return doc

    vectorizer_model = CountVectorizer(
        analyzer= analyzer,
        tokenizer = dummy_func,
        preprocessor = dummy_func,
        token_pattern = None,
        max_df = max_df,
        min_df = min_df,
        max_features = max_features)

    return vectorizer_model

def distance_matrix_from_tf_matrix(tf_matrix):
    '''
    Receives as input a tf-idf matrix and returns the corresponding distance matrix,
    calculated as 1 - cosine_similarity.
    '''
    # compute cosine similarity matrix for the tf_idf matrix of the violations' gumtree diffs
    cosine_sim = cosine_similarity(tf_matrix, tf_matrix)

    # ### Clustering
    distance_matrix = 1 - cosine_sim

    # Some times 0 float numbers are equal to a very small negative float number, so

    # we make these values equal to 0.
    np.clip(distance_matrix, 0, 1, distance_matrix)

    # make diagonal equal to real zeros
    np.fill_diagonal(distance_matrix, 0)

    return distance_matrix
########################### Functions for Data Preprocessing & Preparation (END) #############################

def agglomerative_hc_custom_dmatrix(distance_matrix, nclusters, linkage, computeFullTree, distanceThresshold):
    '''
    Applies aglomerative hierarchical clustering, on an input distance matrix.
    '''
    clustering_model = AgglomerativeClustering(n_clusters=nclusters, affinity="precomputed",\
        linkage= linkage, compute_full_tree=computeFullTree, distance_threshold= distanceThresshold)

    clustering_model.fit(distance_matrix)

    return clustering_model
  
def kmeans_SSE_plot(input_X, min_clusters = 1, max_clusters = 8, step = 1,\
     max_iter = 300, tol = 1e-04, init = 'k-means++', n_init = 10, algorithm = 'auto'):
    '''
    Executes kmeans for k from min_clusters to max_clusters with a certain step (step), and
    plots the SSE (sum of squared errors / insertia) plot.
    '''
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans

    import matplotlib.pyplot as plt
    inertia_values = []

    numbers_of_clusters = range(min_clusters, max_clusters+1,step)
    
    for i in numbers_of_clusters:
        km = KMeans(n_clusters=i,  max_iter=max_iter,\
            tol=tol, init=init, n_init=n_init, random_state=1, algorithm=algorithm)
        km.fit(input_X)
        inertia_values.append(km.inertia_)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    plt.plot(numbers_of_clusters, inertia_values, color='red')
    plt.xlabel('No. of Clusters', fontsize=15)
    plt.ylabel('SSE / Inertia', fontsize=15)
    plt.title('SSE / Inertia vs No. Of Clusters', fontsize=15)
    plt.grid()
    plt.show()


def create_sub_dfs_from_clusters(initial_df, clustering_model):
    '''
    Receives as input the initial dataframe and the clustering model, and returns
    a list (lets assume it as subdf_list) of dictionaries where:

    subdf_list[i]['df']: corresponds to the rows of initial_df that clustered to cluster i.
    subdf_list[i]['rules-freq']: The rules' frequencies of the rows of the subdf_list[i]['df'] .
    '''

    # A list of dictionaries where the sub-dataframes corresponding to each cluster will be stored
    # clusters_dataframes[i]["df"], corresponds to the rows of initial_df, that clustered on i.
    clusters_dataframes = []

    # Loop through clusters
    for cluster in range(0, clustering_model.n_clusters, 1):
        
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
    for cluster in range(clustering_model.n_clusters):
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
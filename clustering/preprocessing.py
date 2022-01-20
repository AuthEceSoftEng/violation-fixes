'''
Functions for Data Preprocessing & Preparation 
Before Applying learning algorithms
'''

from pmdTools import get_column_val_frequencies
from gumtreeTools import get_actions_from_gumtree_txt_diff, txt_gummtree_actions_tokenizer, txt_gummtree_actions_tokenizer_srcml_tokens
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import re
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity


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
    gumtree_actions_tokens_raw = []

    for row_index , row in parsed_violations_df.iterrows():
        
        update_actions = get_actions_from_gumtree_txt_diff(row)

        

        gumtree_actions_tokens = txt_gummtree_actions_tokenizer(update_actions)
        # gumtree_actions_tokens = txt_gummtree_actions_tokenizer_srcml_tokens(update_actions)

        gumtree_actions_tokens_raw.append(gumtree_actions_tokens)

        # gumtree_actions_tokens = gumtree_tokens_post_proces(gumtree_actions_tokens)

        update_scripts_tokens.append(gumtree_actions_tokens)
        violations_IDs.append(row[violation_ID_col])

    return update_scripts_tokens,gumtree_actions_tokens_raw, violations_IDs


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

def distance_matrix_from_0_to_1_sim_matrix(similarity_matrix_0_1):

    # Get Distance Matrix from similarity matrix
    distance_matrix = 1 - similarity_matrix_0_1

    # Some times 0 float numbers are equal to a very small negative float number, so
    # we make these values equal to 0.
    np.clip(distance_matrix, 0, 1, distance_matrix)

    # make diagonal equal to real zeros
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix

def distance_matrix_from_tf_matrix(tf_matrix):
    '''
    Receives as input a tf-idf matrix and returns the corresponding distance matrix,
    calculated as 1 - cosine_similarity.
    '''
    # compute cosine similarity matrix for the tf_idf matrix of the violations' gumtree diffs
    cosine_sim = cosine_similarity(tf_matrix, tf_matrix)

    # ### Clustering
    distance_matrix = distance_matrix_from_0_to_1_sim_matrix(cosine_sim)

    return distance_matrix

############ Functionality for computing longest common subsequence (START) ########
# Function to find the length of the longest common subsequence of substring
# `X[0…m-1]` and `Y[0…n-1]`
def LCSLength(X, Y):
 
    m = len(X)
    n = len(Y)
 
    # lookup table stores solution to already computed subproblems;
    # i.e., `T[i][j]` stores the length of LCS of substring
    # `X[0…i-1]` and `Y[0…j-1]`
    T = [[0 for x in range(n + 1)] for y in range(m + 1)]
 
    # fill the lookup table in a bottom-up manner
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # if the current character of `X` and `Y` matches
            if X[i - 1] == Y[j - 1]:
                T[i][j] = T[i - 1][j - 1] + 1
            # otherwise, if the current character of `X` and `Y` don't match
            else:
                T[i][j] = max(T[i - 1][j], T[i][j - 1])
 
    # LCS will be the last entry in the lookup table
    return T[m][n]


def lcs_similarities(vectors_of_action_tokens):

    LCS_similarities = np.zeros((len(vectors_of_action_tokens),len(vectors_of_action_tokens)) )

    for i in range(len(vectors_of_action_tokens)):
        for j in range(i,len(vectors_of_action_tokens)):

            seq_1 = vectors_of_action_tokens[i]
            seq_2 = vectors_of_action_tokens[j]
            
            LCS_similarities[i,j] = (2 * LCSLength(seq_1, seq_2)  ) / (len(seq_1) + len(seq_2))
            LCS_similarities[j,i] = LCS_similarities[i,j]

       
    return LCS_similarities
############ Functionality for computing longest common subsequence (END) ##########

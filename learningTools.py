from pmdTools import get_column_val_frequencies
from gumtreeTools import get_actions_from_gumtree_txt_diff, txt_gummtree_actions_tokenizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.text import TfidfVectorizer

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

def violations_df_gumtree_actions_tokenizer(parsed_violations_df, txt_gumtree_output_path_col):
    '''
    Receives as input a dataframe of parsed violations, the violations
    of which, have their before to after code fragment gumtree update script, saved on textual
    format on certain path (param: txt_gumtree_output_path).
    It returns: 1) a list of lists, where each list is a tokenized gumtree update script
                2) a parallel to 1) list , where the IDs of the violations are stored.

    param parsed_violations_df: the parsed violations dataframe
    param txt_gumtree_output_path: the column determines the path where gumtree update script is stored.
    '''
    # update_scripts_tokens and violations_IDs, are two parallel lists where 
    # update_scripts_tokens[i] is the tokenized version of the update path of 
    # violation with ID equals to violations_IDs[i]
    update_scripts_tokens = []
    violations_IDs = []


    for row_index , row in parsed_violations_df.iterrows():
        
        update_actions = get_actions_from_gumtree_txt_diff(row)

        update_scripts_tokens.append(txt_gummtree_actions_tokenizer(update_actions))
        violations_IDs.append(row[txt_gumtree_output_path_col])

    return update_scripts_tokens, violations_IDs


def tfidf_for_tokenized_data(corpus):
    '''
    Produces tf-idf model for already tokenized data.
    returns the tfidf model.

    param corpus: a list of lists of tokens, each list corresponds
    to the tokens of an observation.
    '''
    # Dummy function to serve as a dummy tokenizer and preprocessor for tf-idf model
    # as already tokenized documents will be provided
    def dummy_func(doc):
        return doc

    tfidf_model = TfidfVectorizer(
        analyzer='word',
        tokenizer=dummy_func,
        preprocessor=dummy_func,
        token_pattern=None)

    return tfidf_model

def agglomerative_hc_custom_dmatrix(distance_matrix, nclusters, linkage, computeFullTree, distanceThresshold):


    
    clustering_model = AgglomerativeClustering(n_clusters=nclusters, affinity="precomputed",\
        linkage= linkage, compute_full_tree=computeFullTree, distance_threshold= distanceThresshold)

    clustering_model.fit(distance_matrix)

    return clustering_model
from kneed import KneeLocator
from numpy.random import sample
import pandas as pd
import os
import json
import subprocess
import numpy as np
import re
import math

from sklearn import cluster

from properties import github_token, path_to_commits_data, path_to_results_stats
from GHapiTools import diff_parsed
from codeParseTools import add_IDs_to_df_csv
from pmdFixesDownloader.downloader import download_commits_files, commits_files_PMD_resolved_violations
from codeParser.parser import parse_indexed_violations

from gumtreeTools import get_actions_from_gumtree_txt_diff, txt_gummtree_actions_tokenizer

# ################################### Downloading PMD fixes from Github (START) ###########################################
# max_deleted_lines_per_file = 15

# max_added_lines_per_file = 15

# max_files_per_commit = 150

# # commit items per result page
# results_per_page = 100

# # The number of pages to parse for each query.
# # # max results per query on GH API  = 1000 - (max actual (pages* results_per_page) == 1000)
# pages_limit_for_query = 10

# rulesets = "./pmdRulesets/ruleset_1.xml"
# rules =     ["AvoidPrintStackTrace" , "AvoidReassigningParameters" , "ForLoopCanBeForeach" , "ForLoopVariableCount" ,\
#     "GuardLogStatement" , "LiteralsFirstInComparisons" , "LooseCoupling" , "MethodReturnsInternalArray" , \
#     "PreserveStackTrace" ,"SystemPrintln","UnusedAssignment","UnusedLocalVariable","UseCollectionIsEmpty" , \
#     "UseVarargs" , "ControlStatementBraces","UnnecessaryFullyQualifiedName","UnnecessaryImport" , \
#     "UnnecessaryLocalBeforeReturn" , "UselessParentheses" , "ClassWithOnlyPrivateConstructorsShouldBeFinal" ,\
#     "CollapsibleIfStatements" , "ImmutableField" , "AssignmentInOperand" , "AvoidCatchingNPE" ,\
#     "AvoidLiteralsInIfCondition" , "CallSuperFirst" , "CallSuperLast" ,"CloseResource" ,"CompareObjectsWithEquals" ,\
#     "ComparisonWithNaN" ,"ConstructorCallsOverridableMethod" , "EmptyIfStmt" ,"EmptyStatementNotInLoop" ,\
#     "EqualsNull" , "NullAssignment" ,  "UseEqualsToCompareStrings" ,"AddEmptyString" , "AppendCharacterWithChar" ,\
#     "AvoidFileStream" , "ConsecutiveAppendsShouldReuse" , "InefficientStringBuffering" ,  "UseIndexOfChar" , \
#     "UselessStringValueOf"  ]
# # #ALL RULESETS:
# # rulesets =  "category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"
# # rules = []
# # query_text = "PMD violations Fixes"


# # The messages of the commits we want to query on Github's Search API.
# # search_msgs = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix", \
# #             "PMD+rule+fix", "PMD+resolve", "PMD+refactor", "PMD+fix","java+static+analysis+fix" ]

# search_msgs = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix"]

# # The Years when the commits to search, has been commited
# yearsToSearch = ["2016", "2017", "2018", "2019", "2020", "2021"]

# # commits_files = download_commits_files(github_token, path_to_commits_data, path_to_results_stats,\
# #         search_msgs, yearsToSearch, rules, max_deleted_lines_per_file, max_added_lines_per_file, pages_limit_for_query, \
# #         max_files_per_commit, results_per_page)

# commits_files = pd.read_csv("./data/commits_files_downloaded.csv")

# max_possible_modified_lines = max_deleted_lines_per_file + max_added_lines_per_file

# report_format = "xml"
# df = commits_files_PMD_resolved_violations(commits_files, report_format, rulesets,max_possible_modified_lines, path_to_commits_data, path_to_results_stats)
# ################################### Downloading PMD fixes from Github (END) ###########################################

# # Add IDs (index), to the resolved violations of the dataset colected above
# indexed_resolved_violations = add_IDs_to_df_csv("data/Resolved_violations_ruleset_1.csv", "data/Resolved_violations_ruleset_1_indexed.csv", "Violation ID")

# ############################################## Code Parsing (START) ###################################################
# # Parse before and after violations code and create code represantation
# parsed_indexed_resolved_violations = parse_indexed_violations(indexed_resolved_violations, path_to_commits_data)

# # Store the dataset of parsed violations
# parsed_indexed_resolved_violations.to_csv(path_to_results_stats + "parsed_violations.csv", index = False )

# # We hold patch fragments, where only single violations are resolved, as we want a clean training set.
# clean_parsed_indexed_resolved_violations = parsed_indexed_resolved_violations.drop_duplicates(subset=[ "fragmentBeforePatch",\
#     "fragmentAfterPatch"],  keep = False)
# # Store the dataset of clean (only one violation solvled per patch) parsed violations
# clean_parsed_indexed_resolved_violations.to_csv(path_to_results_stats + "parsed_violations_clean.csv", index = False )
# ############################################### Code Parsing (END) ####################################################

############################################### Learning Phase & Visualization (START) ################################################
import pickle
from clustering.preprocessing import delete_rows_based_on_col_frequency, violations_df_gumtree_actions_tokenizer, lcs_similarities,\
    tfidfVectorizer_for_tokenized_data, countVectorizer_tokenized_data, distance_matrix_from_0_to_1_sim_matrix
from clustering.kmeans import kmeans_SSE_plot
from clustering.kmedoids import kmedoids_inertia_values_calculate, distance_matrix_kmedoids_clustering, kmedoids_purity_plot
from clustering.tools import clusters_sub_dfs_and_data, print_cluster_rule_frequencies
from sklearn.cluster import KMeans
from clustering.dbscan import DBSCAN_execution
from clustering.visualize import mds_def_precomputed_execution, plot_2D_mds_array, plot_3D_mds_array, knns_distance_plot,\
    metric_w_knee_plot
# # Save in order to examine
# sample_df.to_csv("sample_df.csv")
#sample_df = pd.read_csv(path_to_results_stats + "parsed_violations_clean.csv")
sample_df = pd.read_csv("data/sample_df.csv")
# Random repositiong of our sample
# sample_df = sample_df.sample(frac=1)

# As we want general patterns to be extracted, only violation fixes of rules that appear more than
# a certain (minimum) frequency (minimum_rule_frequency), are held.
minimum_rule_frequency = 15
# delete the rows with rules of frequencies smaller than minimum_rule_frequency:
sample_df = delete_rows_based_on_col_frequency(
    sample_df, "Rule", minimum_rule_frequency)

# sample_df_up_vectors and sample_df_violations_IDs, are two parallel lists where
# sample_df_up_vectors[i] is the tokenized version of the update path of
# violation with ID equals to sample_df_violations_IDs[i]
sample_df_up_vectors, actions_vec, sample_df_violations_IDs = violations_df_gumtree_actions_tokenizer(
    sample_df, 'Violation ID')

# We use pickle as the calculation of the longest common subsequence is time consuming
# LCS_similarities = lcs_similarities(sample_df_up_vectors)
# pickle.dump(LCS_similarities, open("pickles/LCS_similarity_matrix_java_srcml_tokens.picke", "wb"))
LCS_similarities = pickle.load(open("pickles/LCS_similarity_matrix_java_srcml_tokens.picke","rb"))

# distance_mat = distance_matrix_from_0_to_1_sim_matrix(LCS_similarities)
# pickle.dump(distance_mat, open("pickles/LCS_distance_matrix_java_srcml_tokens.picke", "wb"))
distance_mat = pickle.load(open("pickles/LCS_distance_matrix_java_srcml_tokens.picke","rb"))

# Plot distance for the k-NN of each datapoint in ascending row.
knns_distance_plot(distance_mat, k=15, metric="precomputed", plot=True)


# 2D MDS Represantation of data
# mds_model_2D = mds_def_precomputed_execution(distance_mat, n_dimensions=2, random_state=1, n_jobs=-1)
# pickle.dump(mds_model_2D, open("pickles/MDS_2D_MDS_from_distance_matrix_JAVA_SRCMLtokens.pickle", "wb"))
mds_model_2D = pickle.load(open("pickles/MDS_2D_MDS_from_distance_matrix_JAVA_SRCMLtokens.pickle","rb"))
plot_2D_mds_array(mds_model_2D, s=5)

# 3D MDS Represantation of data
# mds_model_3D = mds_def_precomputed_execution(distance_mat, n_dimensions=3, random_state=1, n_jobs=-1)
# pickle.dump(mds_model_3D, open("pickles/MDS_3D_MDS_from_distance_matrix_JAVA_SRCMLtokens.pickle", "wb"))
mds_model_3D = pickle.load(open("pickles/MDS_3D_MDS_from_distance_matrix_JAVA_SRCMLtokens.pickle","rb"))
plot_3D_mds_array(mds_model_3D, s=5)

#### K-MEDOIDS experiment (START) ####
# Get k-medoids inertia plot
n_of_clusters, sae_values = kmedoids_inertia_values_calculate(distance_mat, min_clusters=2, max_clusters=500, step=1)

# purity_values = kmedoids_purity_plot(distance_mat, sample_df, min_clusters = 2, max_clusters = 500)
# pickle.dump(purity_values, open("pickles/purity_values_2_to_500_JAVA_SRCMLtokens.pickle", "wb"))
purity_values = pickle.load(open("pickles/purity_values_kmedoids_2_to_500_JAVA_SRCMLtokens.pickle","rb"))

# Find and print knee of kmedoids inertia plot.
kneedle = KneeLocator(n_of_clusters, sae_values, S=1.0, curve="convex", direction="decreasing")  
print("The knee of the K on k-medoids in SAE plot is:" + str(list(kneedle.all_knees)[0]))

# Plotting kmedoids inertia values for different K along with the knee value
metric_w_knee_plot(n_of_clusters, sae_values, list(kneedle.all_knees)[0], title = "SAE / Number of Clusters (Kmedoids)",
    x_label = 'Number of Clusters (K)', y_label="SAE",\
    legend = ["SAE","knee/elbow (at K="+ str(list(kneedle.all_knees)[0])+ ")" ]  )

clustering_model = distance_matrix_kmedoids_clustering(distance_mat, nclusters = list(kneedle.all_knees)[0], random_state= 1)

plot_2D_mds_array(mds_model_2D, c=clustering_model.labels_, s=5)
plot_3D_mds_array(mds_model_3D, c=clustering_model.labels_, s=2)
#### K-MEDOIDS experiment (START) ####
# clustering_model = DBSCAN_execution(distance_mat, eps=0.08, min_samples=15, metric='precomputed')




# # # Store sub-dataframes and rules frequencies for each cluster
clusters_data = clusters_sub_dfs_and_data(sample_df, clustering_model)

print_cluster_rule_frequencies(clusters_data, clustering_model)
############################################### Learning Phase & Visualization (END) ##################################################

for i_cluster in range(-1, max(clustering_model.labels_) + 1):
    print("CLUSTER: " + str(i_cluster) + " RULES:")
    for point in np.where(clustering_model.labels_ == i_cluster)[0]:
        print(sample_df.iloc[point]["Rule"])
    print("-----------------------------------------------")

# for cluster_index,cluster_medoid_i in enumerate(clustering_model.medoid_indices_):
#     print("CLUSTER " + str(cluster_index) + " medoid rule:")
#     print(sample_df.iloc[cluster_medoid_i]["Rule"])
#     print("--------------------------------------------")

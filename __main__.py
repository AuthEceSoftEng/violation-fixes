from numpy.random import sample
import pandas as pd
import os
import json
import subprocess
import numpy as np
import re
import math


from properties import github_token, path_to_commits_data, path_to_results_stats
from GHapiTools import diff_parsed
from codeParseTools import add_IDs_to_df_csv
from pmdFixesDownloader.downloader import download_commits_files, commits_files_PMD_resolved_violations
from codeParser.parser import parse_indexed_violations

from gumtreeTools import get_actions_from_gumtree_txt_diff, txt_gummtree_actions_tokenizer

#def 

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

############################################### Learning Phase (START) ################################################
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from learningTools import delete_rows_based_on_col_frequency, violations_df_gumtree_actions_tokenizer,\
    tfidf_for_tokenized_data, agglomerative_hc_custom_dmatrix
    

# # # # Save in order to examine
# # sample_df.to_csv("sample_df.csv")
sample_df = pd.read_csv(path_to_results_stats + "parsed_violations_clean.csv")
sample_df = sample_df.sample(frac=0.1)

minimum_rule_frequency = 15

sample_df = delete_rows_based_on_col_frequency(sample_df, "Rule",minimum_rule_frequency)

# update_scripts_tokens and violations_IDs, are two parallel lists where 
# update_scripts_tokens[i] is the tokenized version of the update path of 
# violation with ID equals to violations_IDs[i]
sample_df_up_vectors, sample_df_violations_IDs = violations_df_gumtree_actions_tokenizer(sample_df, 'Violation ID')

## TF - IDF
tfidf_gumtree_diffs_model = tfidf_for_tokenized_data(sample_df_up_vectors)

tf_idf_gt_diffs_matrix = tfidf_gumtree_diffs_model.fit_transform(sample_df_up_vectors)

# compute cosine similarity matrix for the tf_idf matrix of the violations' gumtree diffs
cosine_sim = cosine_similarity(tf_idf_gt_diffs_matrix, tf_idf_gt_diffs_matrix)
# print(cosine_sim)

# ### Clustering

distance_mat = 1 - cosine_sim

# Some times 0 float numbers are equal to a very small negative float number, so

# we make these values equal to 0.
np.clip(distance_mat,0,1,distance_mat)

# make diagonal equal to real zeros
np.fill_diagonal(distance_mat, 0)



# # Apply clustering for different number of clusters and calculate silhouette
# from sklearn import metrics
# n_of_clusters_list = list(range(2,min(300,len(sample_df))))
# silhouetes = []
# #clustering_model = agglomerative_hc_custom_dmatrix(distance_mat, 25, 'average', 'auto', None)
# ## Check Clusters with: sample_df.iloc[np.where(clustering_model.labels_ == 1)]["Rule"]
# for n_clusters in n_of_clusters_list:
#     print("n_clusters= " + str(n_clusters))
#     clustering_model = agglomerative_hc_custom_dmatrix(distance_mat, n_clusters, 'average', 'auto', None)
#     curr_silh = metrics.silhouette_score(distance_mat, clustering_model.labels_, metric="precomputed")
#     silhouetes.append(curr_silh)
#     print("silhouete= "+ str(curr_silh))
#     print("---------------------")

# max(silhouetes)

# Check each cluster.
# cluster = 10
# print(len(np.where(clustering_model.labels_== cluster)[0]))
# for i in np.where(clustering_model.labels_== cluster)[0]:
#     print("SIZE:")
#     print(sample_df_up_vectors[i])




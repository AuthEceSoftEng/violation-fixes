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


        
############################################### Learning Phase (START) ################################################
from learningTools import delete_rows_based_on_col_frequency, violations_df_gumtree_actions_tokenizer,\
    tfidfVectorizer_for_tokenized_data, kmeans_SSE_plot, create_sub_dfs_from_clusters
from sklearn.cluster import KMeans

# # Save in order to examine
# sample_df.to_csv("sample_df.csv")
#sample_df = pd.read_csv(path_to_results_stats + "parsed_violations_clean.csv")
sample_df = pd.read_csv("data/sample_df.csv")
# Random repositiong of our sample
sample_df = sample_df.sample(frac=1)

## As we want general patterns to be extracted, only violation fixes of rules that appear more than 
# a certain (minimum) frequency (minimum_rule_frequency), are held.
minimum_rule_frequency = 15
# delete the rows with rules of frequencies smaller than minimum_rule_frequency:
sample_df = delete_rows_based_on_col_frequency(sample_df, "Rule", minimum_rule_frequency)

# sample_df_up_vectors and sample_df_violations_IDs, are two parallel lists where 
# sample_df_up_vectors[i] is the tokenized version of the update path of 
# violation with ID equals to sample_df_violations_IDs[i]
sample_df_up_vectors, sample_df_violations_IDs = violations_df_gumtree_actions_tokenizer(sample_df, 'Violation ID')

## TF - IDF application to the tokenized update scripts
# with min_df = 15, only tokens that appear in more than 15 documents
tfidf_gumtree_diffs_model = tfidfVectorizer_for_tokenized_data(min_df = 15)

tf_idf_gt_diffs_matrix = tfidf_gumtree_diffs_model.fit_transform(sample_df_up_vectors)

# # ploting k-means' SSE for different k values.
# kmeans_SSE_plot(tf_idf_gt_diffs_matrix, min_clusters = 2, max_clusters = 500, step = 1)

# Apply k-means with selected K from the SSE plot above.
clustering_model = KMeans(n_clusters=40, random_state=1)
clustering_model.fit(tf_idf_gt_diffs_matrix)

# Store sub-dataframes and rules frequencies for each cluster
clusters_data = create_sub_dfs_from_clusters(sample_df, clustering_model)
############################################### Learning Phase (END) ##################################################

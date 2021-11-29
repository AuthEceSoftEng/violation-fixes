import pandas as pd
from properties import github_token, path_to_commits_data, path_to_results_stats
from pmdFixesDownloader.downloader import download_commits_files, commits_files_PMD_resolved_violations

################################### Downloading PMD fixes from Github (START) ###########################################
max_deleted_lines_per_file = 15

max_added_lines_per_file = 15

max_files_per_commit = 150

# commit items per result page
results_per_page = 100

# The number of pages to parse for each query.
# # max results per query on GH API  = 1000 - (max actual (pages* results_per_page) == 1000)
pages_limit_for_query = 10

rulesets = "./pmdRulesets/ruleset_1.xml"
rules =     ["AvoidPrintStackTrace" , "AvoidReassigningParameters" , "ForLoopCanBeForeach" , "ForLoopVariableCount" ,\
    "GuardLogStatement" , "LiteralsFirstInComparisons" , "LooseCoupling" , "MethodReturnsInternalArray" , \
    "PreserveStackTrace" ,"SystemPrintln","UnusedAssignment","UnusedLocalVariable","UseCollectionIsEmpty" , \
    "UseVarargs" , "ControlStatementBraces","UnnecessaryFullyQualifiedName","UnnecessaryImport" , \
    "UnnecessaryLocalBeforeReturn" , "UselessParentheses" , "ClassWithOnlyPrivateConstructorsShouldBeFinal" ,\
    "CollapsibleIfStatements" , "ImmutableField" , "AssignmentInOperand" , "AvoidCatchingNPE" ,\
    "AvoidLiteralsInIfCondition" , "CallSuperFirst" , "CallSuperLast" ,"CloseResource" ,"CompareObjectsWithEquals" ,\
    "ComparisonWithNaN" ,"ConstructorCallsOverridableMethod" , "EmptyIfStmt" ,"EmptyStatementNotInLoop" ,\
    "EqualsNull" , "NullAssignment" ,  "UseEqualsToCompareStrings" ,"AddEmptyString" , "AppendCharacterWithChar" ,\
    "AvoidFileStream" , "ConsecutiveAppendsShouldReuse" , "InefficientStringBuffering" ,  "UseIndexOfChar" , \
    "UselessStringValueOf"  ] 
# #ALL RULESETS: 
# rulesets =  "category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"
# rules = []
# query_text = "PMD violations Fixes"



# The messages of the commits we want to query on Github's Search API. 
# search_msgs = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix", \
#             "PMD+rule+fix", "PMD+resolve", "PMD+refactor", "PMD+fix","java+static+analysis+fix" ]
    
search_msgs = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix"]

# The Years when the commits to search, has been commited
yearsToSearch = ["2016", "2017", "2018", "2019", "2020", "2021"]

commits_files = download_commits_files(github_token, path_to_commits_data, path_to_results_stats,\
        search_msgs, yearsToSearch, rules, max_deleted_lines_per_file, max_added_lines_per_file, pages_limit_for_query, \
        max_files_per_commit, results_per_page)

# commits_files = pd.read_csv("./data/commits_files_downloaded.csv")

max_possible_modified_lines = max_deleted_lines_per_file + max_added_lines_per_file

report_format = "xml"
df = commits_files_PMD_resolved_violations(commits_files, report_format, rulesets,max_possible_modified_lines, path_to_commits_data, path_to_results_stats)
################################### Downloading PMD fixes from Github (END) ###########################################
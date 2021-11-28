import os
import requests
import pandas as pd
import time
from GHapiTools import diff_parsed, store_file, create_search_queries, check_ghapi_ratelimit_status
from pmdTools import PMD_report_json_to_dataframe, PMD_report_XML_to_dataframe, get_resolved_violations, \
    get_column_val_frequencies, execute_PMD
from properties import github_token, path_to_commits_data, path_to_results_stats

def download_commits_files(github_token, path_to_commits_data, path_to_results, search_msgs=["fix+pmd+violation"], \
    yearsToSearch=['2020'], rules=[], max_deleted_lines_per_file = 15, max_added_lines_per_file = 15, pages_limit_for_query = 10,\
    max_files_per_commit = 1000, results_per_page = 100):
    '''
    Downloads before and after files of commits searched by the given queries.
    '''
    # Create queries for input commits' messages and years commited.
    queries = create_search_queries(search_msgs, yearsToSearch, rules)

    # Request Headers
    headers = {'Authorization': 'token ' + github_token, \
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    # The columns of a Dataframe where the data of the files of the commits will be stored  
    commit_files_column_names = ['Commit url','Commit HashId', 'beforeFile', 'afterFile','file_patch','gh_filename']

    # The Dataframe where the data of the commits will be stored 
    commitsFiles = pd.DataFrame(columns = commit_files_column_names) 


    # A list for storing the ids of all commits that our loop has parsed
    # It is used to avoid processing the same commit more than once
    commits_parsed_ids = []
     
    for query_text in queries:

        # The complete Url corresponding to the request to Github API
        request_url = "https://api.github.com/search/commits?q=" + query_text + "&per_page=" + str(results_per_page)
                
        # Check current search API rate limit status, before request.
        check_ghapi_ratelimit_status('search', headers)   
      
        response = requests.get(request_url, headers = headers)

        # Variable indicating how many pages of the response are parsed so far.
        pages_parsed = 0

        ## Loop through results' pages
        while pages_parsed < pages_limit_for_query :

            # In this case a secondary rate limit of GH API is exceeded
            while not ('items' in response.json().keys()):
                # Sleep to avoi rate limit
                time.sleep(10)
                # The response from Gitehub's API
                response = requests.get(request_url, headers = headers)

            commits = response.json()['items']

            # Loop through results (commits) of the current page
            for i in commits:

                # If a commit has been processed already by the programm, it is skipped
                if(i['sha'] in commits_parsed_ids):
                    continue

                commits_parsed_ids.append(i['sha'])

                # Check current core rate-limit API status, before requesting a commit
                check_ghapi_ratelimit_status('core', headers)   

                # Get the actual commit's data 
                resp_commit = requests.get(i['url'], headers = headers)
                print(i['sha']) # DEBUG-line

                patch = []

                # Currently parsing only commits, having a single parent, for simplicity of code.
                # Filter the commits by the number of files modified in them.
                if len(i['parents']) == 1 and len(resp_commit.json()['files']) <= max_files_per_commit:
                    for i_file in resp_commit.json()['files']:
                        if i_file['filename'].endswith('.java'):

                            # Get the urls of the before and after version of the file
                            after_file_url = i_file['raw_url']
                            before_file_url = after_file_url.replace(i['sha'], i['parents'][0]['sha'])

                            # Get the commit's patches corresponding to the current file and its parsed version
                            try:
                                patch = i_file['patch']
                            except:
                                continue

                            # Skip files, where annotation for suppressing PMD's checks is added.
                            if( len(patch) == 0 or ("NOPMD" in patch) or ("@SuppressWarnings(\"PMD" in patch) or ("@SuppressWarnings({\"PMD" in patch) ):
                                continue

                            # Filter the files by the number of lines addedd or deleted.
                            if(i_file['additions'] <= max_added_lines_per_file and i_file['deletions'] <= max_deleted_lines_per_file):
                                
                                #### Request the before and after file page ####
                                # Check current core rate-limit API status, before requesting a file
                                check_ghapi_ratelimit_status('core', headers)  
                                before_file = requests.get(before_file_url, headers = headers)

                                # Check current core rate-limit API status, before requesting a file
                                check_ghapi_ratelimit_status('core', headers)  
                                after_file = requests.get(after_file_url, headers = headers)

                                # Get the content of before and after files' in bytes
                                try:
                                    before_file_content = before_file.content
                                    after_file_content =  after_file.content
                                except:
                                    continue

                                # Store temporarily the before and after Files localy
                                # before
                                before_file_path = (path_to_commits_data + i['sha'] + "/files/before/" + i_file['filename']).replace(" ","_")
                                store_file(before_file_path, before_file_content)

                                # after
                                after_file_path = (path_to_commits_data + i['sha'] + "/files/after/" + i_file['filename']).replace(" ","_")
                                store_file(after_file_path.replace(" ","_"), after_file_content)

                                # Store current file's data 
                                temp_df = pd.DataFrame([[i['html_url'], i['sha'], before_file_path, after_file_path, patch,i_file['filename']]] , columns = commit_files_column_names)      
                                commitsFiles = commitsFiles.append(temp_df, ignore_index = True)
                else:
                    continue
            
            pages_parsed += 1
        
            if 'next' in response.links.keys():
                # Get next page of the results            
                request_url = response.links['next']['url']

                # Check current core rate-limit API status, before requesting next page
                check_ghapi_ratelimit_status('core', headers) 

                response = requests.get(request_url, headers = headers)
            else:
                break
                                    
    # minor Bug fix, check if path_to_results exists.
    os.makedirs(path_to_results, exist_ok = True)

    # Save Data of the commits and their files.
    commitsFiles.to_csv(path_to_results + "commits_files_downloaded.csv", index = False)

    # Save SHA ids of commits parsed from the programm.
    textfile = open(path_to_results + "commits_parsed.txt", "w")
    for commit in commits_parsed_ids:  
        textfile.write(commit + "\n")
    textfile.close()

    return commitsFiles


#  Method to get the resolved PMD violations of a commit_files_df
def commits_files_PMD_resolved_violations(commit_files_df, pmd_report_format, rulesets, path_to_commits_data, path_to_results):

    if pmd_report_format == "xml":

        column_names_res = ['Commit url','Commit HashId', 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                    'endColumn', 'package', 'class', 'method', 'variable', 'Description', 'Filename','filePatch']

        column_names = ['Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                    'endColumn', 'package', 'class', 'method', 'variable', 'Description', 'Filename']

    elif pmd_report_format == "json":

        column_names_res = ['Commit url','Commit HashId', 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn','Description', 'Filename','filePatch']

        column_names = ['Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn','Description', 'Filename']

    # Data-frame, where data of possible resolved issues will be stored
    possibly_Resolved_Violations = pd.DataFrame(columns = column_names_res) 
    
    for index,row in commit_files_df.iterrows():        
        filename = row['gh_filename']

        #### Execute PMD.                           
        # Files where PMD results will be stored - Storing Results in JSON Format
        pmd_report_before = path_to_commits_data + row['Commit HashId'] + "/reports/before/" + \
        (filename.replace("/","__")).replace(".java","_java").replace(" ","_") + "." + str(pmd_report_format)

        pmd_report_after = path_to_commits_data + row['Commit HashId'] + "/reports/after/" + \
        (filename.replace("/","__")).replace(".java","_java").replace(" ","_") + "." + str(pmd_report_format)
        
        execute_PMD(row['beforeFile'], pmd_report_before, rulesets, pmd_report_format,1)
        execute_PMD(row['afterFile'], pmd_report_after, rulesets, pmd_report_format,1)
        
        #### Store The Results of PMD in desirable form. #####
        # BEFORE COMMIT FILE REPORT
        if pmd_report_format == "xml":             
            df_temp = PMD_report_XML_to_dataframe(pmd_report_before)
        elif pmd_report_format == "json":
            df_temp = PMD_report_json_to_dataframe(pmd_report_before)
        df_temp.insert(0, "Commit url", row["Commit url"])
        df_temp.insert(1, "Commit HashId", row["Commit HashId"])
        df_before_report = df_temp

        if df_before_report.empty:
            continue                 

        # AFTER COMMIT FILE REPORT
        if pmd_report_format == "xml":             
            df_temp = PMD_report_XML_to_dataframe(pmd_report_after)
        elif pmd_report_format == "json":
            df_temp = PMD_report_json_to_dataframe(pmd_report_after)
        df_temp.insert(0, "Commit url", row["Commit url"])
        df_temp.insert(1, "Commit HashId", row["Commit HashId"])
        df_after_report = df_temp
        if df_after_report.empty:
            continue

        #### Get only the fixed violations (violations that existed in before
        # reports and disappeard in after reports) ####
        # Data-frame, where data of possible resolved issues of this file will be stored
        possibly_Resolved_Violations_this_file = get_resolved_violations(df_before_report, \
                                df_after_report, column_names_res, row['file_patch'])
                        
        # Add the resolved violations of the file examined, to the dataset of all resolved violations
        # With the conditional statement bellow, 
        if(len(possibly_Resolved_Violations_this_file) <= max_deleted_lines_per_file + max_added_lines_per_file ):
            possibly_Resolved_Violations = possibly_Resolved_Violations.append( \
                                            possibly_Resolved_Violations_this_file , ignore_index = True)

    #### Store Data Properly ####
    # Save the exported data into files properly
    possibly_Resolved_Violations_clean = possibly_Resolved_Violations.drop_duplicates(subset=[ 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                    'endColumn','Description'])

    # minor Bug fix, check if path_to_results exists.
    os.makedirs(path_to_results, exist_ok = True)

    # Save the resolved PMD violations
    possibly_Resolved_Violations_clean.to_csv(path_to_results + "Resolved_violations.csv", index = False)

    # Save the frequencies of the rules on the resolved dataset.
    textfile = open(path_to_results + "resolved_rules_frequencies.txt", "w")
    for rule in get_column_val_frequencies(possibly_Resolved_Violations_clean, "Rule"):  
        textfile.write(str(rule[0]) + " --> " + str(rule[1]) + "\n")
    textfile.close()

    return possibly_Resolved_Violations_clean

if __name__ == "__main__":
    
    max_deleted_lines_per_file = 15

    max_added_lines_per_file = 15 

    max_files_per_commit = 15

    # commit items per result page
    results_per_page = 100

    # The number of pages to parse for each query.
    # # max results per query on GH API  = 1000 - (max actual (pages* results_per_page) == 1000)
    pages_limit_for_query = 5

    rulesets = "../pmdRulesets/ruleset_1.xml"
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
    

    report_format = "xml"
    df = commits_files_PMD_resolved_violations(commits_files, report_format, rulesets, path_to_commits_data, path_to_results_stats)

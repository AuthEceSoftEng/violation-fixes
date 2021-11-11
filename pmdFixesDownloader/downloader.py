import os
import requests
import pandas as pd
import numpy as np
from diffParser import diff_parsed
from pmdReport import PMD_report_json_to_dataframe,get_resolved_violations, \
    get_column_val_frequencies
from properties import github_token, max_deleted_lines_per_file, max_added_lines_per_file, \
    pages_limit_for_query, max_files_per_commit, results_per_page,  rulesets, queries
    

# store_file method
def store_file(filepath, content):
    ''' Method that allows storing certain content to a file
    with given path. If the file and its path don't exit, this method 
    creates them.
    
    param filepath: the path of the file
    param content: the content that will be stored in the file
    
    '''
    os.makedirs(os.path.dirname(filepath), exist_ok = True)
    with open(filepath, "w", encoding = "UTF-8") as f:
        f.write(content)
        

column_names = ['Commit HashId', 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn','Description', 'Filename']

# The Headers of our Request
headers = {'Authorization': 'token ' + github_token, \
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}


# Data-frame, where data of possible resolved issues will be stored
possibly_Resolved_Violations = pd.DataFrame(columns = column_names) 

# Data-frame, where data of all before and after versions of commits will be stored - MAYBE WE DO NOT NEED IT
df_before_report_full = pd.DataFrame(columns = column_names)  
df_after_report_full = pd.DataFrame(columns = column_names) 

# Looping through queries 
for query_text in queries:

    # The complete Url corresponding to the request to Github API
    request_url = "https://api.github.com/search/commits?q=" + query_text + "&per_page=" + str(results_per_page)

    # The response from Github's API
    response = requests.get(request_url, headers = headers)

    # Variable indicating how many pages of the response are parsed.
    # Used
    pages_parsed = 0;

    # A list for storing the ids of all commits that our loop has parsed
    # It is used to avoid processing the same commit more than one time
    commits_parsed_ids = []

    ## Looping through results' pages
    while ('next' in response.links.keys()) and pages_parsed < pages_limit_for_query :

        commits = response.json()['items']

        ## Looping through results (commits) of the current page
        for i in commits:

            # If a commit has been processed by the programm bellow, we skip it
            if(i['sha'] in commits_parsed_ids):
                continue

            commits_parsed_ids.append(i['sha'])

            # Getting the actual commit's content
            resp_commit = requests.get(i['url'], headers = headers)
            print(i['sha'])

            patch = []

            # Currently parsing only commits, having a single parent, for simplicity of our code.
            # Filtering the commits by the number of files modified in them.
            if len(i['parents']) == 1 and len(resp_commit.json()['files']) <= max_files_per_commit:
                for i_file in resp_commit.json()['files']:
                    if i_file['filename'].endswith('.java'):
                        # getting the urls of the before and after versions of the file
                        after_file_url = i_file['raw_url']
                        before_file_url = after_file_url.replace(i['sha'], i['parents'][0]['sha'])

                        # Getting the commit's patches corresponding to the current file and its parsed version
                        try:
                            patch = i_file['patch']
                        except:
                            continue

                        if( len(patch) > 0 ):
                            parsed_patches = diff_parsed(patch)
                        else:
                            continue;

                        # Getting more detailed information about the patch
                        added_lines = parsed_patches['added']
                        deleted_lines = parsed_patches['deleted']

                        lines_with_adds = []

                        lines_with_dels = []

                        for i_line in range(len(added_lines)):
                            lines_with_adds.append(added_lines[i_line][0])

                        for i_line in range(len(deleted_lines)):
                            lines_with_dels.append(deleted_lines[i_line][0])
                        ###############################################################################################
                        # Filtering the files by the number of lines addedd or deleted.
                        if(len(added_lines) <= max_added_lines_per_file and len(deleted_lines) <= max_deleted_lines_per_file):


                            # Requesting the before and after file page
                            before_file = requests.get(before_file_url, headers = headers)
                            after_file = requests.get(after_file_url, headers = headers)

                            # Decoding the before and after files' content to readable form
                            try:
                                before_file_content = (before_file.content).decode("utf-8")
                                after_file_content =  (after_file.content).decode("utf-8")
                            except:
                                continue

                            # Storing temporarily the before and after Files localy
                            # before
                            before_file_path = "../data/commits/" + i['sha'] + "/files/before/" + i_file['filename']
                            store_file(before_file_path, before_file_content)

                            # after
                            after_file_path = "../data/commits/" + i['sha'] + "/files/after/" + i_file['filename']
                            store_file(after_file_path, after_file_content)

                            ###########################################################################################
                            # Executing PMD.
                           
                            # Files where PMD results will be stored - Storing Results in JSON Format
                            pmd_report_before = "../data/commits/" + i['sha'] + "/reports/before/" + \
                            ((i_file['filename']).replace("/","__")).replace(".java","_java") +".json"

                            pmd_report_after = "../data/commits/" + i['sha'] + "/reports/after/" + \
                            ((i_file['filename']).replace("/","__")).replace(".java","_java") +".json"
                            
                            # Commands For Executing PMD
                            pmd_exec_command_before = "pmd.bat -d " + before_file_path + " -f json -R " + rulesets + \
                            " -reportfile "    + pmd_report_before + " -t 2" 
                            pmd_exec_command_after =  "pmd.bat -d " + after_file_path + " -f json -R " + rulesets + \
                            " -reportfile "    + pmd_report_after + " -t 2" 

                            # Executing the Commands
                            os.system(pmd_exec_command_before)
                            os.system(pmd_exec_command_after)

                            ###########################################################################################
                            # Storing The Results of PMD in desirable form.
                            # BEFORE COMMIT FILE REPORT             
                            df_before_report = PMD_report_json_to_dataframe(i,pmd_report_before, column_names)

                            if df_before_report.empty:
                                continue                 

                            # AFTER COMMIT FILE REPORT
                            df_after_report = PMD_report_json_to_dataframe(i,pmd_report_after, column_names)

                            if df_after_report.empty:
                                continue

                            df_before_report_full = df_before_report_full.append(df_before_report, ignore_index = True)
                            df_after_report_full = df_after_report_full.append(df_after_report, ignore_index = True)
                            
                            ###########################################################################################
                            # Getting only the fixed violations (violations that existed in before
                            # reports and disappeard in after reports)
                            print("OK")
                            # Data-frame, where data of possible resolved issues of this file will be stored
                            possibly_Resolved_Violations_this_file = get_resolved_violations(df_before_report, \
                                                    df_after_report, lines_with_dels, lines_with_adds,  column_names)
    
                                         
                            # Adding the resolved violations of the file examined, to the dataset of all resolved violations
                            # With the conditional statement bellow, 
                            if(len(possibly_Resolved_Violations_this_file) <= max_deleted_lines_per_file + max_added_lines_per_file ):
                                possibly_Resolved_Violations = possibly_Resolved_Violations.append( \
                                                                possibly_Resolved_Violations_this_file , ignore_index = True)
                            ###########################################################################################

            else:
                continue

        # Getting next page of the results
        request_url = response.links['next']['url']

        # The response from Github's API
        response = requests.get(request_url, headers = headers)

        pages_parsed += 1
    
#(possibly_Resolved_Violations.drop_duplicates()).to_csv("Resolved_violations.csv", index = False)
possibly_Resolved_Violations_clean = possibly_Resolved_Violations.drop_duplicates(subset=[ 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn','Description'])

possibly_Resolved_Violations_clean.to_csv("../data/Resolved_violations.csv", index = False)

# Saving the frequencies of the rules on the resolved dataset.
textfile = open("../data/resolved_rules_frequencies.txt", "w")
for rule in get_column_val_frequencies(possibly_Resolved_Violations_clean, "Rule"):  
    textfile.write(str(rule[0]) + " --> " + str(rule[1]) + "\n")
textfile.close()

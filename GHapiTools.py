import os
import requests

def check_ghapi_ratelimit_status(resourse, request_headers):
    '''
    Method for checking the current status of rate limit
    of Github's API resource.

    param resource : the resource, its rate limit is going to be checked
    '''
    # Checking our current search API rate limit status   
    rate_limit_resp = requests.get("https://api.github.com/rate_limit", headers = request_headers)
    
    while(rate_limit_resp.json()['resources'][resourse]['remaining'] == 0):
        time.sleep(1)
        rate_limit_resp = requests.get("https://api.github.com/rate_limit", headers = request_headers)  

# function to create search queries.
def create_search_queries(searchMessages, yearsOfCommits,rules):
    ''' Creates commit search queries given the commit messages to 
    be searched and the years they have been commited. Creates a query for each month 
    of a year, allows the download of a big number of commits. This happens, due to 
    the fact, that Github's API, limits the number of results of every query to 1000.
   
    param searchMessages: a list with the commit messages that are going to be searched
    param yearsOfCommits: a list with the years the commits created
    param rules: a list of strings, of rules' names to create special queries
    '''    
    months=[ "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12" ]
    queries = []

    for rule in rules:
        queries.append(rule + "+fix")

    for rule in rules:
        queries.append("PMD+" + rule )
    
    for msg in searchMessages:
        for year in yearsOfCommits:
            for idx, month in  enumerate(months):
                if month != "12":    
                    queries.append(msg + "+committer-date:" + str(year) +"-"+ str(month) + "-01.." + \
                        str(year) +"-" + str(months[idx+1]) + "-01")
                elif month == "12":
                    queries.append(msg + "+committer-date:" + str(year) +"-"+ str(month) + "-01.." + \
                        str(year) +"-" + "12-31")
                        
    return queries                    

# store_file function
def store_file(filepath, content_in_bytes):
    ''' Allows storing certain content to a file with given path.
     If the file and its path don't exit, this method 
    creates it.
    
    param filepath: the path of the file
    param content: the content that will be stored in the file
    
    '''
    os.makedirs(os.path.dirname(filepath), exist_ok = True)
    with open(filepath, "wb") as f:
        f.write(content_in_bytes)
        

'''
Functions for getting parsed commits' patches from commit's diffs. (START)
Took it from pydriller's implementation of diff_parsed() method, from here:
https://github.com/ishepard/pydriller/blob/master/pydriller/domain/commit.py
repo: https://github.com/ishepard/pydriller
'''
from typing import List,  Dict, Tuple

def _get_line_numbers(line):
    token = line.split(" ")
    numbers_old_file = token[1]
    numbers_new_file = token[2]
    delete_line_number = int(numbers_old_file.split(",")[0]
                             .replace("-", "")) - 1
    additions_line_number = int(numbers_new_file.split(",")[0]) - 1
    return delete_line_number, additions_line_number

def diff_parsed(patch) -> Dict[str, List[Tuple[int, str]]]:
    """
    Returns a dictionary with the added and deleted lines.
    The dictionary has 2 keys: "added" and "deleted", each containing the
    corresponding added or deleted lines. For both keys, the value is a
    list of Tuple (int, str), corresponding to (number of line in the file,
    actual line).
    :return: Dictionary
    """
    lines = patch.split("\n")
    modified_lines = {
        "added": [],
        "deleted": [],
    }  # type: Dict[str, List[Tuple[int, str]]]

    count_deletions = 0
    count_additions = 0

    for line in lines:
        line = line.rstrip()
        count_deletions += 1
        count_additions += 1

        if line.startswith("@@"):
            count_deletions, count_additions = _get_line_numbers(line)

        if line.startswith("-"):
            modified_lines["deleted"].append((count_deletions, line[1:]))
            count_additions -= 1

        if line.startswith("+"):
            modified_lines["added"].append((count_additions, line[1:]))
            count_deletions -= 1

        if line == r"\ No newline at end of file":
            count_deletions -= 1
            count_additions -= 1

    return modified_lines
'''
methods for getting parsed commits' patches from commit's diffs. (END)
'''   


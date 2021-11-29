# Properties 
# Github authentication Token -- Paste your GH authentication Token inside github_token.txt
with open('./github_token.txt', 'r') as file:
    github_token = file.read().replace('\n', '')

# Where before and after files along with their PMD reports will be stored.
path_to_commits_data = "./data/commits/"

# Where resolved violations' dataframe along with other results will be stored.
path_to_results_stats = "./data/"
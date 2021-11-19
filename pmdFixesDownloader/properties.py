# Properties 
# Github authentication Token -- Paste your GH authentication Token inside github_token.txt
with open('../github_token.txt', 'r') as file:
    github_token = file.read().replace('\n', '')


max_deleted_lines_per_file = 15

max_added_lines_per_file = 15 

max_files_per_commit = 15

# commit items per result page
results_per_page = 100

# The number of pages we want to parse for each query.
#max results per query on GH API  = 1000 - (max actual (pages* results_per_page) == 1000)
pages_limit_for_query = 10

rulesets = "category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"
#ALL RULESETS#"category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"  


# query_text = "PMD violations Fixes"



# The messages of the commits we want to query on Github's Search API. 
search_msgs = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix", \
            "PMD+rule+fix", "PMD+resolve", "PMD+refactor", "PMD+fix","java+static+analysis+fix" ]

# The Years when the commits to search, has been commited
yearsToSearch = ["2020","2021"]
# Properties 
# Github authentication Token 
github_token = ""

max_deleted_lines_per_file = 25

max_added_lines_per_file = 25 

max_files_per_commit = 8

# commit items per result page
results_per_page = 100

# The number of pages we want to parse for each query.
#max results per query on GH API  = 1000 - (max actual (pages* results_per_page) == 1000)
pages_limit_for_query = 10

rulesets = "category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"
#ALL RULESETS#"category/java/errorprone.xml,category/java/security.xml,category/java/bestpractices.xml,category/java/documentation.xml,category/java/performance.xml,category/java/multithreading.xml,category/java/codestyle.xml,category/java/design.xml"  

# The querrues we want to apply to Github's Search API.
# query_text = "PMD violations Fixes"

queries = ["PMD+violation+fix", "PMD+warning+fix", "PMD+error+fix", "PMD+bug+fix", \
            "PMD+rule+fix", "PMD+resolve", "PMD+refactor", "PMD+fix","static+analysis+fix" ]
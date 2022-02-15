
# thesis-static-analysis-fixes
This repo contains the code of a methodology for mining bug fix patterns, for bugs detectable by rules of the static analysis tool, *[PMD](https://pmd.github.io/)*.
## Abstract
Modern Software products, are getting bigger, more complex and involved in many aspects of human life. During the processes of software development and maintenance, programmers spend a big amount of their work time on detecting and fixing bugs. Static Analysis Tools, automatize the process of bug detection. Their use however, is limited among programming community, due to a number of problems these tools face and as the understanding and fixing of bugs, remain part of programmer's responsibilities.  

Lately, several research approaches have been presented, trying to extract useful bug fix patterns, or to automate the bug fixing process. The first, aim to the understanding of how programmers face similar problems and frequently they serve as groundwork for systems of automated bug fixing.  

Our research, aims to the extraction of useful bug fix patterns, for bugs that belong to the rules of static analysis tool, *PMD*. Initially, by providing proper queries to the *Github API*, we search for commits, that correspond to fixes of these categories of bugs. Both the before and after the commit, version of the commits' files are downloaded. Then, by executing *PMD* on the two versions of each file, individual fixes are detected and a suitable dataset is yielded. The dataset consists exclusively, from fixes of bugs detectable from rules of *PMD*. The fixes, are analyzed and by utilizing [*srcML*](https://www.srcml.org/) code representation and *tree edit distance algorithm, [Gumtree](https://github.com/GumTreeDiff/gumtree)*, the extraction of a representative sequence for each fix is possible. Afterwards, by utilizing the metric of *longest common subsequence* between two sequences of two fixes, the development of a *similarity scheme* for the dataset's fixes gets possible. This similarity scheme, operates as base for the clustering of fixes and the pattern extraction. 

In order to cluster the fixes, two separate experiments were conducted, one with *K-medoids* and one with *DBSCAN* algorithm. In both experiments, but mostly with the *DBSCAN* algorithm, almost each cluster of the extracted clusters, consists mostly of bug fixes of a certain *PMD* rule. Alongside, by computing of the number of commits and repositories from which, the fixes of each cluster come from, it gets clear, that most of the clusters arise from fixes coming from a large number of commits and repositories. Thus the extracted patterns correspond the way in which similar problems are faced, by a number of different programmers. Consequently, our extracted patterns, can be utilized as groundwork for an automatic bug fixing system, where *PMD* will serve for bug detection.  
<div style="text-align: right"><i>Michael Karatzas<br>
<a href="mailto:mikalakis@hotmail.gr">mikalakis@hotmail.gr</a>, <a href="mailto:mikalaki@ece.auth.gr">mikalaki@ece.auth.gr</a> <br>
ECE AUTH<br>
February 2022<br></i>
</div>

## Repository Structure  
Bellow you can see the directories' structure of the repository:
```
.
├── clusering/: Contains functionlity for the conducting of clustering experiments.
├── codeParser/: Contains functionlity for isolation and parsing of fixes' code fragments.
├── pmdFixesDownloader/: Contains functionlity for downloading and discovering fixes of PMD rules, leading to proper dataset creation.
├── pmdRulesets/: Contains PMD rulesets on xml format.
├── .gitignore: a simple gitignore file.
├── GHapiTools.py: Contains useful methods for Github's API querying. Used from pmdFixesDownloader package.
├── __main__.py: The main script of the project.
├── codeParseTools.py: Contains useful methods for parsing fixes' code fragments. Used from codeParser package.
├── github_token.txt: Github Auth token, used for GH Search API.
├── gumtreeTools.py: Contains useful methods for executing Gumtree and analyze its outpout.
├── pmdTools.py: Contains useful methods for executing PMD and analyze its outpout.
└── properties.py: Denotes paths where data will be stored.
```

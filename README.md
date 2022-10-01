# thesis-static-analysis-fixes
This repo contains the code of a methodology for mining bug fix patterns, for bugs detectable by rules of the static analysis tool, *[PMD](https://pmd.github.io/)*.

Contents:
  - [Title](#title)
  - [Abstract](#abstract)
  - [Repository Structure](#repository-structure)
  - [Dependencies](#dependencies)
    - [<u>External Systems involved</u>](#external-systems-involved)
    - [<u>Python Dependencies</u>](#python-dependencies)
  - [Dataset](#dataset)
  - [Execution](#execution)

## Title
Applying Data Mining Techniques to Extract Fix Patterns for Static Analysis Violations
## Abstract
Contemporary Software products, are getting larger, more complex and involved in many aspects of human life. During the processes of software development and maintenance, programmers spend a significant amount of their work time on detecting and fixing bugs. Static Analysis Tools, automate the process of bug detection. Their use however, is limited among the programming community, due to a number of problems these tools face and as the understanding and fixing of bugs, remain part of programmer's responsibilities.  

Lately, several research approaches have been presented, trying to extract useful bug fix patterns, or to automate the bug fixing process. The first focus on understanding how programmers face similar problems and frequently they serve as groundwork for systems of automated bug fixing.  

Our research aims at the extraction of useful bug fix patterns, for bugs that belong to the rules of static analysis tool *PMD*. Initially, by providing proper queries to the *Github API*, we search for commits, that correspond to fixes of these categories of bugs. Both the before and after the commit, versions of the commits' files are downloaded. Then, by executing *PMD* on the two versions of each file, individual fixes are detected and a suitable dataset is crafted. The dataset consists exclusively, from fixes of bugs detectable from rules of *PMD*. The fixes, are analyzed and by utilizing [*srcML*](https://www.srcml.org/) code representation and *tree edit distance algorithm, [Gumtree](https://github.com/GumTreeDiff/gumtree)*, a representative sequence is extracted from each fix. Afterwards, by utilizing the metric of *longest common subsequence* between two sequences of two fixes, we develop a *similarity scheme* for the dataset's fixes. This similarity scheme, operates as base for the clustering of fixes and the pattern extraction. 

In order to cluster the fixes, two separate experiments were conducted, one with *K-medoids* and one with *DBSCAN* algorithm. In both experiments, but mostly with the *DBSCAN* algorithm, almost each cluster of the extracted clusters, consists mostly of bug fixes of a certain *PMD* rule. Alongside, by computing the number of commits and repositories from which the fixes of each cluster come from, it gets clear, that most of the clusters arise from fixes coming from a large number of commits and repositories. Thus the extracted patterns correspond to the way in which similar problems are faced, by a number of different programmers. Consequently, our extracted patterns, can be utilized as groundwork for an automated bug fixing system, where *PMD* will serve for bug detection.  
<div style="text-align: right"><i>Michael Karatzas<br>
<a href="mailto:mikalakis@hotmail.gr">mikalakis@hotmail.gr</a>, <a href="mailto:mikalaki@ece.auth.gr">mikalaki@ece.auth.gr</a> <br>
ECE AUTH<br>
February 2022<br></i>
</div>

## Repository Structure  
Bellow you can see the directories' structure of the repository:
```
.
├── clusering/: Package containing functionlity for the conducting of clustering experiments.
├── codeParser/: Package containing functionlity for isolation and parsing of fixes' code fragments.
├── pmdFixesDownloader/: Package containing  functionlity for downloading and discovering fixes of PMD rules, leading to proper dataset creation.
├── pmdRulesets/: Contains PMD rulesets on xml format.
├── .gitignore: a simple gitignore file.
├── execute_full.py: a script for the full process execution.
├── GHapiTools.py: Contains useful methods for Github's API querying. Used from pmdFixesDownloader package.
├── __main__.py: The main script of the project, from which the processes and experiments were conducted.
├── codeParseTools.py: Contains useful methods for parsing fixes' code fragments. Used from codeParser package.
├── github_token.txt: Github Auth token, used for GH Search API.
├── gumtreeTools.py: Contains useful methods for executing Gumtree and analyze its outpout.
├── pmdTools.py: Contains useful methods for executing PMD and analyze its outpout.
├── properties.py: Denotes paths where data will be stored and executables.
└── save_dataset.py: a simple script used for saving, the crafted dataset of PMD fixes properly.
```

## Dependencies
Bellow, the dependencies that are needed for the execution of our methodology are listed.
### <u>External Systems involved</u>
1. *[PMD](https://pmd.github.io/)* : install *PMD* static analysis tool and its dependencies with the instructions linked [here](https://pmd.github.io/latest/pmd_userdocs_installation.html). During our executions *version 6.39.0* of *PMD* was used.
2.  [*srcML*](https://www.srcml.org/) : download and install *srcML* tool from [here](https://www.srcml.org/#download). During our executions *version 1.0.0* of *srcML* was used.
3.  *[Gumtree](https://github.com/GumTreeDiff/gumtree)* :  download and install *Gumtree* tool with the instructions linked [here](https://github.com/GumTreeDiff/gumtree/wiki/Getting-Started#installation). During our executions *version 3.0.0* of *Gumtree* was used.
### <u>Python Dependencies</u>
The external python libraries and their versions used in our methodology, are listed in [*requirements.txt*](./requirements.txt), as shown bellow:
```
kneed==0.7.0
matplotlib==3.4.2
nltk==3.6.3
numpy==1.20.3
pandas==1.3.3
requests==2.26.0
scikit_learn==1.0.2
scikit_learn_extra==0.2.0
```
The python dependencies above, can be installed, by executing:


`
pip install -r /path/to/requirements.txt
`

inside repo's directory.
<hr>

Our executions, conducted on a laptop computer with *Windows 10* operating system and *Python 3.8.3* installed on it. 
<hr>

## Dataset
The dataset, crafted for the purposes of this project, can be downloaded from [here](https://mega.nz/file/hUoBlYqS#-8tLc9dOjtj9EoCS5S0rZBw01_UPyVF1DWeceCGSAmY).

The above link, contains a zip where the dataset's files are stored, **unzip** and **read README_EN.txt** of the unzipped folder, for further information. 

The dataset consists of 11365 fixes of bugs, detectable by 43 useful rules of static analysis tool *[PMD](https://pmd.github.io/)* (version 6.39.0) . For the collection of this dataset, proper commits were searched and their files downloaded from Github's Search  API and then certain fixes were isolated by executing *[PMD](https://pmd.github.io/)*.

## Execution
In order to execute the full proccess described in this research, and recreate similar results*, you have to follow the steps bellow:
1. Firstly, all the dependencies of [Dependencies](#dependencies) section, have to be installed.
2. Paths for directories and executables, have to be provided in [*properties.py*](./properties.py) file.
3. Paste your Github authentication token in the beggining of [*github_token.txt*](./github_token.txt) file, by replacing:
   ```
   ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
   with your own token. This token must be valid and is needed for accessing Github API resources, otherwise problems are created with the execution, due to the API's rate limits. 
4. Execute the python script [*execute_full.py*](./execute_full.py) inside repo's directory, as shown bellow:
  
   `
   python execute_full.py
   `

\* the final results are going to be similar and not the exact same with our results, as the end results depend on the commits that will be fetched from Github API, *PMD* version, *srcML* version and *Gumtree* version.
<hr>

Our executions, conducted on a laptop computer with *Windows 10* operating system and *Python 3.8.3* installed on it. 
<hr>

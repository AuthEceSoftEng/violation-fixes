import pandas as pd
import os
import json
import collections
import xml.etree.ElementTree as ET
from GHapiTools import diff_parsed

from properties import pmd_executable

def execute_PMD(path_to_analyze, report_file_path, rules, reportFormat,nThreads):

    # Create folder to store the report
    os.makedirs(os.path.dirname(report_file_path), exist_ok = True)

    # Command For Executing PMD
    pmd_exec_command = pmd_executable + " -d " + path_to_analyze + " -f " + reportFormat + " -R " + rules + \
    " -reportfile "    + report_file_path + " -t " + str(nThreads)
       
    # Execute the Command
    os.system(pmd_exec_command)

# Convert PMD json reports to pandas Dataframes 
def PMD_report_json_to_dataframe( report_filepath, column_names = ['Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn','Description', 'Filename']):
    '''
    Converts PMD json reports to pandas Dataframes. The dataframe is returned by the function. 
    '''    
    # The dataframe with the PMD's report data. It is returned by the function.
    report_df = pd.DataFrame(columns = column_names)
    
    # Check if input json is empty 
    if(os.path.isfile(report_filepath) and os.path.getsize(report_filepath) > 0):
        
        # Open JSON file, used ISO-8859-1 encoding, as without it an error occured.
        f = open(report_filepath, "r", encoding = "ISO-8859-1") 

        # returns JSON object as a dictionary
        try:
            data = json.load(f)
            f.close()
        except:
            return report_df

        # Create a DataFrame from the imported Data
        data_to_df = pd.DataFrame(data["files"]); 

        # Loop through files of the report and store data to dataframe
        for index, file in data_to_df.iterrows():
            for violation in file['violations']:
                temp_df = pd.DataFrame([[ violation['rule'], violation['ruleset'],violation['beginline'],\
                                        violation['endline'],violation['begincolumn'],violation['endcolumn'], \
                                        violation['description'], (os.path.relpath(file['filename'])).replace(os.sep,"/") ]] , columns = column_names)      
                report_df = report_df.append(temp_df, ignore_index = True)
        
        # Return the dataframe with the report's data.
        return report_df


# Convert PMD json reports to pandas Dataframes 
def PMD_report_XML_to_dataframe( report_filepath, column_names = ['Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                'endColumn', 'package', 'class', 'method', 'variable', 'Description', 'Filename']):
    '''
    Converts PMD XML reports to pandas Dataframes. The dataframe is returned by the function. 
    '''    
    # The dataframe with the PMD's report data. It is returned by the function.
    report_df = pd.DataFrame(columns = column_names)
    #'src__main__java__org__perfectable__artifactable__ArtifactIdentifier_java.xml'
    try:
        mytree = ET.parse(report_filepath)
    except:
        return report_df
    root = mytree.getroot()

    for child in root:

        # Check if current node represents a file
        if (child.tag).endswith("file"):

            filename = child.attrib['name']

            for violation in child:
                # Check if current node represents a violation
                if (violation.tag).endswith("violation"):
                    
                    # Check if current violation is part of a certain method
                    if 'method' in violation.attrib:
                        curr_violation_method = violation.attrib['method']
                    else:
                        curr_violation_method = ""     

                    # Check if current violation is spotted on a certain variables
                    if 'variable' in violation.attrib:
                        curr_violation_variable = violation.attrib['variable']
                    else:
                        curr_violation_variable = "" 

                    # Check if current violation is spotted on a certain package
                    if 'package' in violation.attrib:
                        curr_violation_package = violation.attrib['package']
                    else:
                        curr_violation_package = "" 

                    # Check if current violation is spotted on a certain class
                    if 'class' in violation.attrib:
                        curr_violation_class = violation.attrib['class']
                    else:
                        curr_violation_class = "" 
                        
                    temp_df = pd.DataFrame([[ violation.attrib['rule'], violation.attrib['ruleset'], int(violation.attrib['beginline']),\
                                            int(violation.attrib['endline']), int(violation.attrib['begincolumn']), int(violation.attrib['endcolumn']), \
                                            curr_violation_package, curr_violation_class, curr_violation_method,\
                                            curr_violation_variable, ((violation.text).strip('\n')).strip('\t'), (os.path.relpath(filename)).replace(os.sep,"/") ]] , columns = column_names) 
                    report_df = report_df.append(temp_df, ignore_index = True)                    
    return report_df

# method for getting the pmd violations that existed on a before pmd report and dissapeared after
def get_resolved_violations(df_before_report, df_after_report, column_names, file_patch):

    # Get a parsed diff version of the files' patch, as it is needed for analysis bellow.
    parsed_patch = diff_parsed(file_patch)


    # Getting more detailed information about the patch
    added_lines = parsed_patch['added']
    deleted_lines = parsed_patch['deleted']
    
    lines_with_adds = []

    lines_with_dels = []

    for i_line in range(len(added_lines)):
        lines_with_adds.append(added_lines[i_line][0])

    for i_line in range(len(deleted_lines)):
        lines_with_dels.append(deleted_lines[i_line][0])
    
    
    # Data-frame, where current possible resolved issues will be stored
    current_possibly_Resolved_Violations = pd.DataFrame(columns = column_names)
    
    # Indexes for df_before_report and df_after_report dataframe
    i_before_df = 0
    i_after_df = 0
    
    # Indexes for line_with_adds and line_with_dels lists
    i_lines_w_adds = 0
    i_lines_w_dels = 0
    
    # offsets, that its value is configured based on the additions and deletions.
    beforeOffset = 0
    afterOffset = 0; 
    
    #Loop through violations
    while(i_before_df < len(df_before_report) and i_after_df < len(df_after_report) ):
                
        # Check the number of added lines up to current beginline of violation, in order to balance the after offset 
        while(i_lines_w_adds < len(lines_with_adds) and i_after_df < len(df_after_report) and \
            df_after_report.iloc[i_after_df]['beginLine'] >= lines_with_adds[i_lines_w_adds] and \
            ( df_after_report.iloc[i_after_df -1]['beginLine'] < lines_with_adds[i_lines_w_adds] or\
             i_after_df == 0)):
            i_lines_w_adds += 1
            afterOffset +=1
    
        # Check the number of added lines up to current beginline of violation, in order to balance the before offset
        while(i_lines_w_dels < len(lines_with_dels) and i_before_df < len(df_before_report) and \
            df_before_report.iloc[i_before_df]['beginLine'] >= lines_with_dels[i_lines_w_dels] and \
            ( df_before_report.iloc[i_before_df -1]['beginLine'] < lines_with_dels[i_lines_w_dels] or\
             i_before_df == 0)):
            i_lines_w_dels += 1
            beforeOffset +=1
    
    
        # Common Violations on before and after file
        if  (df_before_report.iloc[i_before_df]['Rule'] == df_after_report.iloc[i_after_df]['Rule']  and \
            df_before_report.iloc[i_before_df]['beginLine'] - beforeOffset \
             == df_after_report.iloc[i_after_df]['beginLine'] - afterOffset and \
            (df_before_report.iloc[i_before_df]['Description'] == df_after_report.iloc[i_after_df]['Description'] or \
             df_before_report.iloc[i_before_df]['beginColumn'] == df_after_report.iloc[i_after_df]['beginColumn'])):
            i_before_df +=1
            i_after_df +=1
    
        # New introduced violations on after commit's version file.
        elif (df_before_report.iloc[i_before_df]['beginLine'] - beforeOffset \
               > df_after_report.iloc[i_after_df]['beginLine'] - afterOffset):
            i_after_df +=1
    
        # Possible Fix
        elif (df_before_report.iloc[i_before_df]['beginLine'] - beforeOffset \
               <=  df_after_report.iloc[i_after_df]['beginLine'] - afterOffset): 
            resolved_row =  (df_before_report.iloc[i_before_df]).append(pd.Series(data= file_patch, index=['filePatch'])) 
            current_possibly_Resolved_Violations = current_possibly_Resolved_Violations.append( resolved_row, ignore_index = True)                                     
                                         
            i_before_df +=1;    

    # Scan violations that possible are left at the end of before_report_df (resolved violation at the end of the codefile.)
    while(i_before_df < len(df_before_report) and i_after_df >= len(df_after_report) ):
            
            resolved_row =  (df_before_report.iloc[i_before_df]).append(pd.Series(data= file_patch, index=['filePatch'])) 
            current_possibly_Resolved_Violations = current_possibly_Resolved_Violations.append( resolved_row, ignore_index = True)

            i_before_df +=1;  
    return current_possibly_Resolved_Violations

def get_column_val_frequencies(df, colname):
    '''
    Returns the absolute frequency of values of column with colname
    of the df dataframe.
    '''
    
    Resolved_Rules = df.iloc[:][colname]
    Resolved_Rules_counter = collections.Counter(Resolved_Rules)
    return Resolved_Rules_counter.most_common()
        
import pandas as pd
import os
import json
import collections

#method for executing PMD 
def execute_PMD(path_to_analyze, report_file_path, rules, reportFormat,nThreads):    
    # Commands For Executing PMD
    pmd_exec_command = "pmd.bat -d " + path_to_analyze + " -f " + reportFormat + " -R " + rules + \
    " -reportfile "    + report_file_path + " -t " + str(nThreads)
       
    # Executing the Commands
    os.system(pmd_exec_command)

# method for converting PMD json reports to pandas Dataframes 
def PMD_report_json_to_dataframe(commit, report_filepath, column_names):
    
    # The dataframe with the PMD's report data. It is returned by the function.
    report_df = pd.DataFrame(columns = column_names)
    
    # Checking if input json is empty 
    if(os.path.isfile(report_filepath) and os.path.getsize(report_filepath) > 0):
        
        # Opening JSON file, used UTF-8 encoding, as without it we had error
        f = open(report_filepath, "r", encoding = "ISO-8859-1") 

        # returns JSON object as a dictionary
        try:
            data = json.load(f)
            f.close()
        except:
            return report_df

        # Create a DataFrame from the imported Data
        data_to_df = pd.DataFrame(data["files"]); 

        # Looping through files of the report (if PMD analyzed one file, it)
        for index, file in data_to_df.iterrows():
            for violation in file['violations']:
                temp_df = pd.DataFrame([[commit['sha'], violation['rule'], violation['ruleset'],violation['beginline'],\
                                        violation['endline'],violation['begincolumn'],violation['endcolumn'], \
                                        violation['description'], os.path.relpath(file['filename']) ]] , columns = column_names)      
                report_df = report_df.append(temp_df, ignore_index = True)
        
        # Returning the dataframe with the report's data.
        return report_df


# method for getting the pmd violations that existed on a before pmd report and dissapeared after
def get_resolved_violations(df_before_report, df_after_report, lines_with_dels, lines_with_adds,  column_names):
    
    
    # Data-frame, where current possible resolved issues will be stored
    current_possibly_Resolved_Violations = pd.DataFrame(columns = column_names)
    
    i_before_df = 0;
    i_after_df = 0;
    
    i_lines_w_adds = 0;
    i_lines_w_dels = 0;
    
    # offsets, that it's value is configured based on the additions and deletions.
    beforeOffset = 0;
    afterOffset = 0; 
    
    #Looping through violations
    while(i_before_df < len(df_before_report) and i_after_df < len(df_after_report) ):
    
        # Checking the number of added lines up to current beginline of violation, in order to balance the after offset 
        while(i_lines_w_adds < len(lines_with_adds) and i_after_df < len(df_after_report) and \
            df_after_report.iloc[i_after_df]['beginLine'] >= lines_with_adds[i_lines_w_adds] and \
            ( df_after_report.iloc[i_after_df -1]['beginLine'] < lines_with_adds[i_lines_w_adds] or\
             i_after_df == 0)):
            i_lines_w_adds += 1;
            afterOffset +=1;
    
        # Checking the number of added lines up to current beginline of violation, in order to balance the before offset
        while(i_lines_w_dels < len(lines_with_dels) and i_before_df < len(df_before_report) and \
            df_before_report.iloc[i_before_df]['beginLine'] >= lines_with_dels[i_lines_w_dels] and \
            ( df_before_report.iloc[i_before_df -1]['beginLine'] < lines_with_dels[i_lines_w_dels] or\
             i_before_df == 0)):
            i_lines_w_dels += 1;
            beforeOffset +=1;
    
    
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
            current_possibly_Resolved_Violations = current_possibly_Resolved_Violations.append( \
                                        df_before_report.iloc[i_before_df] , ignore_index = True)
            i_before_df +=1;    
            
    return current_possibly_Resolved_Violations

def get_column_val_frequencies(df, colname):
    
    Resolved_Rules = df.iloc[:][colname]
    Resolved_Rules_counter = collections.Counter(Resolved_Rules)
    return Resolved_Rules_counter.most_common()
        
import pandas as pd
import re
from codeParseTools import store_string_to_file, get_lines_from_codefile, parse_and_store_lines_violation_detected,\
    executeSrcML_code_to_srcml
from gumtreeTools import  executeGumtree

def parse_indexed_violations(indexed_violations_df, path_to_commits_data):
    ''' Parse the before and after code of the resolved Violations and creates their 
    represantation (srcML) and stores them.
    Returns the dataframe contains the parsed violations information.
    ''' 
    # Column names of the dataframe of the parsed violations
    column_names = ['Violation ID', 'Commit url','Commit HashId', 'Rule', 'Rule set', 'beginLine', 'endLine', 'beginColumn',\
                        'endColumn', 'package', 'class', 'method', 'variable', 'Description', 'Filename','filePatch',\
                        # NEW COLUMNS - for code Parsing
                            'violationLines', "violationLinesPath", "violationLinesSrcmlPath","fragmentBeforePatch" ,\
                                "fragmentAfterPatch", "fragmentBeforePatchPath", "fragmentAfterPatchPath", "srcmlBeforePatchPath", "srcmlAfterPatchPath",\
                                    "gumtreeUpdatePath","gumtreeUpdatePath_txt"]

    # The dataframe where the parsed violations will be stored.
    parsed_df = pd.DataFrame(columns = column_names)

    # The offset of the spotted violation window. (case =1,the lines violation detected are saved along with the exact previous and next line) 
    violationLinesOffset = 0

    # Scan through dataframe of indexed violations rows
    for violation_index, violation in indexed_violations_df.iterrows():

        # Variables where the before and after fragment of a patch will be stored
        before_patch_fragment = ""
        after_patch_fragment = ""

        # The path of the before patch file.
        before_filepath = violation['Filename']
        # The path of the after patch file.
        after_filepath = violation['Filename'].replace("/before/","/after/")

        ##################### PARSE LINES VIOLATION SPOTTED (START) ###################################
        # The path of the file where the violation lines (along with their window) will be stored
        violationLinesPath = path_to_commits_data + violation['Commit HashId'] + "/codeFragments/before/" + \
            "violation_" + str(violation['Violation ID']) + "_ViolationLines.java"

        # The path of the file where the violation lines' srcml will be stored
        violationLinesSrcmlPath = path_to_commits_data + violation['Commit HashId'] + "/srcML/before/" + \
            "violation_" + str(violation['Violation ID']) + "_ViolationLinesSrcml.xml"
        
        try:
            violationLines = parse_and_store_lines_violation_detected(violation, violationLinesOffset, violationLinesPath)
        except:
            continue
        
        # Create and save the srcML of the lines the violation detected
        executeSrcML_code_to_srcml(violationLinesPath, violationLinesSrcmlPath)
        ##################### PARSE LINES VIOLATION SPOTTED (END) #####################################

        ##################### PARSE BEFORE AND AFTER PATCH CODE FRAGMENT (START) ######################
        # The path of the file where the code fragment before the apllication of the patch will be stored.
        before_patch_code_fragment_filepath = path_to_commits_data + violation['Commit HashId'] + "/codeFragments/before/" + \
            "violation_" + str(violation['Violation ID']) + "_beforePatchFragment.java"

        # The path of the file where the code fragment after the apllication of the patch will be stored.
        after_patch_code_fragment_filepath = path_to_commits_data + violation['Commit HashId'] + "/codeFragments/after/" + \
            "violation_" + str(violation['Violation ID']) + "_afterPatchFragment.java"

        # The path of the file where the srcml of the code fragment before the apllication of the patch will be stored.
        before_patch_fragment_scrml_filepath = path_to_commits_data + violation['Commit HashId'] + "/srcML/before/" + \
            "violation_" + str(violation['Violation ID']) + "_beforePatchFragmentSrcml.xml"
        
        # The path of the file where the srcml of the code fragment after the apllication of the patch will be stored.
        after_patch_fragment_scrml_filepath = path_to_commits_data + violation['Commit HashId'] + "/srcML/after/" + \
            "violation_" + str(violation['Violation ID']) + "_afterPatchFragmentSrcml.xml"
        
        # get before and after fragment
        for elem_index, elem in enumerate(violation["filePatch"].split("@@")):
            
            # Check if current patch's part, is line pointer (e.g. " @@ -361,7 +356,6 @@ ")
            if bool(re.match("^[ ][-][0-9]+[,][0-9]+[ ][+][0-9]+[,][0-9]+[ ]$", elem)):
                
                # split the lines' pointer properly  to get the right parts.
                patch_lines_header = elem.split(" ")

                before_lines_header = patch_lines_header[1].replace("-","")
                after_lines_header = patch_lines_header[2].replace("+","")

                before_lines_raw = before_lines_header.split(",")
                after_lines_raw = after_lines_header.split(",")

                # Saving the lines of the before and after file correspoding to patch fragment
                ## List containing the lines of the code file correspoding to the fragment before the application of patch.
                before_patch_lines = list(range( int(before_lines_raw[0]) , int(before_lines_raw[0]) + int(before_lines_raw[1])  ))
                ## List containing the lines of the code file correspoding to the fragment before the application of patch.
                after_patch_lines = list(range( int(after_lines_raw[0]) , int(after_lines_raw[0]) + int(after_lines_raw[1])  ))

                # Check if currently parsed violation is part of this patch
                if violation['beginLine'] in before_patch_lines:
                    
                    # Get before and after patch application code fragments.
                    before_patch_fragment = get_lines_from_codefile(before_filepath, before_patch_lines)
                    after_patch_fragment = get_lines_from_codefile(after_filepath, after_patch_lines)

                    # Store before and after patch application code fragments to desired location
                    store_string_to_file(before_patch_code_fragment_filepath, before_patch_fragment)
                    store_string_to_file(after_patch_code_fragment_filepath, after_patch_fragment)                 

                    # If the before, after code fragment of violation have been parsed, we end the loop.
                    break
        
        ## Create and save the srcML before and after patch application, code fragments.
        executeSrcML_code_to_srcml(before_patch_code_fragment_filepath, before_patch_fragment_scrml_filepath)
        executeSrcML_code_to_srcml(after_patch_code_fragment_filepath, after_patch_fragment_scrml_filepath)
        ##################### PARSE BEFORE AND AFTER PATCH CODE FRAGMENT (END) ######################

        # The path of the file where the update script between before and after code fragment of the patch will be stored.
        gumtree_results_json_path = path_to_commits_data + violation['Commit HashId'] + "/gumtree/" + \
            "violation_" + str(violation['Violation ID']) + "_gumtree_raw_update_script.json"

        gumtree_results_text_path = path_to_commits_data + violation['Commit HashId'] + "/gumtree/" + \
            "violation_" + str(violation['Violation ID']) + "_gumtree_raw_update_script.txt"
        # Get gumtree update scrippt for current violation
        executeGumtree("textdiff", "java-srcml", "JSON", before_patch_code_fragment_filepath, after_patch_code_fragment_filepath, gumtree_results_json_path )
        executeGumtree("textdiff", "java-srcml", "TEXT", before_patch_code_fragment_filepath, after_patch_code_fragment_filepath, gumtree_results_text_path )

        # In case no before and after fragments are scanned, we skip current violation
        if before_patch_fragment == "" and after_patch_fragment == "":
            continue
        
        # Storing the information of the parsed code, along with the input dataset data.
        temp_df = pd.DataFrame([[ violation['Violation ID'], violation['Commit url'], violation['Commit HashId'], violation['Rule'], violation['Rule set'], violation['beginLine'],\
                                            violation['endLine'], violation['beginColumn'], violation['endColumn'], violation['package'], violation['class'], \
                                            violation['method'], violation['variable'], violation['Description'], violation['Filename'], violation['filePatch'],\
                                            violationLines, violationLinesPath, violationLinesSrcmlPath, before_patch_fragment, after_patch_fragment ,\
                                                before_patch_code_fragment_filepath, after_patch_code_fragment_filepath, before_patch_fragment_scrml_filepath, after_patch_fragment_scrml_filepath,\
                                                    gumtree_results_json_path,gumtree_results_text_path ]]\
                                                , columns = column_names) 
        
        parsed_df = parsed_df.append(temp_df, ignore_index = True)
    
    # update dataframe's index, in order to be the same with violation ID.
    parsed_df["ID"] = parsed_df["Violation ID"]
    parsed_df.set_index('ID', inplace=True)
    return parsed_df
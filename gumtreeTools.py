import os
import re
import json
import subprocess
import string

def get_actions_from_gumtree_json_diff(parsed_viol_row):
    '''
    Reveices as input a complete gumtree diff result in json form and it 
    returns a list of the actions of the gumtree diffs.
    '''
    json_file_path = parsed_viol_row["gumtreeUpdatePath"]

    # Check if input json is empty 
    if(os.path.isfile(json_file_path) and os.path.getsize(json_file_path) > 0):
        
        # Open JSON file, used UTF-8 encoding, as without it an error occured.
        f = open(json_file_path, "r", encoding = "UTF-8") 

        # returns JSON object as a dictionary
        try:
            f_data = json.load(f)
            f.close()
        except:
            return ""

        actions = f_data['actions']
    return actions

def get_actions_from_gumtree_txt_diff(parsed_viol_row):
    '''
    Reveices as input a complete gumtree diff result in textual form and it 
    returns a list of the actions of the gumtree diffs.
    '''
    txt_file_path = parsed_viol_row["gumtreeUpdatePath_txt"]

    # Check if input text is empty 
    if(os.path.isfile(txt_file_path) and os.path.getsize(txt_file_path) > 0):
        
        with open(txt_file_path, 'r', encoding = "UTF-8") as f:
            f_data = f.read()
    else:
        return ""  

    # splitting on every "match", and hold the last element
    actions_data = f_data.split("===\nmatch\n---")[-1]

    # 1. === or double === , lines mean the end of a match/actions by the algorithm.
    actions_data = actions_data.replace("\n===\n===\n","\n===\n")
    actions_data = actions_data.split("\n===\n")

    # Skip first element, as it is the last match of the gumtree output
    actions_list = actions_data[1:]

    # Eliminate elements of the actions' list, equals to '\n' and '' that may occured.
    actions_list = list(filter(('\n').__ne__, actions_list))
    actions_list = list(filter(('').__ne__, actions_list))

    return actions_list

    
def txt_gummtree_actions_tokenizer(txt_actions_list):
    '''
    Gets as input a list of gumtree diff actions in textual form and "translates"
    all the actions to a list of tokens.
    '''

    # The list where all the tokens will be stored.
    update_process_vector = []
    
    # If the list of txt actions is empty, then we return a default list of tokens.
    if not txt_actions_list:
        return ["no-action"]
    
    for action in txt_actions_list:

        # Split lines of the text of each action.
        action_terms = action.splitlines()

        # for action operations we ignore if they are apllied to tree or nodes.
        action_operation = action_terms[0].split("-")[0] # ignore -node and -tree
        update_process_vector.append(action_operation)

        # loop through the other part of the action (Except operation)
        for line in action_terms[2:]:

            words = line.split(" ")
            for word_index, word in enumerate(words):
                
                # avoid empty words and if a word follows replace, is duplicate,
                # as it is part on action description, so it is skipped.
                if len(word) <= 0 or words[word_index - 1]== "replace":
                    continue

                # dont add words that describe the action, and number to our update script vector.
                elif (word[0]=="[" and word[-1]=="]") or word == "to" or word == "at" or word == "by" or word=="replace"\
                    or bool(re.match("^[0-9]+$", word)):
                    continue
                # for words ending with :, : is skipped (e.g. for "tree:", "tree" is stored )
                elif word[-1] == ":" :
                    update_process_vector.append(word[:-1])
                else:
                    update_process_vector.append(word)

    if not txt_actions_list:
        return ["no-action"]
    return update_process_vector


def txt_gummtree_actions_tokenizer_srcml_tokens(txt_actions_list):
    '''
    Gets as input a list of gumtree diff actions in textual form and "translates"
    all the actions to a list of tokens.
    '''

    srcml_tokens = [
        "annotation",  "annotation_defn",  "assert", "block",  "block_content",  "break", "call", "case", 
        "catch", "class", "comment", "condition", "constructor", "continue",  "control", 
        "decl",  "decl_stmt", "default", "do", "else",  "empty_stmt",  "enum",  
        "expr",  "expr_stmt",  "extends", "finally", "for", "function", "function_decl", "if",  
        "if_stmt",  "implements",  "import", "incr",  "index",  "init",  "interface",  
        "interface_decl", "label",  "lambda", "literal", "modifier",  "name",  "operator",  
        "package",  "parameter_list", "private",  "protected",  "public",  
        "range", "return", "specifier",  "static", "super_list",  "switch",  
        "synchronized", "ternary",  "then",  "throw",  "throws",  "try",  "type",  
        "unchecked",  "union",  "union_decl", "while"]

    # The list where all the tokens will be stored.
    update_process_vector = []
    
    # If the list of txt actions is empty, then we return a default list of tokens.
    if not txt_actions_list:
        return ["no-action"]
    
    for action in txt_actions_list:

        # Split lines of the text of each action.
        action_terms = action.splitlines()

        # for action operations we ignore if they are apllied to tree or nodes.
        action_operation = action_terms[0].split("-")[0] # ignore -node and -tree
        update_process_vector.append(action_operation)

        # loop through the other part of the action (Except operation)
        for line in action_terms[2:]:

            words = line.split(" ")
            for word_index, word in enumerate(words):
                # avoid empty words and if a word follows replace, is duplicate,
                # as it is part on action description, so it is skipped.
                if len(word) <= 0 or words[word_index - 1]== "replace":
                    continue
                elif word in srcml_tokens:
                    update_process_vector.append(word)
                # for words ending with :, : is skipped (e.g. for "tree:", "tree" is stored )
                elif word[-1] == ":" and word[:-1] in srcml_tokens:
                    update_process_vector.append(word[:-1])
                    
    if not update_process_vector:
        return ["no-action"]
    return update_process_vector
    

def executeGumtree(gumtree_mode, tree_generator, output_format, code_file_1, code_file_2, output_file ):
    
    # Constructing gumtree execution command
    command = "gumtree " + gumtree_mode + " -g "+ tree_generator + " -f "+ output_format + " " + code_file_1 +\
         " " + code_file_2 + " -o " + output_file 

    #Folder where output file will be stored.
    output_folder = os.path.dirname(output_file)

    # check if folder for output file exists, otherwise, it causes problem to gumtree.
    os.makedirs(output_folder, exist_ok = True)

    # Executing gumtree command
    subprocess.Popen(command, shell=True).wait()
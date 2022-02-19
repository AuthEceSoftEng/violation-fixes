import pandas as pd
import os
import subprocess

from properties import srcml_executable

# store_file function
def store_string_to_file(filepath, string_to_be_written):
    ''' Stores certain sting to a file with given path.
     If the file and its path don't exit, this method 
    creates it.
    
    param filepath: the path of the file
    param content: the string that will be stored in the file
    
    '''
    os.makedirs(os.path.dirname(filepath), exist_ok = True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(string_to_be_written)

def get_lines_from_codefile(code_filepath, numbers_of_lines):
    ''' Returns the content of certain lines (numbers_of_lines) of a codefile,
    with given path (code_filepath).    
    '''

    # case there are no desirable lines
    if not numbers_of_lines:
        return ""

    # We subtract 1 from every line in numbers_of_lines, as by using enumerate(f) bellow
    # the indexing for line starts at 0
    numbers_of_lines = [x-1 for x in numbers_of_lines]

    # Initialize an empty string where the lines of the code will be stored
    lines_of_code = ""
    
    f = open(code_filepath, "r", encoding = "UTF-8") 

    # Loop through lines of file
    for position, line in enumerate(f):
        if position in numbers_of_lines:
           lines_of_code = lines_of_code + line
        
        # Avoid unnecessary iterations of the for loop
        elif position > numbers_of_lines[-1]:
            break

    return lines_of_code

def parse_and_store_lines_violation_detected(violation_df_row, linesOffest = 0, path_to_save ="0"):
    '''
    1. saves the lines where the violation is detected to desired path .
    2. returns the content of the lines, where the violation is detected
    for a row of a violations' dataframe
    '''
    linesOffest = int(linesOffest)

    
    lines_to_read = list(range( violation_df_row['beginLine'] - linesOffest, violation_df_row['endLine'] + 1 + linesOffest))

    # Initialize an empty string where the lines the violation detected will be stored
    lines_violation_detected = get_lines_from_codefile(violation_df_row['Filename'], lines_to_read)

    if path_to_save != "0" and lines_violation_detected != "":
        store_string_to_file(path_to_save, lines_violation_detected)

    return lines_violation_detected


def executeSrcML_code_to_srcml(input_file, output_file ):

    command = srcml_executable + " " + input_file + " -o " + output_file + " -l Java"

    output_folder = os.path.dirname(output_file)

    # check if folder for output file exists, otherwise, it causes problem to srcml.
    os.makedirs(output_folder, exist_ok = True)

    # Executing srcml command
    subprocess.Popen(command, shell=True).wait()


def add_IDs_to_df_csv(current_df_csv_path, indexed_df_csv_path, ID_label):
    ''' Adds IDs to the rows of a dataframe saved as csv, and saves the indexed dataframe as
    csv to a given path. 

    Returns the index dataframe as dataframe.
    '''
    # open input df
    dataF = pd.read_csv(current_df_csv_path)

    # "shift" dataframe index to start from 1 instead of 0, as to avoid ID equals to 0
    dataF.index += 1

    # saving indexed dataframe as csv, to desirable path
    dataF.to_csv(indexed_df_csv_path, index = True, index_label= ID_label)

    dataF = pd.read_csv(indexed_df_csv_path) 
    dataF.index += 1

    return dataF

import pandas as pd
import shutil
import os
############################################## Saving useful PMDfixes dataset (START) ################################
# Importing indexed violations
indexed_violations = pd.read_csv("./data/Resolved_violations_ruleset_1_indexed.csv")

# Add "after Filename" column:
indexed_violations["after Filename"] = indexed_violations["Filename"]

for index, row in indexed_violations.iterrows():   
    indexed_violations.at[index,'after Filename'] = row["Filename"].replace("/before/","/after/")

    file_before_path_origin =  row["Filename"]
    file_after_path_origin =  indexed_violations.at[index,'after Filename']

    file_before_path_new = "./save_dataset/" + file_before_path_origin
    file_after_path_new = "./save_dataset/" + file_after_path_origin

    # Copying before and after file into the dataset folder
    os.makedirs(os.path.dirname(file_before_path_new), exist_ok=True)
    shutil.copy2(file_before_path_origin, file_before_path_new)

    os.makedirs(os.path.dirname(file_after_path_new), exist_ok=True)
    shutil.copy2(file_after_path_origin, file_after_path_new)

# Rearange columns
cols = indexed_violations.columns.tolist()

cols_reordered =  cols[:-2] + cols[-1:] + cols[-2:-1]

indexed_violations_reordered = indexed_violations[cols_reordered]

# Save dataset 
indexed_violations_reordered.to_csv("./save_dataset/pmdUsefulFixes_dataset.csv", index = False)
############################################## Saving useful PMDfixes dataset (END) ################################

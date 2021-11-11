
'''
methods for getting parsed commits' patches from commit's diffs. (START)
Took it from pydriller's implementation of diff_parsed() method, from here:
https://github.com/ishepard/pydriller/blob/master/pydriller/domain/commit.py
'''
from typing import List,  Dict, Tuple

def _get_line_numbers(line):
    token = line.split(" ")
    numbers_old_file = token[1]
    numbers_new_file = token[2]
    delete_line_number = int(numbers_old_file.split(",")[0]
                             .replace("-", "")) - 1
    additions_line_number = int(numbers_new_file.split(",")[0]) - 1
    return delete_line_number, additions_line_number

def diff_parsed(patch) -> Dict[str, List[Tuple[int, str]]]:
    """
    Returns a dictionary with the added and deleted lines.
    The dictionary has 2 keys: "added" and "deleted", each containing the
    corresponding added or deleted lines. For both keys, the value is a
    list of Tuple (int, str), corresponding to (number of line in the file,
    actual line).
    :return: Dictionary
    """
    lines = patch.split("\n")
    modified_lines = {
        "added": [],
        "deleted": [],
    }  # type: Dict[str, List[Tuple[int, str]]]

    count_deletions = 0
    count_additions = 0

    for line in lines:
        line = line.rstrip()
        count_deletions += 1
        count_additions += 1

        if line.startswith("@@"):
            count_deletions, count_additions = _get_line_numbers(line)

        if line.startswith("-"):
            modified_lines["deleted"].append((count_deletions, line[1:]))
            count_additions -= 1

        if line.startswith("+"):
            modified_lines["added"].append((count_additions, line[1:]))
            count_deletions -= 1

        if line == r"\ No newline at end of file":
            count_deletions -= 1
            count_additions -= 1

    return modified_lines
'''
methods for getting parsed commits' patches from commit's diffs. (END)
'''   
# TODO move to cornsnake

import os

def change_extension(input_filename, new_extension):
    """
    Change the extension of the given filename.

    Examples:
    - ('input1.txt', '.yaml') -> 'input1.yaml')
    - ('input2', '.yaml.txt') -> 'input2.yaml.txt')
    - ('input3', '.xml') -> 'input3.xml')
    """
    if not new_extension.startswith("."):
        raise ValueError(f"new_extension must start with a '.'. For example: '.txt'")
    base_filename = input_filename
    if "." in input_filename:
        parts = input_filename.split(".")
        base_filename = ".".join(parts[:-1])
    return base_filename + new_extension

def _get_last_part_of_path(file_path, sep):
    return file_path.split(sep)[-1]

def get_last_part_of_path(file_path):
    last_part = _get_last_part_of_path(file_path, os.sep)
    
    # Windows can sometimes use unix separators (e.g. from bash shell)
    if "/" in last_part:
        return _get_last_part_of_path(last_part, "/")
    return last_part

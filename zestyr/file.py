import os
import json
from pathlib import Path

user_dir = str(Path.home())
zestyr_dir = os.path.join(user_dir, '.zestyr')

if not os.path.exists(zestyr_dir):
    os.makedirs(zestyr_dir)

auth_header_file_name = os.path.join(zestyr_dir,'auth')
issue_meta_file_name = os.path.join(zestyr_dir,'issue_meta')

def get_dict(file_name):
    with open(file_name, "r") as file:
        dictionary = json.loads(file.read())
        return dictionary
    return None

def write_dict(file_name, dictionary):
    with open(file_name, "w+") as file:
        header = file.write(json.dumps(dictionary,
                                       sort_keys=True,
                                       indent=4
                                       )
                           )
        file.write("\n")
    print("    Wrote file:", file_name)


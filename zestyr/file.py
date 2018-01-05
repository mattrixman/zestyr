import re
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

# if the test case didn't exist, but was created with a different key 
# delete this file and make a new one with the right name and key 
def try_nuke_rewrite(test_case, this_file_name): 
    nuke_and_rewrite = False 
 
    with open(this_file_name, 'r') as this_file: 
        this_code=this_file.read() 
 
        mask = re.compile("^[ ]+test_case\.key = '([a-zA-Z0-9-]+)'", 
                re.MULTILINE) 
        match = re.search(mask, this_code) 
        if match: 
            specified_key = match.group(1) 
            if specified_key != test_case.key: 
                nuke_and_rewrite = True 
        else: 
            print(this_code) 
            raise ValueError("{} not found in {}".format(mask, this_file_name)) 
    if nuke_and_rewrite: 
        os.remove(this_file_name) 
        test_case.write()
        return True
    else:
        return False



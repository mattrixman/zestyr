import os
import sys
import base64
import json
from getpass import getpass
from pathlib import Path

import zestyr.file as zfile

import textwrap
def deindent(count, string):
    return textwrap.indent(text=textwrap.dedent(string)[1:-1], prefix=count*' ')

def yes_no(question, default="yes"):
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def prompt_auth_header():
    jira_user = input("jira user: ")
    jira_pass = getpass()
    auth_str = base64.encodestring('{}:{}'
        .format(jira_user, jira_pass)
        .encode('ascii')).decode('utf-8')[:-1]

    header = { "Content-Type"  : "application/json",
               "Authorization" : "Basic {}".format(auth_str) }
    return header

def get_auth_header():
    try:
        header = zfile.get_dict(zfile.auth_header_file_name)

        assert "Content-Type" in header
        assert "Authorization" in header
        print("    Warning: Your jira username and password are stored locally.")
        print("             The security gods frown upon you.")

    except IOError as e:
        header = prompt_auth_header()

    return header

# use at your own risk
def store_auth_header():
    header = prompt_auth_header()
    message = deindent(0, 
    """
    You are about to store your username and password here: {}
    Do you think that's a good idea?
    """.format(zfile.auth_header_file_name))
    if yes_no(message):
        print("This is how the bad guys win.")
        zfile.write_dict(zfile.auth_header_file_name, header)
        #TODO: OAuth

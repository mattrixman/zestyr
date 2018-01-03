import sys
import os
import argparse
import textwrap
import zestyr.user as user

def deindent(count, string):
    return textwrap.indent(text=textwrap.dedent(string)[1:-1], prefix=count*' ')

prog_name = os.path.basename(sys.argv[0])

parser = argparse.ArgumentParser(
    description='manage zephyr test cases',
    usage=deindent(0,
        """
        {0} <verb> [<args>]

        Example:
            {0} new <case description>
            {0} push <case id>
            {0} rm <case id>

        """).format(prog_name)
    )

parser.add_argument("-q", "--quiet", action="store_true", help="No output")
parser.add_argument("-v", "--verbose", action="store_true", help="More output")
parser.add_argument("-l", "--local-dry-run", action="store_true", help="Don't make changes to jira")
parser.add_argument("-d", "--dry-run", action="store_true", help="Don't make changes to jira or the filesystem")

subparsers = parser.add_subparsers(dest='verb')
subparsers.required = True

new_desc = "Create a new test case"
new_help=deindent(0,
        """
        {0} new <description>

        The `new` verb does the following:
            - Create a new test case in zephyr with <description>.
            - Write `(<key>, <id>)` to stdout
            - Create ./<caseID>.py, which can be edited to add steps to the test case"
        """.format(prog_name))
new_parser = subparsers.add_parser("new", help=new_desc, usage=new_help)
new_parser.add_argument('desc', action='store', help="A description for the new test case")


push_help=deindent(0,
        """
        {0} push <id>

        The `push` verb does the following:
            - Check the filesystem for ./<id>.py
            - Check jira for a test case with id = <id>
            - Create it if it doesn't exist (prompt user for description)
            - Overwrite any test steps associated with case <id> with the contents of <id>.py
        """.format(prog_name))

push_desc = "Upload test case modifications to Zephyr"
push_parser = subparsers.add_parser("push", help=push_desc, usage=push_help)
push_parser.add_argument('id', action="store", help="the zephyr issue id to be updated")

rm_help=deindent(4,
        """
        {0} rm <id>

        The `rm` verb does the following:
            - Check jira for a test case with id = <id>
            - Delete it if it exists
            - Delete associated steps if they exists
        """.format(prog_name))
rm_desc = "Delete test cases from Zephyr"
rm_parser = subparsers.add_parser("rm", help=rm_desc, usage=rm_help)
rm_parser.add_argument('id', action="store", help="the zephyr issue id to be deleted")

def parse(args):
    return  parser.parse_args(args[1:])

def main():
    parsed_args = parse(sys.argv)
    print(parsed_args)
    pass
    
class Case:
    def __init__(self, user, project, description):
        self.user
        self.project=project
        self.description=descrption

    def exists(self):
        # go ask jira
        pass

    def create(self):
        auth_header = user.get_auth_header()
        # go tell jira
        pass

if __name__ == "__main__":
    main()

import sys
import argcomplete, argparse
import textwrap

new_desc = "Create a new test case"
new_help = textwrap.dedent(
              """
              `{} new <description>` does the following:
              - Create a new test case in zephyr with <description>.
              - Write `(<key>, <id>)` to stdout
              - Create ./<caseID>.py, which can be edited to add steps to the test case"
              """.format(sys.argv[0])[1:])

push_desc = "Upload test case modifications to Zephyr"
push_help = textwrap.dedent(
                """
                `{} push <id>` does the following:
                  - Check the filesystem for ./<id>.py
                  - Check jira for a test case with id = <id>
                    - Create it if it doesn't exist (prompt user for description)
                  - Overwrite any test steps associated with case <id> with the contents of <id>.py
                """.format(sys.argv[0])[1:])

rm_desc = "Delete test cases from Zephyr"
rm_help = textwrap.dedent(
                """
                `{} rm <id>` does the following:
                  - Check jira for a test case with id = <id>
                    - Delete it if it exists
                    - Delete associated steps if they exists
                """.format(sys.argv[0])[1:])

parser = argparse.ArgumentParser(
        description='manage zephyr test cases',
        usage=textwrap.dedent(
            """
            {} <command> [<args>]

            The most commonly used zcase commands are:
            new     {}
            push    {}
            rm      {}
            """.format(sys.argv[0], new_desc, push_desc, rm_desc)[1:])
parser.add_argument("-q", "--quiet", action="store_true", help="No output")
parser.add_argument("-v", "--verbose", action="store_true", help="More output")
parser.add_argument("-p", "--partial-dry-run", action="store_true", help="Don't make changes to jira")
parser.add_argument("-d", "--dry-run", action="store_true", help="Don't make changes to jira or the filesystem")

subparsers = parser.add_subparsers(help="zcase commands")

new_parser = subparsers.add_parser("new")
new_parser.add_argument('desc', help="The test case description", action='store')
new_parser.set_defaults(which='add')

push_parser = subparsers.add_parser("push")
push_parser.add_argument('id', help="The test id", action="store")
push_parser.set_defaults(which='push')

rm_parser = subparsers.add_parser("rm")
rm_parser.add_argument('id', help="The test id", action="store")
rm_parser.set_defaults(which='rm')


argcomplete.autocomplete(parser)

def parse(args):
    return  parser.parse_args(args)

def main(args):
    parsed_args = parse(args)
    pass
    
class Case:
    def __init__(self, user, project, description):
        self.user
        self.projcet=project
        self.description=descrption

    def exists(self):
        # go ask jira
        pass

    def create(self):
        # go tell jira
        pass

if __name__ == "__main__":
    main(sys.argv)

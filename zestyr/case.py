import sys
import os
import re
import argparse
from textwrap import dedent
from textwrap import indent
import zestyr
import zestyr.user as user
import zestyr.http as http
import zestyr.jira as jira
import zestyr.zephyr as zephyr
from copy import deepcopy

def undent(string):
    return dedent(string)[1:-1]

def deindent(count, string):
    return indent(text=dedent(string)[1:-1], prefix=count*' ')

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
    def __init__(self, host, summary=''):
        self.host = host
        self.client = http.Client(user.get_auth_header())
        self.jira = jira.API(self.client, host)
        self.zephyr = zephyr.API(self.client, host)
        self.fields = {}
        self.fields['summary'] = summary

    # return a copy of the object which omits self.client, self.jira and self.zephyr
    def data_only(self):
        obj = type('Case', (object,), {})

        if hasattr(self, 'fields'):
            obj.fields = deepcopy(self.fields)

        if hasattr(self, 'id'):
            obj.id = deepcopy(self.id)

        if hasattr(self, 'key'):
            obj.set_key(self.get_key())

        if hasattr(self, 'steps'):
            obj.steps = deepcopy(self.steps)

        return obj

    # like above, but omit steps
    def data_only_no_steps(self):
        obj = type('Case', (object,), {})

        if hasattr(self, 'fields'):
            obj.fields = deepcopy(self.fields)

        if hasattr(self, 'id'):
            obj.id = deepcopy(self.id)

        if hasattr(self, 'key'):
            obj.key = self.get_key()

        return obj

    def make_url(self, slug):
        if slug[0] != '/':
            raise ValueError("slug must start with /")
        return "https://{}{}".format(self.host, slug)

    def create_if_not_exist(self, project_key):
        def create_j_obj():
            if 'summary' not in self.fields:
                print("Warning: adding test case without summary")
                self.fields['summary'] = ''
            j_obj = self.jira.new_test_case_in_project_with_key(project_key, self.fields['summary'])
            return j_obj

        # if this case has a key defined
        if hasattr(self, 'key'):
            # see if jira knows about it
            resp = self.client.request('GET', self.make_url('/rest/api/2/issue/{}'.format(self.get_key())))
            if resp.http_obj.status == 404:
                # if not, create it
                j_obj = create_j_obj()
            else:
                # if so, grab it
                j_obj = jira.TestCase.make(self.jira, http.exit_or_read(resp).data)

        # if no key, create a jira object and get one
        else:
            j_obj = create_j_obj()
        return j_obj

    # sync with jira and zephyr
    # when in doubt, prefer values on self
    def put_sync(self, project_key):

        # ensure an object exists within jira for this case
        j_obj = self.create_if_not_exist(project_key)

        # grab its identifying details
        self.set_key(j_obj.key)
        self.id = j_obj.id

        # update jira with values from self
        # omit steps, since they'll confuse jira
        self_data = self.data_only_no_steps()
        j_obj.__dict__.update(self_data.__dict__)
        self.jira.update_test_case(j_obj)

        # update self with values from jira
        j_case = self.jira.get_test_case_by_key(self.get_key())
        self.__dict__.update(j_case.__dict__)


        # tell zephyr to match step count
        if not hasattr(self, 'steps'):
            self.steps = []
        z_case = self.zephyr.get_steps_for_test_case(j_case)
        z_case = self.zephyr.ensure_n_steps_on(len(self.steps), z_case)

        # preserve new step id's, but update contents
        for (z_case_step, self_step) in zip(z_case.steps, self.steps):
            z_case_step.update(self_step)
        self.zephyr.update_case_steps(z_case)

        # update self with values from zephyr
        z_case = self.zephyr.get_steps_for_test_case(z_case)
        self.__dict__.update(z_case.__dict__)

    # populate self from jira and zephyr
    def pull(self, test_case_key):
        j_case = self.jira.get_test_case_by_key(test_case_key)
        z_case = self.zephyr.get_steps_for_test_case(j_case)
        self.__dict__.update(z_case.__dict__)

    def get(host, issue_key):
        # some prereq's
        client = zestyr.http.Client(user.get_auth_header())
        jira = zestyr.jira.API(client, host)
        zephyr = zestyr.zephyr.API(client, host)

        # go ask jira and zephyr
        j_obj = jira.get_test_case_by_key(issue_key)
        z_obj = zephyr.get_steps_for_test_case(j_obj)
        case = Case(host, "")
        case.__dict__.update(z_obj.__dict__)

        # populate object
        case.jira = jira
        case.zephyr = zephyr
        return case

    def create(self):
        auth_header = user.get_auth_header()
        # go tell jira
        pass

    def set_key(self, key):
        self.project = re.sub('[0-9-]', '', key)
        self.key = key

    def get_key(self):
        assert hasattr(self, 'key')
        return self.key

    def write(self):

        def one_t_quot():
            return "\"\"\""

        def t_quot(string):
            return "\"\"\"" + string + "\"\"\""

        def step_str(step):
            #    Step(step=undent("""
            #             this is a step description
            #             it might include a code fragment
            #             {code}
            #             echo hello world
            #             {code}
            #         """),
            #         data=undent("""
            #             this is a data field
            #         """),
            #         result=undent("""
            #             this is a result
            #             {code}
            #             echo goodbye
            #             {code}
            #         """)
            #     ),
            string = indent("Step(step=undent(" + one_t_quot(),     4 * ' ') + '\n' \
            + indent(step.step,                                12 * ' ') + '\n' \
            + indent(one_t_quot() + "),",                       8 * ' ') + '\n' \
            + indent("data=undent(" + one_t_quot(),             8 * ' ') + '\n' \
            + indent(step.data,                                12 * ' ') + '\n' \
            + indent(one_t_quot() + "),",                       8 * ' ') + '\n' \
            + indent("result=undent(" + one_t_quot(),           8 * ' ') + '\n' \
            + indent(step.result,                              12 * ' ') + '\n' \
            + indent(one_t_quot() + ")",                        8 * ' ') + '\n' \
            + indent("),",                                      4 * ' ') + '\n'
            return string

        try:
            summary = self.fields['summary']
        except KeyError:
            summary = ''

        try:
            description = self.fields['description'].replace('\r\n',os.linesep)
        except KeyError:
            description = ''

        file_contents = undent("""
            import zestyr
            from zestyr.zephyr import TestStep as Step
            import textwrap
            def undent(string):
                return textwrap.dedent(string)[1:-1]

            host = {0}
            key = {1}
            summary = {2}
            description = undent(\"\"\" """.format(t_quot(self.host), 
                                                t_quot(self.get_key()), 
                                                t_quot(summary)
                                                )
            ) \
        + "\n" \
        + indent(description, '    ') \
        + "\n\"\"\")\n\n" \
        + "steps = [" \
        + "\n"

        for step in self.steps:
            file_contents += step_str(step)

        file_contents += undent("""
            ]

            import os
            import re


            # return an instance of the test case defined in this file
            def make_case():
                test_case = zestyr.case.Case(host, summary)
                test_case.set_key(key)
                test_case.fields['summary'] = summary
                test_case.fields['description'] = description
                test_case.steps = steps
                return test_case

            def pull_case():
                test_case = make_case()
                test_case.pull(test_case.get_key())
                test_case.write()

            def push_case():
                test_case = make_case()
                test_case.put_sync(test_case.project)

            if __name__ == '__main__':
                case = make_case()
                print(case.__dict__)
        """)

        with open("{}.py".format(self.get_key()), "w+") as file:
            file.write(file_contents)

if __name__ == "__main__":
    main()

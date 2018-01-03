import json
from copy import deepcopy
from zestyr import context
from zestyr import http
from zestyr import file as zfile

import IPython

class TestCase():
    def __init__(self, meta, project_id, summary):
        self.fields = {}
        self.fields['issuetype'] = meta.zephyr_issue_type
        self.fields['summary'] = summary
        self.fields['project'] = { 'id' : project_id }

# Encapsulates details about the local jira/zephyr install that are unlikely to change
class Meta(http.RestCaller):

    def __init__(self, client, host, context=context.default()):
        super(Meta, self).__init__(client, host)

        try:
            # Examine Filesystem
            self.issue_meta = zfile.get_dict(zfile.issue_meta_file_name)
            assert "projects" in self.issue_meta
        except IOError:
            # Query Jira
            response = self.get('/rest/api/2/issue/createmeta')
            self.issue_meta = response.data
            zfile.write_dict(zfile.issue_meta_file_name, self.issue_meta)

        # loop over projects, map keys to id's and grab the Zephyr Issue type
        self.ids_by_key = {}
        self.zephyr_issue_type = None
        
        for project in self.issue_meta['projects']:
            self.ids_by_key[project['key']] = project['id']
            if self.zephyr_issue_type is None:
                for issue_type in project['issuetypes']:
                    if 'Zephyr Test' in issue_type['description']:
                        self.zephyr_issue_type = issue_type 

        if self.zephyr_issue_type is None:
            raise ValueError("Didn't find any issue types whose descriptions included 'Zephyr Test'")

    def get_test_case_by_key(self, key):
        response = self.get('/rest/api/2/issue/{}'.format(key))
        case_dict = response.data
        case = TestCase(self, int(case_dict['fields']['project']['id']), case_dict['fields']['summary'])
        case.__dict__.update(case_dict)
        self.print_verb_test_case("Fetched", case.key)
        return case

    def print_verb_test_case(self, verb, key):
        print("{0} Test Case {1} (http://{2}/browse/{1})"
                .format(verb, key, self.host))

    def new_test_case_in_project_with_key(self, project_key, summary):
        project_id = self.ids_by_key[project_key]
        case = TestCase(self, project_id, summary)
        response = self.post('/rest/api/2/issue', case)
        case.__dict__.update(response)
        self.print_verb_test_case("Created", case.key)
        return case

    # untested, I didn't have permissions to delete cases (got response 403)
    def delete_test_case_with_key(self, test_case_key):
        response = self.delete('/rest/api/2/issue/{}'.format(test_case_key))
        self.print_verb_test_case("Deleted", case.key)
        return response

    def update_test_case(self, content):

        #  get editable fields
        response = self.get('/rest/api/2/issue/BILT-29/editmeta')
        edit_meta = response.data

        # create an object with just those fields
        update = type('TestCaseUpdate', (object,), {})()
        update.fields = {}
        for key in edit_meta['fields'].keys():
            # not sure why--I get an error when I include these fields
            if key in ['resolution', 'issuelinks', 'comment']:
                pass
            else:
                update.fields[key] = content.fields[key]

        response = self.put('/rest/api/2/issue/{}'.format(content.key), update)
        self.print_verb_test_case("Updated", content.key)

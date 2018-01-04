import json
from zestyr import context
from zestyr import http
from zestyr import jira
from copy import deepcopy
from enum import Enum
from collections import namedtuple
import urllib

import textwrap
def deindent(count, string):
    return textwrap.indent(text=textwrap.dedent(string)[1:-1], prefix=count*' ')

class Status(Enum):
    UNEXECUTED=-1
    PASS=1
    FAIL=2
    WIP=3
    BLOCKED=4

class TestStep:
    def __init__(self, step, data, result):
        self.step = step
        self.data = data
        self.result = result

    def update(self, other):
        self.step = other.step
        self.data = other.data
        self.result = other.result


    def __repr__(self):
        return "<zephyr.TestStep: " + \
                { k : self.__dict__[k] for k in ('step', 'data', 'result')}.__repr__() + \
                ">"

    def make(zephyr_dict):
        assert 'step' in zephyr_dict or 'result' in zephyr_dict

        if 'step' not in zephyr_dict:
            zephyr_dict['step'] = ''
        if 'data' not in zephyr_dict:
            zephyr_dict['data'] = ''
        if 'result' not in zephyr_dict:
            zephyr_dict['result'] = ''

        obj = TestStep('', '', '') # update will overwrite these
        obj.__dict__.update(zephyr_dict)
        return obj

class Execution:
    def __init__(self, executionId, status, cycleId):
        self.executionId = executionId
        self.status = status
        self.cycleId = cycleId

    def make(zephyr_dict):
        assert 'executionId' in zephyr_dict and 'cycleId' in zephyr_dict

        obj = StepResult(-1, Status.UNEXECUTED, -1) # update will overwrite these
        obj.__dict__.update(zephyr_dict)
        return obj

    def __repr__(self):
        return "<zephyr.Execution: " + \
                { k : self.__dict__[k] for k in ('executionId', 'status', 'cycleId')}.__repr__() + \
                ">"
   

class StepResult:
    def __init__(self, executionId, stepId, status):
        self.executionId = executionId
        self.stepId = stepId
        self.status = status

    def make(zephyr_dict):
        assert 'executionId' in zephyr_dict and 'stepId' in zephyr_dict

        obj = StepResult(-1, '', -1, Status.UNEXECUTED) # update will overwrite these
        obj.__dict__.update(zephyr_dict)
        return obj

    def __repr__(self):
        return "<zephyr.StepResult: " + \
                { k : self.__dict__[k] for k in ('executionId', 'stepId', 'status')}.__repr__() + \
                ">"

class API(http.RestCaller):

    def __init__(self, client, host, context=context.default):
        self.jira = super(API, self)
        self.jira.__init__(client, host)

    def get_steps_for_test_case(self, case):
        response = self.get('/rest/zapi/latest/teststep/{}'.format(case.id))
        updated_case = deepcopy(case)

        updated_case.steps = []
        for step_dict in response.data:
            updated_case.steps.append(TestStep.make(step_dict))

        return updated_case

    def ensure_n_steps_on(self, n, case):
        # get the current steps
        current_steps_dict = self.get('/rest/zapi/latest/teststep/{}'.format(case.id)).data

        # copy the case and update it with server values
        updated_case = deepcopy(case)
        updated_case.steps = [TestStep.make(step) for step in current_steps_dict]

        # add/remove steps
        step_ids = [x['id'] for x in current_steps_dict]
        delta = n - len(step_ids)
        if delta == 0:
            return case
        else:
            # add steps
            if delta > 0:
                for x in range(delta):
                    new_resp = self.post('/rest/zapi/latest/teststep/{}'.format(case.id),
                            TestStep('TBD', 'TBD', 'TBD'))
                    updated_case.steps.append(TestStep.make(new_resp.data))
            # remove steps
            else:
                steps_to_keep = updated_case.steps[:delta]
                steps_to_del = updated_case.steps[delta:]
                for step in steps_to_del:
                    self.delete('/rest/zapi/latest/teststep/{}/{}'.format(case.id, step.id))
                updated_case.steps = steps_to_keep

        print("Test Case {} now has {} test steps".format(case.key, n))
        return updated_case

    def update_case_steps(self, case):
        for step in case.steps:
            self.put('/rest/zapi/latest/teststep/{}/{}'.format(case.id, step.id), step)
        print("Updated Steps on Test Case {}".format(case.key))
        return case

    def get_cycles_for_project_with_id(self, proj_id):
        Cycle = namedtuple("Cycle", "version_id cycle_id name description active")

        def boolean(string):
            if string == 'true' or string == 'True':
                return True
            if string == 'false' or string == 'False':
                return False

        cycles = []
        cycles_dict = self.get('/rest/zapi/latest/cycle?projectId={}'.format(proj_id)).data   
        for (version_id, version_list) in cycles_dict.items():
            if version_id != '-1':
                for cycle_dict in version_list:
                    for (cycle_id, cycle) in cycle_dict.items():
                        try:
                            cycles.append(Cycle(version_id,
                                cycle_id,
                                cycle['name'],
                                cycle['description'],
                                boolean(cycle['started']) and not boolean(cycle['ended'])))
                        except TypeError:
                            pass # skip record count
        return cycles

    def get_cycles_for_test_with_key(self, test_case_key):
        Cycle = namedtuple("Cycle", "version_id version_name cycle_id cycle_name")

        query = deindent(0,
        """
        issue = "{}" AND cycleName != "Ad Hoc"
        """.format(test_case_key))
        encoded_query = urllib.parse.quote(query)
        result = self.get('/rest/zapi/latest/zql/executeSearch?zqlQuery={}'.format(encoded_query)).data
        if result['totalCount'] > result['maxResultAllowed']:
            raise ValueError("Only some query results returned, try again with an offset to get the other wones")
            # TODO: walk the full set of results, even if it takes multiple queries
            # or find a better way to query

        cycles = []
        for execution in result['executions']:
            cycles.append(Cycle(execution['versionId'],
                                execution['versionName'],
                                execution['cycleId'],
                                execution['cycleName']))
        return cycles


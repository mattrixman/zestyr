import json
from zestyr import context
from zestyr import http
from zestyr import jira
from copy import deepcopy

class TestStep:
    def __init__(self, step, data, result):
        self.step = step
        self.data = data
        self.result = result

    def __repr__(self):
        return { k : self.__dict__[k] for k in ('step', 'data', 'result')}.__repr__()

    def make(zephyr_dict):
        assert('step' in zephyr_dict)
        assert('data' in zephyr_dict)
        assert('result' in zephyr_dict)
        obj = TestStep('', '', '') # update will set these
        obj.__dict__.update(zephyr_dict)
        return obj

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

        return updated_case

    def update_case_steps(self, case):
        for step in case.steps:
            self.put('/rest/zapi/latest/teststep/{}/{}'.format(case.id, step.id), step)
        return case



# Installation

    pip install -e .

# Usage Examples

### update jira

    import zestyr
    host = "jira.dev.clover.com"
    client = zestyr.http.Client(zestyr.user.get_auth_header())
    jira = zestyr.jira.API(client, host)
    case = jira.get_test_case_by_key('BILT-29')
    
    case.fields['summary'] = 'dummy test case O'
    case.fields['description'] = 'dummy description O'
    
    jira.update_test_case(case)

### update zephyr test case

    import zestyr
    host = "jira.dev.clover.com"
    client = zestyr.http.Client(zestyr.user.get_auth_header())
    jira = zestyr.jira.API(client, host)
    zephyr = zestyr.zephyr.API(client, host)
    
    j_case = jira.get_test_case_by_key('BILT-30')
    z_case = zephyr.get_steps_for_test_case(j_case)
    
    z_case = zephyr.ensure_n_steps_on(4, z_case)
    z_case.steps[0].step = 'foo'
    z_case.steps[1].data = 'bar'
    z_case.steps[2].result = 'baz'
    z_case.steps[3].step = 'step'
    z_case.steps[3].data = 'data'
    z_case.steps[3].result = 'result'
    
    zephyr.update_case_steps(z_case)

### get cycles in project

    import zestyr
    host = "jira.dev.clover.com"
    client = zestyr.http.Client(zestyr.user.get_auth_header())
    jira = zestyr.jira.API(client, host)
    zephyr = zestyr.zephyr.API(client, host)
    cycles = zephyr.get_cycles_for_project_with_id(jira.ids_by_key['BILT'])

### get cycles for test

    import zestyr
    host = "jira.dev.clover.com"
    client = zestyr.http.Client(zestyr.user.get_auth_header())
    jira = zestyr.jira.API(client, host)
    zephyr = zestyr.zephyr.API(client, host)
    cycles = zephyr.get_cycles_for_test_with_key('BILT-16')

### create a zephyr test case

    import zestyr
    test_case = zestyr.case.Case('jira.dev.clover.com', 'yet another dummy test case 5')
    test_case.steps = [zestyr.zephyr.TestStep('foo', 'bar', 'baz'), zestyr.zephyr.TestStep('FOO', 'BAR', 'BAZ')]
    test_case.put_sync('BILT') # project key

### overwrite a zephyr test case

    import zestyr
    test_case = zestyr.case.Case('jira.dev.clover.com', 'yet another dummy test case 6')
    test_case.key = 'BILT-40'
    test_case.steps = [zestyr.zephyr.TestStep('foo', 'bar', 'baz'), zestyr.zephyr.TestStep('FOO', 'BAR', 'BAZ')]
    test_case.put_sync('BILT') # project key

### pull a zephyr test case

    import zestyr
    test_case = zestyr.case.Case('jira.dev.clover.com', '')
    test_case.pull('BILT-53')

### another way to pull a zephyr test case

    import zestyr                                              
    tc = zestyr.case.Case.get('jira.dev.clover.com', 'BILT-16')
    tc.write()

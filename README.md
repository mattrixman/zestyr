# Zestyr
### *Z*ephyr *E*mits *S*teps *T*hen *Y*ou *R*un'em

    Zestyr is a python api for Zephyr which aims to provided automated execution of test cycles.  Imagine a chron job that executes a test cycle before you come to work so you can analyze the test results when you get in.  Here's how Zestyr helps with that:

 1. At 1:00 AM, Chron tells Zestyr to run test cycle `alpha`.
 2. Zestyr finds and runs all test cases in `alpha`, storing the results locally
 3. You view the results and tell Zestyr to push the results to Zephyr
 4. Zestyr creates Zephyr test executions and populates them with the results, providing you with hyperlinks to the failed test executions
 5. You annotate those executions and create issues for the failed test executions


#### Commands

The above vision is not yet complete.  Here's the current target:

| Command | Action |
| `zcase new "An awesome test"` | Contact jira and create a new zephyr test case (i.e. Jira Issue), store an empty zestyr test case in the current working directory (e.g. `BILLT-97.py`) and output the jira key and id for the new issue (e.g. `(ISVT-70, 86587)`) |
| `zcase push BILLT-97` | Contact jira and overwrite whatever test steps exist for BILLT-97 with those in BILLT-97.py |
| `zcase rm BILLT-97` | Contact jira and remove the zephyr test case BILLT-97 |
| `zexec case BILLT-97` | Contact zephyr and create a new ad-hoc execution for BILLT-97, mark the first step as in-progress.  Store the results locally output the zephyr id for this execution (e.g. `14291`) |
| `zexec push 14291` | Push the contents of the indicated test execution to zephyr.  Output a hyperlink to the updated test case.  Warn if it contains a failure |

It's not complete either.

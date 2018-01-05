# Zestyr
### **Z**ephyr **E**mits **S**teps **T**hen **Y**ou **R**un'em

#### Running tests

Zestyr is a python api for Zephyr which aims to provide automated execution of test cycles.  Imagine the scheduled execution of a test cycle before you make it to the office.  Here's how Zestyr helps with that:

 0. The night before, you configure chron to run `zexec --cycle 'Monday' --version 'beta'` at 1:00 AM
 1. At 1:00 AM, Chron calls Zestyr
 2. Zestyr finds and runs the relevant tests, updating zephyr with the status of each test step, and attaching both STDOUT and STDERR to the relevant test step
 3. Zestyr prints links to all of the test executions it performed
 4. At 9:00 AM you arrive and view the executions, add some comments, and create some issues for the failures.

#### Managing test cases

Zestyr also allows you to pull test cases from zephyr into your local directory (where you can edit them), and then push them back up to zephyr (where your updates will be applied).  

It might not be obvious why you'd want to do this.  Here's my reasoning:

Zephyr is good at presenting test results to humans, so you probably want human-readable representations of each test step in zephyr.  On the other hand it makes a pretty shabby version control system--so you probably *shouldn't* store your test automation in zephyr.  You'll want a tight correspondence between test steps in zephyr and segments of code in your automation repo so that a failed step tells a rather specific story.  Maintaining this correspondence by hand sounds like a terrible pain.  My strategy is to make the automation repository the single-source-of-truth for test cases and store them as zestyr-generated python scripts.  Then I use zestyr to keep zephyr up to date.  To sync zephyr to git, you can do a `zestyr pull` followed by a `git push`, and to sync git to zephyr, you can do a `git pull` and a `zephyr push`.

#### Install

You'll need python3 installed

    sudo -H pip3 install -e <dir/containing/setup.py>

(Or, if you're in a python3 venv: `pip install -e <dir/containing/setup.py>`)

#### Uninstall

    sudo -H pip3 uninstall zestyr

#### Commands

The above vision is not yet complete.  Here's the goal:

| Command | Action |
|:--|:--|
| `zstr new "An awesome test"` --proj-key PROJ | Create a new test zephyr test case (i.e. Jira Issue), store an empty zestyr test case in the current working directory (e.g. `TEST-70.py`) and output the jira key and id for the new issue (e.g. `(ISVT-70, 86587)`) |
| `zstr pull TEST-97` | Write the steps in TEST-97 to the current directory (TEST-97.py) |
| `zstr push TEST-97.py` | Overwrite whatever test steps exist for TEST-97 with those in TEST-97.py |
| `python TEST-97.py --show` | Print the steps in `TEST-97.py` |
| `python TEST-97.py` | Execute the test contained in `TEST-97.py`, store the results in the ad-hoc cycle |
| `python TEST-97.py --cycle 'foo' --version 'bar'` | Execute the test contained in `TEST-97.py`, store the results in the cycle called 'foo' under the version called 'bar' |
| `zstr run --cycle 'foo' --version 'bar'` | Pull one case for each unexecuted execution in the 'foo' cycle against the 'bar' version, execute them, and set the status of those executions. |

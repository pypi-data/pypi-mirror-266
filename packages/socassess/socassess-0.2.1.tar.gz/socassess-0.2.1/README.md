# Socrates Assess

This is a tool to assist assessment creators to create test-based assessments
that can provide high-quality formative feedback.

![Generate automated feedback](doc/automated.png)

However, if an unexpected test failure happens.

![No automated feedback available](doc/diagram.png)

## Prepare a python environment

Since `socassess` is a Python package, here we use `poetry` for package
management and to handle our virtual environment.

```
poetry new hw1
```

Install SocAssess and then activate the virtual environment.

```
cd hw1
poetry add socassess
poetry shell
```

You should be able to assess the `socassess` command now.

```
socassess -h
```

```
usage: socassess [-h] {create,feedback} ...

positional arguments:
  {create,feedback}
    create           Create SocAssess starter code in a new folder
    feedback         Generate feedback

options:
  -h, --help         show this help message and exit
```

## Create the starter code

The original hw1/hw1 can be deleted. We will use SocAssess to re-create one with
starter code in it.

```
rm -r hw1
socassess create --name hw1
```

```
Assessment folder is created! Let's give it a try.
    cd hw1
To see the automated feedback:
    socassess feedback --config=socassess.toml --artifacts=artifacts --ansdir=stu --probing=probing_tests --feedback=maps
To inspect pytest outcomes:
    socassess feedback --artifacts=artifacts --ansdir=stu --probing=probing_tests
Or you can just use `pytest`
    pytest -vv --artifacts=artifacts --ansdir=stu probing_tests
For more info
    socassess --help
Take a look at the code in ./hw1 and have fun!
```

Running just the probing tests.

```
socassess feedback --artifacts=artifacts --ansdir=stu --probing=probing_tests
```

```
...
collected 2 items

probing_tests/test_it.py::test_exist PASSED                                                                             [ 50%]
probing_tests/test_it.py::test_content PASSED                                                                           [100%]

- generated xml file: .../hw1/hw1/artifacts/report.xml -
```

Those pass and fail outcomes will be mapped to

```
socassess feedback --config=socassess.toml --artifacts=artifacts --ansdir=stu --probing=probing_tests --feedback=maps
```

```
# Feedback

## general

Nice! Your answer looks good!
```

Take a look at the code inside the folder and have fun!

## A more complicated example

You can find it in examples/a1

```
cd examples/a1
poetry install
poetry shell
cd a1  # examples/a1/a1
```

Probing test outcomes

```
socassess feedback --artifacts=artifacts --ansdir=stu --probing=probing_tests
```

```
...
probing_tests/test_it.py::test_exist PASSED                                                                             [ 11%]
probing_tests/test_it.py::test_single PASSED                                                                            [ 22%]
probing_tests/test_it.py::test_combined_1 PASSED                                                                        [ 33%]
probing_tests/test_it.py::test_combined_2 PASSED                                                                        [ 44%]
probing_tests/test_it.py::test_level_lowest PASSED                                                                      [ 55%]
probing_tests/test_it.py::test_level_medium_1 PASSED                                                                    [ 66%]
probing_tests/test_it.py::test_level_medium_2 PASSED                                                                    [ 77%]
probing_tests/test_it.py::test_ai FAILED                                                                                [ 88%]
probing_tests/test_it.py::test_email FAILED                                                                             [100%]

========================================================== FAILURES ===========================================================
auto-feedback/socassess/examples/a1/a1/probing_tests/test_it.py:46: AssertionError: failed due to unknown reason
auto-feedback/socassess/examples/a1/a1/probing_tests/test_it.py:58: AssertionError: failed due to unknown reason
----------------------- generated xml file: auto-feedback/socassess/examples/a1/a1/artifacts/report.xml -----------------------
=================================================== short test summary info ===================================================
FAILED probing_tests/test_it.py::test_ai - AssertionError: failed due to unknown reason
FAILED probing_tests/test_it.py::test_email - AssertionError: failed due to unknown reason
```

Generated feedback

```
socassess feedback --config=socassess.toml --artifacts=artifacts --ansdir=stu --probing=probing_tests --feedback=maps
```

```
# Feedback

## single

Congrats! test_single passed

## combined

Congrats! test_combined_1 and test_combined_2 passed

## level

Congrats! test_level_medium_1 passed. This feedback should be shown.
Congrats! test_level_medium_2 passed. This feedback should be shown.

## non_auto

non_auto: automated feedback is not available
```

### Use AI and/or Email

If in `socassess.toml`, you set `ai` and/or `email` to `true`, and filled
corresponding fields. Then socassess will seek AI feedback and/or send an email
to seek human help.

```toml
[feature]
ai = true
email = true
```

```toml
[email]

[email.account]
account = 'account'  # the sender account of the mail server
password = "pswd"  # the password to login to the mail server
from = 'from@address.com'  # the email address to use under the account
to = "to@address.com"  # to which address the email is sent, i.e., the expert email
smtp_server = "smtp.server.com"  # the SMTP server to use

[email.content]
subject = "[SocAssess][Assignment 1] Human feedback needed"
email_body = '''
SocAssess is needing human feedback.
The attached files contain relevant context of the submission.

See attachments
'''
initial_reply = '''
An instructor has been notified for questions where pre-coded feedback are not available.
'''  # the initial feedback to be shown to let the student know that automated feedback is not available


[openai]
openai_key = "<key>, if empty, use OPENAI_KEY environment variable"
model = "gpt-3.5-turbo"
temperature = 1
max_tokens = 2048
top_p = 1
frequency_penalty = 0
presence_penalty = 0
system_prompt = """\
You are an expert in assessing students' answers. Your message will be sent \
directly to students. When the instructor provides you with a student's answer, \
you will give a short feedback message to correct student's misunderstanding, \
but without leaking any infomation of the canonical or correct answer directly. \
       """  # per TOML spec, in "" string, "\" will be used to trim whitespaces and newlines
template = '''
AI generated feedback:
{feedback}'''  # support one key: `feedback`; AI response will replace {feedback}
```

```
## non_auto

AI generated feedback:
Good effort on adding content to your answer file! Make sure to review the
question prompt and ensure that your response directly addresses all aspects of
the question for a comprehensive answer. Keep up the good work!

## _email

An instructor has been notified for questions where pre-coded feedback are not available.
```

### Unit test for the assessment code in examples/a1

```
cd examples/a1
pytest -v tests
```

```
tests/test_auto.py::test_match[1.txt] PASSED                                                                            [100%]
```

import importlib
import shutil
from pathlib import Path

from colorama import Fore


def create_project(name):
    """Set up starter code."""
    assessment_root = Path(name)
    try:
        assessment_root.mkdir(parents=False, exist_ok=False)
    except Exception as e:
        print(e)
        exit(1)

    # set up files under probing_tests/
    probing_tests = assessment_root / 'probing_tests'
    probing_tests.mkdir(parents=False, exist_ok=False)
    (probing_tests / '__init__.py').write_text("")  # empty
    (probing_tests / 'conftest.py').write_text(conftest_content())
    (probing_tests / 'pytest.ini').write_text(pytest_ini_content())
    (probing_tests / 'test_it.py').write_text(test_it_content())

    # set up files under maps/
    maps = assessment_root / 'maps'
    maps.mkdir(parents=False, exist_ok=False)
    (maps / '__init__.py').write_text(maps_init_content())
    (maps / 'general.py').write_text(general_mapping_content())

    # set up files under stu/
    stu = assessment_root / 'stu'
    stu.mkdir(parents=False, exist_ok=False)
    (stu / 'student.txt').write_text(stu_answer_content())

    # set up socassess.toml
    toml_template = importlib.resources.files('socassess') / "socassess.template.toml"  # noqa: E501
    shutil.copy(toml_template, assessment_root / "socassess.toml")

    # done
    starter_messages(name)


def pytest_ini_content():
    """Provide content for pytest.ini file under probing_tests."""
    return """
[pytest]
automark_dependency = True
# always order tests with dependency markers
addopts = --order-dependencies
required_plugins = pytest-timeout pytest-dependency pytest-order
    """.strip()


def conftest_content():
    """Provide content for conftest.py file under probing_tests."""
    return """
from pathlib import Path

import pytest


def pytest_addoption(parser):
    \"\"\"Add necessary pytest configurations.\"\"\"
    parser.addoption(
        "--artifacts", action="store", default="artifacts"
    )
    parser.addoption(
        "--ansdir", action="store", default="stu"
    )


@pytest.fixture(scope="session")
def artifacts(request) -> Path:
    \"\"\"Contains the folder path to store artifacts.\"\"\"
    opt = request.config.getoption("--artifacts")
    return Path(opt)


@pytest.fixture(scope="session")
def stu_answer(request) -> Path:
    \"\"\"Contains the folder path containing student's solution file.\"\"\"
    opt = request.config.getoption("--ansdir")
    return Path(opt) / 'student.txt'


@pytest.fixture(scope="session")
def stu_answer_content(stu_answer) -> Path:
    \"\"\"Read and return the content of the student answer file.\"\"\"
    return stu_answer.read_text()
    """.strip()


def test_it_content():
    """Provide content for test_it.py file under probing_tests/."""
    return """
import shutil

import pytest


def test_exist(stu_answer):
    assert stu_answer.exists()


@pytest.mark.dependency(depends=['test_exist'])
def test_content(stu_answer_content, stu_answer, artifacts):
    \"\"\"Test content only if the solution file exists.\"\"\"
    try:
        assert len(stu_answer_content) > 0
    except AssertionError as e:
        # back up the answer file in case something happens so we can inspect
        # manually later.
        shutil.copy(stu_answer, artifacts)
        raise e
    """.strip()


def maps_init_content():
    """Provide content for __init__.py file under maps/."""
    return """
\"\"\"Contain necessary information for SocAssess to provide feedback..\"\"\"

from . import general

__all__ = [
    # required
    "questions",
    "selected",
]


# ========
# Required
# ========

selected = {
    "general": general.mappings,
}


questions = {
    "general": "this is a general question",
}
    """.strip()


def general_mapping_content():
    """Provide content for general.py file under maps/."""
    return """
mappings = {
    frozenset([
        # Since this is an one-line binary test so we assume the only cause of
        # its failure is the file was not found.
        'test_it::test_exist::failed',
    ]): {
        'feedback': 'Oops! Did you forget to submit the file or did name your file correctly?',  # noqa: E501
    },
    frozenset([
        'test_it::test_content::passed',
    ]): {
        'feedback': 'Nice! Your answer looks good!',
    },
}
    """.strip()


def stu_answer_content():
    """Provide content for student.txt file under stu/."""
    return """
Great! I put something into my answer file.
    """.strip()


def starter_messages(name):
    """Output starter commands."""
    print("Assessment folder is created! Let's give it a try.")
    print(f"    {Fore.GREEN}cd {name}{Fore.RESET}")
    print("To see the automated feedback:")
    print(f"    {Fore.GREEN}socassess feedback --config=socassess.toml --artifacts=artifacts --ansdir=stu --probing=probing_tests --feedback=maps{Fore.RESET}")  # noqa: E501
    print("To inspect pytest outcomes:")
    print(f"    {Fore.GREEN}socassess feedback --artifacts=artifacts --ansdir=stu --probing=probing_tests{Fore.RESET}")  # noqa: E501
    print("Or you can just use `pytest`")
    print(f"    {Fore.GREEN}pytest -vv --artifacts=artifacts --ansdir=stu probing_tests{Fore.RESET}")  # noqa: E501
    print("For more info")
    print(f"    {Fore.GREEN}socassess --help{Fore.RESET}")  # noqa: E501
    print(f"Take a look at the code in {Fore.GREEN}./{name}{Fore.RESET} and have fun!")  # noqa: E501

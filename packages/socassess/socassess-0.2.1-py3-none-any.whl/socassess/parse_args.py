import argparse

from .create import create_project


def parse_args():
    """Parse args."""
    parser = argparse.ArgumentParser(
        description="""

A tool to assist assessment creators to create test-based assessments that can
provide high-quality formative feedback

        """.strip())  # noqa: E501
    subparsers = parser.add_subparsers(dest="command")
    # create_parser
    create_parser = subparsers.add_parser('create', help='Create SocAssess starter code in a new folder')  # noqa: E501
    create_parser.add_argument(
        '--name',
        dest='name',
        action='store',
        required=True,
        help='the folder containing the socassess code')

    # feedback_parser
    feedback_parser = subparsers.add_parser('feedback', help='Generate feedback')  # noqa: E501
    feedback_parser.add_argument(
        '--ansdir',
        dest='ansdir',
        action='store',
        required=True,
        default='stu',
        help='the folder containing the answer')
    feedback_parser.add_argument(
        '--artifacts',
        dest='artifacts',
        action='store',
        required=True,
        default='artifacts',
        help='the folder to save generated artifacts, probing test outcomes will be saved to `report.xml`')  # noqa: E501
    feedback_parser.add_argument(
        '--probing',
        dest='probing',
        action='store',
        help='generate artifacts and assess answers with probing tests stored inside the specified folder')  # noqa: E501
    feedback_parser.add_argument(
        '--feedback',
        dest='feedback',
        action='store',
        help='map the test outcomes into feedback messages using mappings inside the specified folder')  # noqa: E501
    feedback_parser.add_argument(
        '--config',
        dest='config',
        action='store',
        # required=True,
        # default='',  # TODO: add a default one
        help='the path to the `socassess.toml` file')  # noqa: E501

    args = parser.parse_args()
    if args.command == 'create':
        create_project(args.name)
        exit(0)
    if args.command == 'feedback' and args.probing is None and args.feedback is None:  # noqa: E501
        feedback_parser.error("Please use at least one of `--probing` or `--feedback`")  # noqa: E501
        exit(1)

    return args

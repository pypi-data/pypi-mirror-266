import contextlib
import io
import os
import shutil
import sys
from pathlib import Path

import pytest

from . import userargs
from .config import Config
from .exception import SocAssessException
from .feedback import generate_feedback
from .parse_args import parse_args


def main() -> int:
    """Provide CLI entry point.

    Raise SocAssessException for development purpose, such exception should
    never be raised during real assessments. For all other Exception, it will
    be silently catched.

    When there is no exception, the exit code is 0; otherwise it will be 1.

    """
    try:
        args = parse_args()

        ansdir = Path(args.ansdir)
        # Always put artifacts onto disk
        artifacts = Path(args.artifacts)

        if args.probing is not None:
            # recreate artifacts only when --probing is used
            shutil.rmtree(artifacts, ignore_errors=True)
            artifacts.mkdir(parents=False, exist_ok=False)
            with Path(args.probing) as pt:
                report_xml = os.path.join(artifacts, 'report.xml')
                # if only "--with-probing", then we output things to console
                # for inspection
                if not args.feedback:
                    pytest.main([
                        f"--junitxml={report_xml}",
                        "-v",
                        "--tb=line",
                        f"--artifacts={artifacts}",
                        f"--ansdir={ansdir}",  # TODO: pytest bug? if
                                               # whitespace appears in previous
                                               # options, remaining options
                                               # cannot be properly parsed
                        pt
                    ])
                else:
                    with io.StringIO() as buf, \
                            contextlib.redirect_stdout(buf), \
                            contextlib.redirect_stderr(buf):
                        pytest.main([
                            f"--junitxml={report_xml}",
                            f"--artifacts={artifacts}",
                            f"--ansdir={ansdir}",
                            pt
                        ])
                        console_output = buf.getvalue()  # noqa: F841

        # allow user to use artifacts
        userargs.artifacts = artifacts
        if args.feedback is not None:
            assert (artifacts / 'report.xml').is_file(), "cannot find report.xml"  # noqa: E501
            assert args.config is not None and Path(args.config).is_file(), \
                "cannot find feedback configuration, e.g., socassess.toml"  # noqa: E501

            # prepare sys.path so we can import `maps` later
            # args.feedback should be named as `maps`
            maps = Path(args.feedback)
            assert maps.name == "maps", "cannot find valid `maps`"
            maps_parent = maps.parent
            # error if there is no parent path
            assert maps_parent != maps, "`maps` should have a parent path"

            sys.path.append(str(maps_parent))

            config = Config(args.config)
            fb = generate_feedback(
                ansdir,
                artifacts,
                config=config
            )
            # always print feedback to stdout
            print(fb)
    except AssertionError as e:
        raise SocAssessException(e) from e
    except SocAssessException as e:
        raise e
    except Exception as e:  # noqa: F841
        print("Oops, something's wrong. Please contact system administrator.")  # noqa: E501
        # for debugging
        # raise e
        return 1

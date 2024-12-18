"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Entrypoint to validate :py:mod:`logging.config` yaml file(s)

**Module objects**

"""

from __future__ import annotations

import argparse
import io
import sys
import textwrap
from contextlib import redirect_stderr
from pathlib import Path

from strictyaml import YAMLValidationError

from .constants import (
    LoggingConfigCategory,
    g_app_name,
)
from .exceptions import (
    LoggingStrictPackageNameRequired,
    LoggingStrictPackageStartFolderNameRequired,
)
from .logging_api import LoggingConfigYaml
from .logging_yaml_validate import validate_yaml_dirty
from .util.check_type import is_not_ok


def _process_args():
    """parse args

    :returns: cli arguments
    :rtype: tuple[tuple[pathlib.Path, ...], bool]
    """
    desc = "Validate .[worker|app].logging.config.yaml files"
    prog = f"{g_app_name}_validate_yaml"
    epilog = f"""Validation of `*.[app|worker].logging.config.yaml` file(s)
against a strictyaml schema. Resultant data types are as expected by
Python built-in logging.handlers

For custom (handlers, filters, and formatters) functions, there is no
way to know beforehand the parameter name and type, parameter type will
become str

Place these files into a separate folder, so as not to be confused
with other yaml files. Cannot distinguish; just don't mistakenly use
this on other yaml files

EXIT CODES

There is no error messages, only exit codes. `echo $?` command to check
which error occurred.

- 1 -- Purposefully avoided. Folder permissions will trigger

- 2 -- Unwisely used as a catchall by cli parser, argparse, to indicate
    called with the wrong positional or optional parameters.
    Unix convention is to reserve this to mean insufficient permissions.

- 3 -- An argument has wrong type or missing entirely

- 5 -- Extra unknown kwarg. Check the normal usage

- 6 -- Package name is required. Package in which logging.config yaml files reside

- 7 -- Package start folder name is required. Each package differs. {g_app_name}
    is in 'configs' folder. Does not assume within 'data' folder

- 8 -- Process category is required. Choices 'app' or 'worker'

- 9 -- Genre is required. For app, UI framework e.g. 'textual' or 'pyside'.
    For worker, 'mp' or 'rabbitmq'

- 10 -- Not an absolute folder or folder does not containing files matching pattern

"""
    parser = argparse.ArgumentParser(
        prog=prog,
        description=textwrap.dedent(desc),
        epilog=textwrap.dedent(epilog),
        formatter_class=argparse.RawTextHelpFormatter,
        exit_on_error=False,
    )

    help_text = (
        "Folder (absolute path) containing " "*.[app|worker].logging.config.yaml files"
    )
    parser.add_argument(
        "dir",
        type=Path,
        help=help_text,
        default=Path.cwd(),
        nargs="?",
    )

    help_text = (
        "Package name within which logging.config.yaml files reside. "
        f"Preferrably curated within '{g_app_name}'"
    )
    parser.add_argument(
        "-p",
        "--package",
        type=str,
        help=help_text,
        default=g_app_name,
        # nargs="?",
    )

    help_text = (
        "Package base data folder name. Depends on the package. Does "
        f"not assume 'data'. {g_app_name} base data folder name is 'configs'"
    )
    parser.add_argument(
        "-s",
        "--package_data_folder_start",
        type=str,
        help=help_text,
        default="configs",
        # nargs="?",
    )

    help_text = "Narrow down the search. Filter by process purpose"
    parser.add_argument(
        "-c",
        "--category",
        type=str,
        choices=[LoggingConfigCategory.UI.value, LoggingConfigCategory.WORKER.value],
        # nargs="?",
        required=False,
    )

    help_text = (
        "Genre. If UI framework, examples: textual, rich. "
        "For worker, e.g. mp (meaning multiprocessing). Preferrably one "
        "word w/o hyphen periods or underscores"
    )
    parser.add_argument(
        "-g",
        "--genre",
        type=str,
        help=help_text,
        required=False,
    )

    help_text = (
        "Flavor (or name). Specific logging config serving a particular purpose. "
        "Preferrably one word w/o hyphen periods or underscores"
    )
    parser.add_argument(
        "-n",
        "--flavor",
        type=str,
        help=help_text,
        required=False,
    )

    help_text = (
        "logging.config yaml file version. Flavor is optional, so applies "
        "to either: genre only or genre/flavor. Not to be confused with: yaml "
        "spec or logging.config version"
    )
    parser.add_argument(
        "-v",
        "--version",
        type=str,
        help=help_text,
        default=None,  # means get all. Unsupported type --> FALLBACK_VERSION
        required=False,
    )

    help_text = "Stop on first fail or error"
    parser.add_argument(
        "-f",
        "--fail-fast",
        type=bool,
        help=help_text,
        default=True,  # TRUE
        required=False,
    )

    # sys.exit(2) happens automagically if missing required args or unknown kwargs
    try:
        f = io.StringIO()
        with redirect_stderr(f):
            args = parser.parse_args()
    except argparse.ArgumentError:
        sys.exit(3)

    d_args = vars(args)
    keys = d_args.keys()

    t_required = ("dir",)
    t_optional = (
        "package",
        "package_data_folder_start",
        "category",
        "genre",
        "flavor",
        "version",
        "fail_fast",
    )

    # Extra args. There is one optional
    if len(keys) > len(t_required) + len(t_optional):
        sys.exit(5)
    else:  # pragma: no cover
        pass

    # files_ = d_args["file_"]
    # file_count = len(files_)
    path_dir = d_args["dir"]  # start path

    if "package" not in keys:
        str_package = None
    else:
        str_package = d_args["package"]

    if "package_data_folder_start" not in keys:
        start_dir = None
    else:
        start_dir = d_args["package_data_folder_start"]

    # LoggingConfigCategory.UI.value
    if "category" not in keys:
        str_category = None
    else:
        tmp_cat = d_args["category"]
        if is_not_ok(tmp_cat):
            str_category = None
        else:
            if tmp_cat not in LoggingConfigCategory.categories():
                str_category = None
            else:
                str_category = tmp_cat

    if "genre" not in keys:
        str_genre = None
    else:
        str_genre = d_args["genre"]

    if "flavor" not in keys:
        str_flavor = None
    else:
        str_flavor = d_args["flavor"]

    # Default is all, not FALLBACK_VERSION. For that provide unsupported type
    if "version" not in keys:
        mixed_version = None
    else:
        mixed_version = d_args["version"]

    if "fail_fast" not in keys:
        is_fail_fast = True
    else:
        is_fail_fast = d_args["fail_fast"]

    abspath_files = []
    file_count = 0
    try:
        api = LoggingConfigYaml(
            str_package,
            start_dir,
            str_category,
            genre=str_genre,
            flavor=str_flavor,
            version_no=mixed_version,
        )
    except LoggingStrictPackageNameRequired:
        sys.exit(6)
    except LoggingStrictPackageStartFolderNameRequired:
        sys.exit(7)

    for path_yaml in api.iter_yamls(path_dir):
        abspath_files.append(path_yaml)
        file_count = file_count + 1
    if file_count == 0:
        sys.exit(10)
    else:  # pragma: no cover
        pass

    return tuple(abspath_files), is_fail_fast


def main() -> None:
    """Validate yaml files, provide useful readable feedback"""
    paths_file, is_fail_fast = _process_args()
    count_total = len(paths_file)
    count_succeed = 0
    count_fail = 0
    current_idx = 0
    file_last = None
    errors = []
    for idx, path_file in enumerate(paths_file):
        current_idx = idx
        file_last = str(path_file)

        # Check file is simple ``ASCII text``
        # file --brief str(path_file)
        pass

        yaml_snippet = path_file.read_text()

        try:
            validate_yaml_dirty(yaml_snippet)
        except YAMLValidationError as exc:
            count_fail = count_fail + 1
            exc_text = exc.context
            problem = exc.problem
            string_mark_problem_mark = exc.problem_mark
            str_problem_mark = str(string_mark_problem_mark)
            t_err = (
                f"file: {file_last}",
                exc_text,
                problem,
                str_problem_mark,
            )
            errors.append("\n".join(list(t_err)))
        else:
            count_succeed = count_succeed + 1
        if is_fail_fast and len(errors) != 0:
            break
        else:  # pragma: no cover continue
            pass

    # Write the report
    count_processed = count_succeed + count_fail
    report = (
        f"Processed: {count_processed} / {count_total}\n"
        f"Success / fail: {count_succeed} / {count_fail}\n"
        f"last ({str(current_idx)}): {file_last}"
    )
    str_err = "\n".join(errors)
    print(f"{report}\n{str_err}", file=sys.stderr)


if __name__ == "__main__":  # pragma: no cover
    main()

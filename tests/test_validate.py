"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

strictyaml lacks proper unittests.

Only one person on the planet gets away with that and that person is
strictyaml author /nosarc

The author has tests as-documentation. Which is brilliant!

But this doesn't excuse the lack of old-school unittests. Also the
as-documentation tests are too simplistic. Kept thinking, yeah **BUT**
that is ``not a realistic example``.

Without old school unittests and the as-documentation being found wanting,
have to confirm strictyaml does what it advertising it does.

That's what real unittests are for.

"""

import unittest
from collections.abc import Sequence
from typing import (
    TYPE_CHECKING,
    cast,
)

import strictyaml as s
from strictyaml.exceptions import YAMLValidationError

from logging_strict.logging_yaml_validate import (
    filters_map,
    format_style,
    handlers_map,
    loggers_map,
    root_map,
    validate_yaml_dirty,
)

if TYPE_CHECKING:
    from typing import Any


class YamlValidate(unittest.TestCase):
    """Monkey/Chaos testing helps to improve the schema.

    Find out where/why it breaks.
    """

    def test_version_required(self) -> None:
        """version is the only required field"""
        if TYPE_CHECKING:
            actual_0: s.YAML
            actual_1: s.YAML

        # Provide version
        yaml_snippet = "version: 1\n"
        schema = s.MapCombined(
            {
                "version": s.Enum([1], item_validator=s.Int()),
                s.Optional("foo"): s.Str(),
            },
            s.Str(),
            s.Any(),
        )
        actual_0 = s.load(
            yaml_snippet,
            schema=schema,
        )
        d_actual_0 = cast("dict[Any, Any]", actual_0.data)
        self.assertIn(
            d_actual_0["version"],
            s.Enum([1])._restricted_to,
        )

        # Required key/value pair is ``version: 1`` Enum expects version to be 1 or freaks! No way to know expecting version
        yaml_snippet = "b: 3\n"

        with self.assertRaises(s.YAMLValidationError) as cm:
            s.load(
                yaml_snippet,
                schema=schema,
            )
        exc = cm.exception
        self.assertEqual(
            exc.context,
            "while parsing a mapping",
        )
        self.assertEqual(
            exc.problem,
            "required key(s) 'version' not found",
        )
        context_mark = "b: '3'\n"
        context_mark_actual = exc.context_mark.buffer
        self.assertEqual(context_mark_actual, context_mark)
        problem_mark = (
            """  in "<unicode string>", line 1, column 1:\n"""
            "    b: '3'\n"
            "     ^ (line: 1)"  # no trailing newline
        )
        problem_mark_actual = exc.problem_mark
        problem_mark_actual_str = str(problem_mark_actual)
        self.assertEqual(problem_mark_actual_str, problem_mark)

        # With version: 1
        yaml_snippet = "version: 1\n" "b: '3'\n"
        actual_1 = s.load(
            yaml_snippet,
            schema=schema,
        )
        d_actual_1 = cast("dict[Any, Any]", actual_1.data)
        self.assertIn(
            d_actual_1["version"],
            s.Enum([1])._restricted_to,
        )
        self.assertIsInstance(d_actual_1["b"], str)
        self.assertEqual(d_actual_1["b"], "3")

    def test_two_scalar_optionals(self) -> None:
        """Tests for scalars: incremental and disable_existing_loggers"""
        schema = s.MapCombined(
            {
                "version": s.Enum(
                    [1],
                    item_validator=s.Int(),
                ),
                s.Optional(
                    "incremental",
                    default=False,
                    drop_if_none=True,
                ): s.EmptyNone()
                | s.Bool(),
                s.Optional(
                    "disable_existing_loggers",
                    default=True,
                    drop_if_none=True,
                ): s.EmptyNone()
                | s.Bool(),
            },
            s.Str(),
            s.Any(),
        )
        yaml_bools = (  # explicits
            ("'False'", False),  # str
            ("'false'", False),  # str
            ("'FALSE'", False),  # str
            ("'off'", False),  # str
            ("n", False),  # str
            ("no", False),  # str
            ("false", False),  # not str
            ("False", False),  # not str
            ("FALSE", False),  # not str
            (0, False),  # not str, int
            ("'True'", True),  # str
            ("'true'", True),  # str
            ("'TRUE'", True),  # str
            ("'on'", True),  # str
            ("y", True),  # str
            ("yes", True),  # str
            ("true", True),  # not str
            ("True", True),  # not str
            ("TRUE", True),  # not str
            (1, True),  # not str, int
        )
        for yaml_bool, expected in yaml_bools:
            yaml_snippet = (
                "version: 1\n"
                f"incremental: {yaml_bool}\n"
                f"disable_existing_loggers: {yaml_bool}\n"
            )
            actual_0 = s.load(
                yaml_snippet,
                schema=schema,
            )
            d_actual_0 = cast("dict[Any, Any]", actual_0.data)
            self.assertIsInstance(d_actual_0["incremental"], bool)
            self.assertEqual(d_actual_0["incremental"], expected)
            self.assertIsInstance(d_actual_0["disable_existing_loggers"], bool)
            self.assertEqual(d_actual_0["disable_existing_loggers"], expected)

        # defaults
        yaml_snippet = "version: 1\n"
        actual_1 = s.load(
            yaml_snippet,
            schema=schema,
        )
        d_actual_1 = cast("dict[Any, Any]", actual_1.data)
        self.assertIsInstance(d_actual_1["incremental"], bool)
        self.assertFalse(d_actual_1["incremental"])
        self.assertIsInstance(d_actual_1["disable_existing_loggers"], bool)
        self.assertTrue(d_actual_1["disable_existing_loggers"])

        # What about if there is a None? So it become the default?
        yaml_snippet = "version: 1\nincremental: \ndisable_existing_loggers: \n"
        actual_2 = s.load(
            yaml_snippet,
            schema=schema,
        )
        d_actual_2 = cast("dict[Any, Any]", actual_2.data)
        self.assertIsNone(d_actual_2["incremental"])
        self.assertIsNone(d_actual_2["disable_existing_loggers"])

        # What about if there is a random junk?
        yaml_snippet = (
            "version: 1\n"
            "incremental: 'dsafasdf'\n"
            "disable_existing_loggers: 'dsafasdf'\n"
        )
        with self.assertRaises(s.YAMLValidationError) as cm:
            s.load(
                yaml_snippet,
                schema=schema,
            )
        exc = cm.exception
        exc_text = (
            "when expecting a boolean value (one "
            """of "yes", "true", "on", "1", "y", "no", "false", "off", "0", "n")"""
        )
        self.assertEqual(
            exc.context,
            exc_text,
        )
        self.assertEqual(
            exc.problem,
            "found arbitrary text",
        )
        # context_mark_actual = exc.context_mark.buffer
        # self.assertEqual(context_mark_actual, yaml_snippet)
        problem_mark = (
            """  in "<unicode string>", line 2, column 1:\n"""
            "    incremental: dsafasdf\n"
            "    ^ (line: 2)"  # no trailing newline
        )
        problem_mark_actual = exc.problem_mark
        problem_mark_actual_str = str(problem_mark_actual)
        self.assertEqual(problem_mark_actual_str, problem_mark)

    def test_filters_optional(self) -> None:
        """filters section

        An example filter
        `[docs] <https://docs.python.org/3/howto/logging-cookbook.html#imparting-contextual-information-in-handlers>`_

        Adds ``user = "jim"`` to every log entry

        .. code-block:: text

           import logging
           import copy
           def filter(record: logging.LogRecord):
               record = copy.copy(record)
               record.user = 'jim'
               return record

        .. seealso::

           Examples

           https://docs.python.org/3/howto/logging-cookbook.html#custom-handling-of-levels

           https://docs.python.org/3/howto/logging-cookbook.html#using-filters-to-impart-contextual-information

           https://docs.python.org/3/howto/logging-cookbook.html#an-example-dictionary-based-configuration

        """
        yaml_snippet = (
            "warnings_and_below:\n"
            "  '()': __main__.filter_maker\n"
            "  level: WARNING\n"
            "  filter_arg0: 'bob'\n"
        )
        schema = s.MapPattern(s.Str(), filters_map)
        actual = validate_yaml_dirty(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsNotNone(actual)
        if actual is not None:
            d_actual = cast("dict[Any, Any]", actual.data)

            self.assertIsInstance(d_actual["warnings_and_below"]["()"], str)
            self.assertEqual(
                d_actual["warnings_and_below"]["()"], "__main__.filter_maker"
            )
            self.assertIsInstance(d_actual["warnings_and_below"]["level"], str)
            self.assertEqual(d_actual["warnings_and_below"]["level"], "WARNING")
            """filter args will always be str, the default of strictyaml.
            All args should be countervariant; accept Any and do proper
            argument processing"""
            self.assertIsInstance(d_actual["warnings_and_below"]["filter_arg0"], str)
            self.assertEqual(d_actual["warnings_and_below"]["filter_arg0"], "bob")

    def test_formatters_optional(self) -> None:
        """formatters section

        Ignore defaults field introduced in py312. Requires a separate test

        https://docs.python.org/3/library/logging.config.html#object-connections"""
        formatter_map = s.MapCombined(  # map validator
            {
                s.Optional("format"): s.Str(),
                s.Optional("datefmt"): s.Str(),
                s.Optional("style", default="%"): format_style,
                s.Optional("validate", default=True): s.Bool(),  # py38
                s.Optional("class"): s.Str(),
            },
            s.Str(),  # key validator Slug() removed
            s.OrValidator(
                s.OrValidator(s.Bool(), s.Str()),
                format_style,
            ),
        )
        schema = s.MapCombined(
            {
                s.Optional("formatters"): s.MapPattern(s.Str(), formatter_map),
                s.Optional("incremental", default=False): s.Bool(),
                s.Optional("disable_existing_loggers", default=True): s.Bool(),
            },
            s.Str(),
            s.Any(),
        )
        format_brief = (
            "'%(levelname)s %(module)s %(funcName)s: %(lineno)d: %(message)s'"
        )
        format_precise = (
            "'%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'"
        )
        yaml_snippet = (
            "formatters:\n"
            "  brief:\n"
            "    class: logging.Formatter\n"
            f"    format: {format_brief}\n"
            "  precise:\n"
            "    class: logging.Formatter\n"
            f"    format: {format_precise}\n"
            "ted: '3'\n"
        )
        actual = s.load(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsNotNone(actual)
        d_actual = cast("dict[Any, Any]", actual.data)
        self.assertIn("brief", d_actual["formatters"].keys())
        self.assertIn("precise", d_actual["formatters"].keys())
        d_brief = d_actual["formatters"]["brief"]
        d_precise = d_actual["formatters"]["precise"]
        self.assertIsInstance(d_brief, dict)
        self.assertIsInstance(d_precise, dict)
        self.assertEqual(d_brief["class"], "logging.Formatter")
        self.assertEqual(d_precise["class"], "logging.Formatter")
        self.assertEqual(d_brief["format"], format_brief.strip("'"))
        self.assertEqual(d_precise["format"], format_precise.strip("'"))

        str_ted = d_actual["ted"]
        self.assertIsInstance(str_ted, str)
        self.assertEqual(str_ted, "3")

    def test_handlers_optional(self) -> None:
        """yaml flow style with unknown keys

        yaml with flow style

        .. code-block:: text

           filters: [allow_foo]

        Corrected yaml, without flow style

        .. code-block:: text

           filters:
             - allow_foo

        The issue is the logging.config docs uses the former. And
        world+dog follow the docs. So stuck supporting yaml w/ flow style
        """
        if TYPE_CHECKING:
            yaml_actual: s.YAML | None

        yaml_snippet = (
            "console:\n"
            "  class: logging.StreamHandler\n"
            "  formatter: brief\n"
            "  level: INFO\n"
            "  filters: [allow_foo]\n"
            "  stream: ext://sys.stdout\n"
            "file:\n"
            "  class: logging.handlers.RotatingFileHandler\n"
            "  formatter: precise\n"
            "  filename: logconfig.log\n"
            "  maxBytes: 1024\n"
            "  backupCount: 3\n"
        )
        schema = s.MapPattern(s.Str(), handlers_map)

        yaml_actual = validate_yaml_dirty(yaml_snippet, schema=schema)
        self.assertIsNotNone(yaml_actual)
        if yaml_actual is not None:
            # mypy understands the underlying dict, not a YAML wrapper object
            d_yaml_actual = cast("dict[Any, Any]", yaml_actual.data)

            # yaml_handler_0 = yaml_actual["console"]
            d_yaml_handler_0 = cast("dict[Any, Any]", d_yaml_actual["console"])
            self.assertEqual(d_yaml_handler_0["class"], "logging.StreamHandler")
            self.assertEqual(d_yaml_handler_0["formatter"], "brief")
            self.assertEqual(d_yaml_handler_0["level"], "INFO")
            str_val = d_yaml_handler_0["stream"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "ext://sys.stdout")

            self.assertEqual(len(d_yaml_handler_0["filters"]), 1)
            str_val = d_yaml_handler_0["filters"][0]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "allow_foo")

            # yaml_handler_1 = cast("dict[Any, Any]", yaml_actual["file"].data)
            d_yaml_handler_1 = cast("dict[Any, Any]", d_yaml_actual["file"])
            self.assertEqual(
                d_yaml_handler_1["class"], "logging.handlers.RotatingFileHandler"
            )
            self.assertEqual(d_yaml_handler_1["formatter"], "precise")

            str_val = d_yaml_handler_1["filename"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "logconfig.log")

            int_val = d_yaml_handler_1["maxBytes"]
            self.assertIsInstance(int_val, int)
            self.assertEqual(int_val, 1024)

            int_val = d_yaml_handler_1["backupCount"]
            self.assertIsInstance(int_val, int)
            self.assertEqual(int_val, 3)

    def test_loggers_optional(self) -> None:
        """loggers section"""
        # Demonstrate empty list will load
        schema_0 = s.Map({"a": s.Seq(s.Str())})
        yaml_snippet = """a: []\n"""
        actual_0 = validate_yaml_dirty(yaml_snippet, schema=schema_0)
        self.assertIsNotNone(actual_0)
        if actual_0 is not None:
            # YAML wrapper object data evaluated at runtime
            d_actual_0 = cast("dict[Any, Any]", actual_0.data)
            # val = actual_0["a"].data
            val = d_actual_0["a"]
            self.assertIsInstance(val, list)
            self.assertEqual(len(val), 0)

        # https://docs.python.org/3/howto/logging-cookbook.html#an-example-dictionary-based-configuration
        schema_1 = s.MapPattern(s.Str(), loggers_map)
        yaml_snippet = (
            "django:\n"
            "  handlers:\n"
            "    - console\n"
            "  propagate: 'yes'\n"
            "django.request:\n"
            "  handlers:\n"
            "    - mail_admins\n"
            "  level: ERROR\n"
            "  propagate: false\n"
            "myproject.custom:\n"
            "  handlers:\n"
            "    - console\n"
            "    - mail_admins\n"
            "  level: INFO\n"
            "  filters:\n"
            "    - special\n"
        )
        actual_1 = validate_yaml_dirty(yaml_snippet, schema=schema_1)
        self.assertIsNotNone(actual_1)
        if actual_1 is not None:
            d_actual_1 = cast("dict[Any, Any]", actual_1.data)
            self.assertEqual(
                tuple(d_actual_1.keys()),
                ("django", "django.request", "myproject.custom"),
            )

            # d_django = actual["django"]
            d_django = d_actual_1["django"]
            str_handler_0 = d_django["handlers"][0]
            self.assertIsInstance(str_handler_0, str)
            self.assertEqual(str_handler_0, "console")
            self.assertIsInstance(d_django["propagate"], bool)
            self.assertTrue(d_django["propagate"])

            d_django_request = d_actual_1["django.request"]
            str_handler_1 = d_django_request["handlers"][0]
            self.assertIsInstance(str_handler_1, str)
            self.assertEqual(str_handler_1, "mail_admins")
            self.assertIsInstance(d_django_request["level"], str)
            self.assertEqual(d_django_request["level"], "ERROR")
            self.assertIsInstance(d_django_request["propagate"], bool)
            self.assertFalse(d_django_request["propagate"])

            d_myproject_custom = d_actual_1["myproject.custom"]
            handlers_count = len(d_myproject_custom["handlers"])
            self.assertEqual(handlers_count, 2)

            str_handler_0 = d_myproject_custom["handlers"][0]
            self.assertIsInstance(str_handler_0, str)
            self.assertEqual(str_handler_0, "console")

            str_handler_1 = d_myproject_custom["handlers"][1]
            self.assertIsInstance(str_handler_1, str)
            self.assertEqual(str_handler_1, "mail_admins")

            self.assertIsInstance(d_myproject_custom["level"], str)
            self.assertEqual(d_myproject_custom["level"], "INFO")
            str_filter_1 = d_myproject_custom["filters"][0]
            self.assertIsInstance(str_filter_1, str)
            self.assertEqual(str_filter_1, "special")

    def test_root_optional(self) -> None:
        """root section does not allow propagate"""
        if TYPE_CHECKING:
            yaml_snippets: list[str]
            snippet: str

        schema = root_map

        yaml_snippets = []
        yaml_snippet = (  # flow style
            "level: WARNING\n" "filters: [bob_will_know]\n" "handlers: ['console']\n"
        )
        yaml_snippets.append(yaml_snippet)

        yaml_snippet = (  # w/o flow style
            "level: WARNING\n"
            "filters:\n"
            "  - bob_will_know\n"
            "handlers:\n"
            "  - 'console'\n"
        )
        yaml_snippets.append(yaml_snippet)

        for snippet in yaml_snippets:
            actual = validate_yaml_dirty(
                snippet,
                schema=schema,
            )
            self.assertIsNotNone(actual)
            if actual is not None:
                d_actual = cast("dict[Any, Any]", actual.data)
                self.assertIsInstance(d_actual["level"], str)
                self.assertEqual(d_actual["level"], "WARNING")
                self.assertIsInstance(d_actual["filters"], Sequence)
                self.assertIsInstance(d_actual["filters"][0], str)
                self.assertEqual(d_actual["filters"][0], "bob_will_know")
                self.assertIsInstance(d_actual["handlers"][0], str)
                self.assertEqual(d_actual["handlers"][0], "console")

        # propagate not allowed; common mistake
        yaml_snippet = (  # w/o flow style
            "propagate: off\n"
            "level: WARNING\n"
            "filters:\n"
            "  - bob_will_know\n"
            "handlers:\n"
            "  - 'console'\n"
        )

        with self.assertRaises(YAMLValidationError) as cm:
            validate_yaml_dirty(
                yaml_snippet,
                schema=schema,
            )
        exc = cm.exception
        exc_text = "while parsing a mapping"
        exc_text_actual = exc.context
        self.assertEqual(exc_text_actual, exc_text)
        problem_actual = exc.problem
        self.assertEqual(problem_actual, "unexpected key not in schema 'propagate'")

        # similar but not exactly equal to yaml_snippet
        # context_mark_actual = exc.context_mark.buffer
        pass

        problem_mark = (
            """  in "<unicode string>", line 1, column 1:\n"""
            "    propagate: off\n"
            "     ^ (line: 1)"  # no trailing newline
        )
        problem_mark_actual = exc.problem_mark
        problem_mark_actual_str = str(problem_mark_actual)
        self.assertEqual(problem_mark_actual_str, problem_mark)

    def test_handler_args_kwargs(self) -> None:
        """logging.handlers args/kwargs typing are known. Enforce type"""
        # https://docs.python.org/3/library/logging.config.html#dictionary-schema-details
        # Demonstrate stream, filename, maxBytes, backupCount are the right type
        yaml_snippet = (
            "console:\n"
            "  class: logging.StreamHandler\n"
            "  formatter: brief\n"
            "  level: INFO\n"
            "  filters: [allow_foo]\n"
            "  stream: ext://sys.stdout\n"
            "file:\n"
            "  class: logging.handlers.RotatingFileHandler\n"
            "  formatter: precise\n"
            "  filename: logconfig.log\n"
            "  maxBytes: 1024\n"
            "  backupCount: 3\n"
        )
        schema_0 = s.MapPattern(s.Str(), handlers_map)
        actual_0 = validate_yaml_dirty(
            yaml_snippet,
            schema=schema_0,
        )
        self.assertIsNotNone(actual_0)
        if actual_0 is not None:
            self.assertIsInstance(actual_0, s.YAML)
            d_actual_0 = cast("dict[Any, Any]", actual_0.data)
            d_console_0 = d_actual_0["console"]
            optstr_val = d_console_0["stream"]
            if optstr_val is None:
                self.assertIsNone(optstr_val)
            else:
                self.assertIsInstance(optstr_val, str)

            d_file_0 = d_actual_0["file"]
            str_val = d_file_0["filename"]
            self.assertIsInstance(str_val, str)

            int_val = d_file_0["maxBytes"]
            self.assertIsInstance(int_val, int)

            int_val = d_file_0["backupCount"]
            self.assertIsInstance(int_val, int)

        # Other data types. Example from
        # `[docs] <https://docs.python.org/3/library/logging.config.html#configuring-queuehandler-and-queuelistener>`_
        yaml_snippet = (
            "console:\n"
            "  class: logging.SMTPHandler\n"
            "  mailhost: localhost\n"
            "  fromaddr: my_app@domain.tld\n"
            "  toaddrs:\n"
            "    - support_team@domain.tld\n"
            "    - dev_team@domain.tld\n"
            "  subject: Houston, we have a problem.\n"
            "qhand:\n"
            "  class: logging.handlers.QueueHandler\n"
            "  queue: my.module.queue_factory\n"
            "  listener: my.package.CustomListener\n"
            "  handlers:\n"
            "  - hand_name_1\n"
            "  - hand_name_2\n"
            "  respect_handler_level: True\n"
        )
        actual_1 = validate_yaml_dirty(
            yaml_snippet,
            schema=schema_0,
        )
        self.assertIsNotNone(actual_1)
        if actual_1 is not None:
            self.assertIsInstance(actual_1, s.YAML)
            d_actual_1 = cast("dict[Any, Any]", actual_1.data)
            d_console_1 = d_actual_1["console"]

            str_val = d_console_1["class"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "logging.SMTPHandler")

            str_val = d_console_1["mailhost"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "localhost")

            str_val = d_console_1["fromaddr"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "my_app@domain.tld")

            seq_str_val = d_console_1["toaddrs"]
            self.assertIsInstance(seq_str_val, Sequence)
            self.assertEqual(len(seq_str_val), 2)
            str_val = d_console_1["toaddrs"][0]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "support_team@domain.tld")
            str_val = d_console_1["toaddrs"][1]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "dev_team@domain.tld")

            str_val = d_console_1["subject"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "Houston, we have a problem.")

            d_qhand_1 = d_actual_1["qhand"]

            str_val = d_qhand_1["class"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "logging.handlers.QueueHandler")

            str_val = d_qhand_1["queue"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "my.module.queue_factory")

            str_val = d_qhand_1["listener"]
            self.assertIsInstance(str_val, str)
            self.assertEqual(str_val, "my.package.CustomListener")

            seq_str_val = d_qhand_1["handlers"]
            self.assertIsInstance(seq_str_val, Sequence)
            self.assertEqual(len(seq_str_val), 2)

            bool_val = d_qhand_1["respect_handler_level"]
            self.assertIsInstance(bool_val, bool)
            self.assertTrue(bool_val)


if __name__ == "__main__":  # pragma: no cover
    """Without coverage

    .. code-block:: shell

       python -m tests.test_validate

       python -m unittest tests.test_validate \
       -k YamlValidate.test_version_required --locals

       python -m unittest tests.test_validate \
       -k YamlValidate.test_two_scalar_optionals --locals

       python -m unittest tests.test_validate \
       -k YamlValidate.test_formatters_optional --locals

       python -m unittest tests.test_validate \
       -k YamlValidate.test_loggers_optional --locals

       python -m unittest tests.test_validate \
       -k YamlValidate.test_handlers_optional --locals

       python -m unittest tests.test_validate \
       -k YamlValidate.test_handler_args_kwargs --locals


    With coverage
    .. code-block:: shell

       coverage run --data-file=".coverage-combine-43" \
       -m unittest discover -t. -s tests \
       -p "test_validate*.py" --locals

       coverage report --include="**/logging_yaml_validate*" \
       --no-skip-covered --data-file=".coverage-combine-43"

    """
    unittest.main(tb_locals=True)

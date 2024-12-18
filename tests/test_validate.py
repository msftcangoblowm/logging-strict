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

import sys
import unittest

import strictyaml as s

from logging_strict.logging_yaml_validate import (
    filters_map,
    format_style,
    handlers_map,
    loggers_map,
    root_map,
    validate_yaml_dirty,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence  # noqa: F401 used by sphinx
else:  # pragma: no cover
    from typing import Sequence  # noqa: F401 used by sphinx


class YamlValidate(unittest.TestCase):
    """Monkey/Chaos testing helps to improve the schema.

    Find out where/why it breaks.
    """

    def test_version_required(self):
        """version is the only required field"""
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
        actual = s.load(
            yaml_snippet,
            schema=schema,
        )
        self.assertIn(actual.data["version"], s.Enum([1])._restricted_to)

        # Required key/value pair is ``version: 1`` Enum expects version to be 1 or freaks! No way to know expecting version
        yaml_snippet = "b: 3\n"

        with self.assertRaises(s.YAMLValidationError) as cm:
            s.load(
                yaml_snippet,
                schema=schema,
            )
        exc = cm.exception
        self.assertEqual(exc.context, "while parsing a mapping")
        self.assertEqual(exc.problem, "required key(s) 'version' not found")
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
        actual = s.load(
            yaml_snippet,
            schema=schema,
        )
        self.assertIn(actual.data["version"], s.Enum([1])._restricted_to)
        self.assertIsInstance(actual.data["b"], str)
        self.assertEqual(actual.data["b"], "3")

    def test_two_scalar_optionals(self):
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
            actual = s.load(
                yaml_snippet,
                schema=schema,
            )
            self.assertIsInstance(actual["incremental"].data, bool)
            self.assertEqual(actual["incremental"].data, expected)
            self.assertIsInstance(actual["disable_existing_loggers"].data, bool)
            self.assertEqual(actual["disable_existing_loggers"].data, expected)

        # defaults
        yaml_snippet = "version: 1\n"
        actual = s.load(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsInstance(actual["incremental"].data, bool)
        self.assertFalse(actual["incremental"].data)
        self.assertIsInstance(actual["disable_existing_loggers"].data, bool)
        self.assertTrue(actual["disable_existing_loggers"].data)

        # What about if there is a None? So it become the default?
        yaml_snippet = "version: 1\nincremental: \ndisable_existing_loggers: \n"
        actual = s.load(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsNone(actual["incremental"].data)
        self.assertIsNone(actual["disable_existing_loggers"].data)

        # What about if there is a random junk?
        yaml_snippet = (
            "version: 1\n"
            "incremental: 'dsafasdf'\n"
            "disable_existing_loggers: 'dsafasdf'\n"
        )
        with self.assertRaises(Exception) as cm:
            s.load(
                yaml_snippet,
                schema=schema,
            )
        exc = cm.exception
        exc_text = (
            "when expecting a boolean value (one "
            """of "yes", "true", "on", "1", "y", "no", "false", "off", "0", "n")"""
        )
        self.assertEqual(exc.context, exc_text)
        self.assertEqual(exc.problem, "found arbitrary text")
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

    def test_filters_optional(self):
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

        self.assertIsInstance(actual["warnings_and_below"]["()"].data, str)
        self.assertEqual(
            actual["warnings_and_below"]["()"].data, "__main__.filter_maker"
        )
        self.assertIsInstance(actual["warnings_and_below"]["level"].data, str)
        self.assertEqual(actual["warnings_and_below"]["level"].data, "WARNING")
        """filter args will always be str, the default of strictyaml.
        All args should be countervariant; accept Any and do proper
        argument processing"""
        self.assertIsInstance(actual["warnings_and_below"]["filter_arg0"].data, str)
        self.assertEqual(actual["warnings_and_below"]["filter_arg0"].data, "bob")

    def test_formatters_optional(self):
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
        self.assertIn("brief", actual.data["formatters"].keys())
        self.assertIn("precise", actual.data["formatters"].keys())
        d_brief = actual.data["formatters"]["brief"]
        d_precise = actual.data["formatters"]["precise"]
        self.assertIsInstance(d_brief, dict)
        self.assertIsInstance(d_precise, dict)
        self.assertEqual(d_brief["class"], "logging.Formatter")
        self.assertEqual(d_precise["class"], "logging.Formatter")
        self.assertEqual(d_brief["format"], format_brief.strip("'"))
        self.assertEqual(d_precise["format"], format_precise.strip("'"))

        str_ted = actual.data["ted"]
        self.assertIsInstance(str_ted, str)
        self.assertEqual(str_ted, "3")

    def test_handlers_optional(self):
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
        yaml_handler = yaml_actual["console"]
        self.assertEqual(yaml_handler["class"].data, "logging.StreamHandler")
        self.assertEqual(yaml_handler["formatter"].data, "brief")
        self.assertEqual(yaml_handler["level"].data, "INFO")
        str_val = yaml_handler["stream"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "ext://sys.stdout")

        self.assertEqual(len(yaml_handler["filters"].data), 1)
        str_val = yaml_handler["filters"][0].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "allow_foo")

        yaml_handler = yaml_actual["file"]
        self.assertEqual(
            yaml_handler["class"].data, "logging.handlers.RotatingFileHandler"
        )
        self.assertEqual(yaml_handler["formatter"].data, "precise")

        str_val = yaml_handler["filename"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "logconfig.log")

        int_val = yaml_handler["maxBytes"].data
        self.assertIsInstance(int_val, int)
        self.assertEqual(int_val, 1024)

        int_val = yaml_handler["backupCount"].data
        self.assertIsInstance(int_val, int)
        self.assertEqual(int_val, 3)

    def test_loggers_optional(self):
        """loggers section"""
        # Demonstrate empty list will load
        schema = s.Map({"a": s.Seq(s.Str())})
        yaml_snippet = """a: []\n"""
        actual = validate_yaml_dirty(yaml_snippet, schema=schema)
        val = actual["a"].data
        self.assertIsInstance(val, list)
        self.assertEqual(len(val), 0)

        # https://docs.python.org/3/howto/logging-cookbook.html#an-example-dictionary-based-configuration
        schema = s.MapPattern(s.Str(), loggers_map)
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
        actual = validate_yaml_dirty(yaml_snippet, schema=schema)
        self.assertEqual(
            tuple(actual.data.keys()),
            ("django", "django.request", "myproject.custom"),
        )

        d_django = actual["django"]
        yaml_handler0 = d_django["handlers"][0]
        self.assertIsInstance(yaml_handler0.data, str)
        self.assertEqual(yaml_handler0.data, "console")
        self.assertIsInstance(d_django["propagate"].data, bool)
        self.assertTrue(d_django["propagate"].data)

        d_django_request = actual["django.request"]
        yaml_handler0 = d_django_request["handlers"][0]
        self.assertIsInstance(yaml_handler0.data, str)
        self.assertEqual(yaml_handler0.data, "mail_admins")
        self.assertIsInstance(d_django_request["level"].data, str)
        self.assertEqual(d_django_request["level"].data, "ERROR")
        self.assertIsInstance(d_django_request["propagate"].data, bool)
        self.assertFalse(d_django_request["propagate"].data)

        d_myproject_custom = actual["myproject.custom"]
        handlers_count = len(d_myproject_custom["handlers"].data)
        self.assertEqual(handlers_count, 2)

        yaml_handler0 = d_myproject_custom["handlers"][0]
        self.assertIsInstance(yaml_handler0.data, str)
        self.assertEqual(yaml_handler0.data, "console")

        yaml_handler1 = d_myproject_custom["handlers"][1]
        self.assertIsInstance(yaml_handler1.data, str)
        self.assertEqual(yaml_handler1.data, "mail_admins")

        self.assertIsInstance(d_myproject_custom["level"].data, str)
        self.assertEqual(d_myproject_custom["level"].data, "INFO")
        yaml_filter0 = d_myproject_custom["filters"][0]
        self.assertIsInstance(yaml_filter0.data, str)
        self.assertEqual(yaml_filter0.data, "special")

    def test_root_optional(self):
        """root section does not allow propagate"""
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
            self.assertIsInstance(actual["level"].data, str)
            self.assertEqual(actual["level"].data, "WARNING")
            self.assertIsInstance(actual["filters"].data, Sequence)
            self.assertIsInstance(actual["filters"][0].data, str)
            self.assertEqual(actual["filters"][0].data, "bob_will_know")
            self.assertIsInstance(actual["handlers"][0].data, str)
            self.assertEqual(actual["handlers"][0].data, "console")

        # propagate not allowed; common mistake
        yaml_snippet = (  # w/o flow style
            "propagate: off\n"
            "level: WARNING\n"
            "filters:\n"
            "  - bob_will_know\n"
            "handlers:\n"
            "  - 'console'\n"
        )

        with self.assertRaises(Exception) as cm:
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

    def test_handler_args_kwargs(self):
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
        schema = s.MapPattern(s.Str(), handlers_map)
        actual = validate_yaml_dirty(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsInstance(actual, s.YAML)
        yaml_console = actual["console"]

        optstr_val = yaml_console["stream"].data
        if optstr_val is None:
            self.assertIsNone(optstr_val)
        else:
            self.assertIsInstance(optstr_val, str)

        yaml_file = actual["file"]
        str_val = yaml_file["filename"].data
        self.assertIsInstance(str_val, str)

        int_val = yaml_file["maxBytes"].data
        self.assertIsInstance(int_val, int)

        int_val = yaml_file["backupCount"].data
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
        actual = validate_yaml_dirty(
            yaml_snippet,
            schema=schema,
        )
        self.assertIsInstance(actual, s.YAML)
        yaml_console = actual["console"]

        str_val = yaml_console["class"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "logging.SMTPHandler")

        str_val = yaml_console["mailhost"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "localhost")

        str_val = yaml_console["fromaddr"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "my_app@domain.tld")

        seq_str_val = yaml_console["toaddrs"].data
        self.assertIsInstance(seq_str_val, Sequence)
        self.assertEqual(len(seq_str_val), 2)
        str_val = yaml_console["toaddrs"][0].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "support_team@domain.tld")
        str_val = yaml_console["toaddrs"][1].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "dev_team@domain.tld")

        str_val = yaml_console["subject"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "Houston, we have a problem.")

        yaml_qhand = actual["qhand"]

        str_val = yaml_qhand["class"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "logging.handlers.QueueHandler")

        str_val = yaml_qhand["queue"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "my.module.queue_factory")

        str_val = yaml_qhand["listener"].data
        self.assertIsInstance(str_val, str)
        self.assertEqual(str_val, "my.package.CustomListener")

        seq_str_val = yaml_qhand["handlers"].data
        self.assertIsInstance(seq_str_val, Sequence)
        self.assertEqual(len(seq_str_val), 2)

        bool_val = yaml_qhand["respect_handler_level"].data
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

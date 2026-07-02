"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Unittest for logging_capture module

"""

import logging
import sys
import tempfile
import unittest
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    cast,
)
from unittest.mock import patch

from logging_strict import (
    LoggingState,
    setup_logging_yaml,
    worker_yaml_curated,
)
from logging_strict.constants import (
    LOG_FORMAT,
    g_app_name,
)
from logging_strict.tech_niques import (
    LoggerRedirector,
    detect_coverage,
)
from logging_strict.tech_niques.logging_capture import (
    _LoggingWatcher,  # pyright: ignore[reportPrivateUsage]
)
from logging_strict.tech_niques.logging_capture import (
    _normalize_formatter,  # pyright: ignore[reportPrivateUsage]
)
from logging_strict.tech_niques.logging_capture import (
    _normalize_level,  # pyright: ignore[reportPrivateUsage]
)
from logging_strict.tech_niques.logging_capture import (
    _normalize_level_name,  # pyright: ignore[reportPrivateUsage]
)
from logging_strict.tech_niques.logging_capture import (
    captureLogs,
    captureLogsMany,
)

from logging_strict.tech_niques.logging_capture import (  # type: ignore[attr-defined]  # isort:skip
    getLevelNamesMapping,  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType]  # fmt: skip
)

if TYPE_CHECKING:
    from collections.abc import (
        Iterator,
        Sequence,
    )
    from typing import Any


class AppLoggingStateSafe(unittest.TestCase):
    """The functions being tested shouldn't avoid causing, hard to
    track down, side effects.

    When run by the UI, on unittest screens, CaptureLogs is being
    used! So if CaptureLogs has side effects, it's really confusing.

    Whereas RecipeScreen is being run within a
    :py:class:`multiprocessing.pool.Pool`. So adverse changes to
    :py:mod:`logging.config` will not propagate outside of a worker process

    Not so with a ThreadPool.

    How to test:

    - Run in the cli (no UI to interfere with)
    - Run in the UI, FunctionsScreen (Thread workers)
    - Run as a recipe, RecipeScreen (Process workers)

    """

    def setUp(self) -> None:
        """Currently testing package logging_strict. The logging.config
        yaml file within package is in ``configs/`` folder.

        If this unittest is being run from within a UI app, do nothing.

        If being run from cli, need to initialize logging.

        If being run from within a worker process, do nothing. The
        worker is responsible for setting up logging.

        If being run within a threadpool, that's insane, refactor as a
        :py:class:`multiprocessing.pool.Pool`

        Choose the logging config yaml. Which can be located within a:

        - logging_strict package

        - 2nd party package (your package)

        - 3rd party package

        Provide enough info to find it within whichever package it's in.
        """
        log_state = LoggingState()  # Singleton
        self.is_state_app = log_state.is_state_app  # get the saved state
        if not self.is_state_app:
            # UI never been initiated. Default logging levels have not been set
            with (
                tempfile.TemporaryDirectory() as fp,
                patch(  # extract use temp folder
                    f"{g_app_name}.logging_api._get_path_config",
                    return_value=Path(fp),
                ),
                patch(  # as_str use temp folder
                    f"{g_app_name}.logging_yaml_abc._get_path_config",
                    return_value=Path(fp),
                ),
            ):
                # Step 1 -- in (worker) entrypoint
                t_ret = worker_yaml_curated(
                    genre="mp",
                    flavor="asz",
                    version_no="1",
                    package_start_relative_folder="",
                )
                f_relpath, str_yaml = t_ret  # pyright: ignore[reportUnusedVariable]
                # Step 2 -- in worker
                setup_logging_yaml(str_yaml)

        LoggerRedirector.redirect_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def tearDown(self) -> None:
        """unittest will revert sys.stdout and sys.stderr after this"""
        LoggerRedirector.reset_loggers(
            fake_stdout=sys.stdout,
            fake_stderr=sys.stderr,
        )

    def test_normalize_level_name(self) -> None:
        """From current logger, normalize logging level name"""
        root = logging.getLogger("root")
        level = root.getEffectiveLevel()
        expected_root = logging.getLevelName(level)

        # logging.Logger("root")
        actual_root = _normalize_level_name(root)
        self.assertEqual(expected_root, actual_root)

        # str or None --> root logger
        roots = (
            "root",
            "",
            None,
            "     ",
        )
        for root_ in roots:
            levelname_root = _normalize_level_name(root_)
            self.assertEqual(expected_root, levelname_root)

        # int levels --> TypeError. Instead use, ``_normalize_level``
        with self.assertRaises(TypeError):
            _normalize_level_name(30)

        # logging.Logger(app) as logging.Logger and as str
        logger_app = logging.getLogger(g_app_name)
        """
        sames = (
            logger_app,
            g_app_name,
        )
        """
        same_0 = logger_app
        levelname = _normalize_level_name(same_0)
        # EffectiveLevel, not level. level is NOTSET
        self.assertEqual(levelname, "ERROR")

        same_1 = g_app_name
        levelname = _normalize_level_name(same_1)
        # EffectiveLevel, not level. level is NOTSET
        self.assertEqual(levelname, "ERROR")

        self.assertFalse(logger_app.isEnabledFor(logging.DEBUG))
        self.assertFalse(logger_app.isEnabledFor(logging.INFO))
        self.assertFalse(logger_app.isEnabledFor(logging.WARNING))
        self.assertTrue(logger_app.isEnabledFor(logging.ERROR))
        self.assertTrue(logger_app.isEnabledFor(logging.CRITICAL))

    def test_normalize_level(self) -> None:
        """From level, normalize logging level name

        The logging.config yaml file has root level logging.ERROR (40),
        not default, logging.WARNING (30)
        """
        # logging.Logger
        # ##################
        root = logging.getLogger("root")
        level = root.getEffectiveLevel()
        expected_level_root = logging.getLevelName(level)

        #    static type checkers import issue
        t_level_names = cast(
            "tuple[str, ...]",
            tuple(getLevelNamesMapping().keys()),  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownArgumentType]  # fmt: skip
        )
        d_level_map = cast("dict[str, int]", getLevelNamesMapping())

        # Assume root logger
        roots = (
            "",
            None,
            "       ",
            "root",
        )
        for root_ in roots:
            actual_level_name = _normalize_level(root_)
            self.assertEqual(expected_level_root, actual_level_name)

        # Take level from current logger
        logger_app = logging.getLogger(g_app_name)

        if logger_app.level == logging.NOTSET:
            # Looks at ancestor(s). Which is root logger
            actual_level = logger_app.getEffectiveLevel()
            actual_level_name = logging.getLevelName(actual_level)
            self.assertEqual(expected_level_root, actual_level_name)
        else:
            expected_level_name = logging.getLevelName(logger_app.level)
            actual_level_name = _normalize_level(logger_app)
            self.assertEqual(actual_level_name, expected_level_name)

        # Another logging.Logger (see logging.config yaml root logger level)
        log_foo = logging.getLogger("foo")
        actual_level_name = _normalize_level(log_foo)
        self.assertIn(
            actual_level_name,
            t_level_names,
        )
        level_by_runner = logging.INFO if detect_coverage() else logging.ERROR
        self.assertEqual(d_level_map[actual_level_name], level_by_runner)

        # int
        # ##################

        # 1 < x < 49
        invalids_0 = (
            11,
            49,
            51,
            -1,
            1,
        )
        for invalid_0 in invalids_0:
            with self.assertRaises(ValueError):
                _normalize_level(invalid_0)

        valids_0 = (
            logging.NOTSET,
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
            logging.FATAL,  # Same as logging.CRITICAL
        )
        for valid_0 in valids_0:
            self.assertIsInstance(valid_0, int)
            actual_level_name = _normalize_level(valid_0)
            self.assertIn(actual_level_name, t_level_names)
            self.assertEqual(d_level_map[actual_level_name], valid_0)

        # Unsupported type
        # ##################
        invalids_1 = (11.4,)
        for invalid_1 in invalids_1:
            with self.assertRaises(TypeError):
                _normalize_level(invalid_1)

        # str
        # ##################
        valids_1 = (
            "0",
            "10",
            "20",
            "30",
            "40",
            "50",
        )
        for valid_1 in valids_1:
            actual_level_name = _normalize_level(valid_1)
            self.assertIn(actual_level_name, t_level_names)
            self.assertEqual(d_level_map[actual_level_name], int(valid_1))

        valids_2 = (
            "NOTSET",
            "DEBUG",
            "INFO",
            "ERROR",
            "WARNING",
            "CRITICAL",
            "FATAL",
        )
        for valid_2 in valids_2:
            actual_level_name = _normalize_level(valid_2)
            self.assertIn(actual_level_name, t_level_names)

        # 1 < x < 49
        invalids_2 = (
            "11",
            "49",
            "51",
            "-1",
            "1",
        )
        for invalid_2 in invalids_2:
            with self.assertRaises(ValueError):
                _normalize_level(invalid_2)

    def test_normalize_formatter(self) -> None:
        """Deal with sending nonsense and insist it can become a logging formatter"""
        # Unsupported type --> fallback. logging.Formatter only accepts str
        invalids_0 = (
            0.1234,
            12,
        )
        for invalid_0 in invalids_0:
            fmt = _normalize_formatter(invalid_0)
            self.assertIsInstance(fmt, logging.Formatter)

        # Invalid format str --> fallback logging.Formatter str
        invalids_1 = ("asdf %q sadf ",)
        for invalid_1 in invalids_1:
            fmt = _normalize_formatter(invalid_1)
            self.assertIsInstance(fmt, logging.Formatter)

        # Probably uses the default format
        invalids_2 = (
            None,
            "",
            "     ",
        )
        for invalid_2 in invalids_2:
            fmt = _normalize_formatter(invalid_2)
            self.assertIsInstance(fmt, logging.Formatter)


class TestsLoggingCapture(unittest.TestCase):
    """Logging capture tests"""

    def setUp(self) -> None:
        """Ensure root logger"""
        self.root = logging.getLogger("")
        # self.root.setLevel(logging.WARNING)
        # print(self.root.getChildren())
        pass

    def tearDown(self) -> None:
        """Ensure root logger"""
        # print(self.root.getChildren())
        # self.root.setLevel(logging.WARNING)
        pass

    def test_capture_logs(self) -> None:
        """captureLogs, within context manager, captures stderr and stdout"""
        module_name = str(Path(__file__).stem)
        MSG_0 = "first message"
        MSG_1 = "second message"
        WORKER_0 = "foo"
        WORKER_1 = "foo.bar"
        workers = (
            WORKER_0,
            WORKER_1,
        )

        # _LogsContext.LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"
        formats = (
            None,  # --> LOG_FORMAT
            4,  # --> LOG_FORMAT
            LOG_FORMAT,
        )

        def get_captured(
            logger_names: "Sequence[Any]",
            levels: "Sequence[str | int | Any | None]",
        ) -> "Iterator[tuple[Any, Sequence[str]]]":
            """Demonstrate captureLogs context manager"""
            if TYPE_CHECKING:
                msgs: list[str]

            for logger_name in logger_names:
                for level in levels:
                    for format_ in formats:
                        # print(f"logger_name (before with block): {logger_name}")
                        # print(f"level (before with block): {level}")
                        # print(f"format_ (before with block): {format_}")
                        with captureLogs(
                            logger=logger_name,
                            level=level,
                            format_=format_,  # type: ignore[arg-type]
                        ) as cm:
                            log_0 = logging.getLogger(WORKER_0)
                            log_0.info(MSG_0)
                            log_1 = logging.getLogger(WORKER_1)
                            log_1.error(MSG_1)

                        msgs = []
                        msg_0 = (
                            f"logger_name: {logger_name} level: {level} "
                            f"format_: {format_}"
                        )
                        msgs.append(msg_0)
                        msg_1 = f"cm.output: {cm.output} cm {cm}"
                        msgs.append(msg_1)
                        # print("\n".join(msgs))
                        # ['INFO:foo:first message', 'ERROR:foo.bar:second message']
                        # messages
                        self.assertIsInstance(cm.output, list)
                        t_ret = (logger_name, cm.output)
                        yield t_ret

        def is_a_worker(logger_name: "Any | None") -> bool:
            """Check if logger name in Sequence workers.

            :param logger_name: logger name
            :type logger_name: typing.Any | None
            :returns: True if logger_name in workers otherwise False
            :rtype: bool
            """
            return (
                logger_name is not None
                and isinstance(logger_name, str)
                and logger_name in workers
            )

        meth_name = "get_captured"
        d_level_map = cast(
            "dict[str, int]",
            logging.getLevelNamesMapping(),  # type: ignore[attr-defined]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]  # fmt: skip
        )

        # LEVELS
        # #############
        levels_0 = (
            10,  # --> DEBUG
            20,  # --> INFO
        )
        logger_names_worker_0 = (WORKER_0,)
        for logger_name, messages in get_captured(logger_names_worker_0, levels_0):
            msg = (
                f"logger {logger_name} messages {messages} count "
                f"{len(messages)} Should be 2"
            )
            # print(msg)
            self.assertEqual(len(messages), 2)

        levels_1 = (
            30,  # --> WARNING
            40,  # --> ERROR
        )
        logger_names_worker_0 = (WORKER_0,)
        for logger_name, messages in get_captured(logger_names_worker_0, levels_1):
            self.assertEqual(len(messages), 1)

        levels_2 = (50,)  # --> CRITICAL
        logger_names_worker_0 = (WORKER_0,)
        for logger_name, messages in get_captured(logger_names_worker_0, levels_2):
            self.assertEqual(len(messages), 0)

        """Cast a very wide net. Capture all logging; level is set to DEBUG

        - Captured: ~NOTSET. DEBUG, INFO, WARNING, ERROR, CRITICAL

        - Logged: Nothing should be logged

        """
        levels_3 = (
            None,  # --> Same as root or EffectiveLevel. aka WARNING
            "",  # --> Same as root or EffectiveLevel
        )
        logger_names_worker_0 = (WORKER_0,)
        for logger_name, messages in get_captured(logger_names_worker_0, levels_3):
            self.assertEqual(len(messages), 1)

        # ValueError
        levels_4 = (
            4,  # --> KISS principle
            51,  # --> outside of range
        )
        with self.assertRaises(ValueError):
            for logger_name, messages in get_captured(logger_names_worker_0, levels_4):
                self.assertEqual(len(messages), 2)

        # TypeError
        levels_5 = (4.44,)  # --> unsupported type
        with self.assertRaises(TypeError):
            for logger_name, messages in get_captured(logger_names_worker_0, levels_5):
                self.assertEqual(len(messages), 2)

        # ancestor logger root level is logging.WARNING
        levels_6 = (
            0,  # --> NOTSET
            logging.NOTSET,
            "NOTSET",
        )
        for logger_name, messages in get_captured(logger_names_worker_0, levels_6):
            self.assertEqual(len(messages), 1)

        # LOGGER NAME
        # #############

        # For logger name, unsupported type
        logger_name_changes_7 = (
            4,  # other --> root
            51,  # other --> root
            4.44,  # other --> root
        )
        # INFO+ captured
        levels_7 = (
            "INFO",
            logging.INFO,
        )
        for level_7 in levels_7:
            with self.assertRaises(TypeError):
                for logger_name, messages in get_captured(
                    logger_name_changes_7, (level_7,)
                ):
                    pass

        # root logger
        logger_name_changes_7_point_5 = (None,)
        for logger_name, messages in get_captured(
            logger_name_changes_7_point_5, levels_7
        ):
            self.assertNotIsInstance(logger_name, str)
            level_name = _normalize_level_name(logger_name)

            lst_messages = cast("list[str]", messages)
            if len(lst_messages) == 1:
                msg = lst_messages.pop()
                parts = msg.split(":")
                if is_a_worker(logger_name):
                    # Will only have the message from that particular worker
                    self.assertIn(f"{module_name} {meth_name}", parts[0])
                else:
                    self.assertIn(level_name, ("WARNING", "ERROR"))
                    self.assertEqual(parts[0], f"ERROR {module_name} {meth_name}")
                    # self.assertEqual(parts[1], WORKER_1) --> lineno
                    self.assertEqual(parts[2].strip(), MSG_1)
            elif len(lst_messages) == 2:
                # If NOTSET, DEBUG, INFO
                if detect_coverage():
                    self.assertIn(
                        level_name, ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR")
                    )
                else:
                    self.assertIn(level_name, ("NOTSET", "DEBUG", "INFO"))

                msg_two = lst_messages.pop()
                msg_one = lst_messages.pop()
                self.assertIsInstance(msg_one, str)
                self.assertIsInstance(msg_two, str)
                # print(f"test_capture_logs parts: {parts}. Whats parts[0]?")
                parts = msg_one.split(":")
                self.assertEqual(parts[0], f"INFO {module_name} {meth_name}")
                # self.assertEqual(parts[1], WORKER_0) --> lineno
                self.assertEqual(parts[2].strip(), MSG_0)

                parts = msg_two.split(":")
                self.assertEqual(parts[0], f"ERROR {module_name} {meth_name}")
                # self.assertEqual(parts[1], WORKER_1) --> lineno
                self.assertEqual(parts[2].strip(), MSG_1)
            else:  # pragma: no cover
                # No messages cuz level too high
                self.assertEqual(len(lst_messages), 0)

            # Exceptions pass thru
            with (
                self.assertRaises(RuntimeError),
                captureLogs(logger=logger_name, level=level_name),
            ):
                msg_exc = "Oh no! This is bad"
                raise RuntimeError(msg_exc)

        """logger foo at logging level INFO, not WARNING"""
        logger_name_bad = (logging.getLogger(WORKER_0),)  # logging.Logger; foo
        # INFO+ captured
        levels_8 = (
            "INFO",
            logging.INFO,
        )
        level_no_8_expected = 20
        for logger_name_8, messages_8 in get_captured(logger_name_bad, levels_8):
            lst_messages_8 = cast("list[str]", messages_8)
            msg_count = len(lst_messages_8)

            self.assertIsInstance(logger_name_8, logging.Logger)
            #    Proves reason for capturing two must be due to arg: ``levels``
            #    level_no_8 = logger_name_8.level
            level_no_8 = logger_name_8.getEffectiveLevel()
            level_name_8 = logging.getLevelName(level_no_8)  # pyright: ignore[reportDeprecated]  # fmt: skip
            effective_level_name = _normalize_level_name(level_name_8)  # noqa: F841  # pyright: ignore[reportUnusedVariable]  # fmt: skip

            # level_by_runner = "INFO" if detect_coverage() else "ERROR"
            # self.assertEqual(effective_level_name, level_by_runner)
            level_no_8_actual = d_level_map[level_name_8.upper()]
            self.assertEqual(level_no_8_actual, level_no_8_expected)

            self.assertEqual(msg_count, 2)
            msg_two = lst_messages_8.pop()
            msg_one = lst_messages_8.pop()
            self.assertIsInstance(msg_one, str)
            self.assertIsInstance(msg_two, str)
            parts = msg_one.split(":")
            self.assertEqual(parts[0], f"INFO {module_name} {meth_name}")
            # self.assertEqual(parts[1], WORKER_0) --> lineno
            self.assertEqual(parts[2].strip(), MSG_0)

        levels_9 = (
            "WARNING",
            logging.WARNING,
        )
        for logger_name, messages_9 in get_captured(logger_name_bad, levels_9):
            lst_messages_9 = cast("list[str]", messages_9)
            msg_count_9 = len(lst_messages_9)
            self.assertIsInstance(logger_name, logging.Logger)
            self.assertEqual(msg_count_9, 1)
            msg = lst_messages_9.pop()
            parts = msg.split(":")
            self.assertIn(f"{module_name} {meth_name}", parts[0])

        levels_10 = (
            "CRITICAL",
            logging.CRITICAL,
        )
        for logger_name, messages_10 in get_captured(logger_name_bad, levels_10):
            lst_messages_10 = cast("list[str]", messages_10)
            msg_count_10 = len(lst_messages_10)
            self.assertIsInstance(logger_name, logging.Logger)
            self.assertEqual(msg_count_10, 0)

    def test_capture_decendants_msgs_nested(self) -> None:
        """For parent to capture both descendant msgs, this nesting will not work"""
        MSG_0 = "first message"
        MSG_1 = "second message"
        WORKER_BOTH = "foo"
        WORKER_0 = "foo.baz"
        WORKER_1 = "foo.bar"

        """Decendants level is initially NOTSET. If set, parent can
        magically capture **both** msgs"""
        log_0 = logging.getLogger(WORKER_0)
        log_0.setLevel("INFO")
        log_1 = logging.getLogger(WORKER_1)
        log_1.setLevel("INFO")

        with captureLogs(logger=log_1, level="INFO") as cm2:
            log_1.error(MSG_1)
            messages = cm2.output
            self.assertIsInstance(messages, list)
            msg_count = len(messages)
            self.assertEqual(msg_count, 1)
            # cm2.output captured, not propagated up to cm.output
            with captureLogs(logger=logging.getLogger(WORKER_BOTH), level="INFO") as cm:
                log_0.info(MSG_0)
                messages = cm.output
                self.assertIsInstance(messages, list)
                msg_count = len(messages)
                self.assertEqual(msg_count, 1)  # not 2

    def test_capture_descendants_msgs(self) -> None:
        """Parent captures descendants messages"""
        MSG_0 = "first message"
        MSG_1 = "second message"
        WORKER_BOTH = "foo"
        WORKER_0 = "foo.baz"
        WORKER_1 = "foo.bar"

        # Set descendants loggers and levels **BEFORE** calling captureLogs
        log_0 = logging.getLogger(WORKER_0)
        log_1 = logging.getLogger(WORKER_1)
        log_0.setLevel("INFO")
        log_1.setLevel("INFO")

        with captureLogs(logger=logging.getLogger(WORKER_BOTH), level="INFO") as cm:
            log_1.error(MSG_1)
            log_0.info(MSG_0)

        messages = cm.output
        self.assertEqual(len(messages), 2)

    @unittest.skipIf(
        sys.version_info >= (3, 12),
        "py312 feature, backport unneeded",
    )
    def test_py312_backport(self) -> None:
        """Backported py312 logging.getHandlerNames and logging.getHandlerByName

        :py:class:`captureLogs` temporarily redirects handlers for one logger, the
        one provided. Not for loggers or capture (and classify) all logging.
        """
        if TYPE_CHECKING:
            logger_both: logging.Logger

        WORKER_0 = "foo.baz"
        WORKER_1 = "foo.bar"
        WORKER_BOTH = "foo"
        MSG_0 = "first message"
        MSG_1 = "second message"

        from logging_strict.tech_niques.logging_capture import logging as logging2  # type: ignore[attr-defined]  # fmt: skip

        logger_both = cast(  # type: ignore[redundant-cast]
            "logging.Logger",
            logging2.getLogger(WORKER_BOTH),  # pyright: ignore[reportUnknownMemberType]
        )
        self.assertIsInstance(
            logger_both,  # pyright: ignore[reportUnknownArgumentType]
            logging.Logger,
        )
        self.assertEqual(
            logger_both.name,  # pyright: ignore[reportUnknownMemberType]
            WORKER_BOTH,
        )
        level_by_runner = logging.INFO if detect_coverage() else logging.ERROR
        self.assertEqual(
            logger_both.level,  # pyright: ignore[reportUnknownMemberType]
            level_by_runner,
        )

        handler_names = logging2.getHandlerNames()  # type: ignore[attr-defined]
        self.assertIsInstance(
            handler_names,  # pyright: ignore[reportUnknownArgumentType]
            frozenset,
        )

        self.assertIsInstance(
            logger_both.hasHandlers(),  # pyright: ignore[reportUnknownArgumentType,reportUnknownMemberType]  # fmt: skip
            bool,
        )
        self.assertIsNone(logging2.getHandlerByName(WORKER_BOTH))  # type: ignore[attr-defined]  # fmt: skip

        with captureLogs(
            logger=logger_both,  # pyright: ignore[reportUnknownArgumentType]
            level="INFO",
        ) as cm:
            self.assertTrue(hasattr(cm, "getHandlerNames"))
            self.assertTrue(hasattr(cm, "getHandlerByName"))
            self.assertEqual(len(cm.output), 0)

            logging.getLogger(WORKER_1).error(MSG_1)
            logging.getLogger(WORKER_0).info(MSG_0)

            # print(f"cm {cm}")
            # print(f"len(cm.output): {len(cm.output)} Should be 2")
            self.assertEqual(len(cm.output), 2)

            handler_names = cm.getHandlerNames()
            self.assertIsInstance(handler_names, frozenset)

            self.assertIsNone(cm.getHandlerByName(WORKER_BOTH))

    def test_watch_many(self) -> None:
        """Micro manage loggers and their respective logging levels"""
        loggers = ("foo.bar", "bar.foo", "")
        levels = ("INFO", "WARNING", "ERROR")
        msgs = ("first message", "second message", "third message")

        MSG_MEMORY_HOLE = "This is my password"
        with captureLogsMany(
            loggers=loggers,
            levels=levels,
            format_=LOG_FORMAT,
        ) as cms:
            log_0 = logging.getLogger(loggers[0])
            log_0.error(msgs[0])
            log_0.debug(MSG_MEMORY_HOLE)

            log_1 = logging.getLogger(loggers[1])
            log_1.warning(msgs[1])
            log_1.info(MSG_MEMORY_HOLE)

            log_2 = logging.getLogger(loggers[2])
            log_2.error(msgs[2])
            log_2.warning(MSG_MEMORY_HOLE)

            for idx, cm in enumerate(cms):
                # print(f"idx {idx} cm {cm}")
                # print(f"len(cm.output): {len(cm.output)} Should be 1")
                self.assertEqual(len(cm.output), 1)
                # cm.records (contains list[logging.LogRecord])
                rec_0 = cm.records[0]
                rec_0_level_no = rec_0.levelno
                int_level = cm.getLevelNo(levels[idx])
                self.assertIsInstance(int_level, int)
                if isinstance(int_level, int):
                    self.assertGreaterEqual(rec_0_level_no, int_level)

                if len(loggers[idx]) == 0:
                    self.assertEqual(rec_0.name, "root")
                else:
                    self.assertEqual(rec_0.name, loggers[idx])
                self.assertEqual(rec_0.msg, msgs[idx])

                # cm.output
                out_0 = cm.output[0]
                self.assertIn(msgs[idx], out_0)

                # Unrecognized logging level name
                self.assertIsNone(cm.getLevelNo("dog"))

        # Exceptions pass thru
        with (
            self.assertRaises(RuntimeError),
            captureLogsMany(
                loggers=loggers,
                levels=levels,
                format_=0.12345,  # type: ignore[arg-type]
            ) as cms,
        ):
            msg_exc = "Oh no! This is bad"
            raise RuntimeError(msg_exc)

    def test_logger_watcher(self) -> None:
        """Test _LoggingWatcher seperately."""
        if TYPE_CHECKING:
            records: list[logging.LogRecord]
            output: list[str]

        records = []
        output = []
        WORKER_BOTH = "foo"
        watcher = _LoggingWatcher(records, output)
        logger_both = logging.getLogger(WORKER_BOTH)  # noqa: F841  # pyright: ignore[reportUnusedVariable]  # fmt: skip
        name = WORKER_BOTH
        handler = watcher.getHandlerByName(name)
        self.assertIsNone(handler)
        handler_names = watcher.getHandlerNames()
        self.assertIsInstance(handler_names, frozenset)


class DocumentAssertLogs(unittest.TestCase):
    """Show unittest way of capturing all log output"""

    def test_assert_logging_output(self) -> None:
        """Test has logging output"""
        with self.assertLogs("foo", level="INFO") as cm:
            logging.getLogger("foo").info("first message")
            logging.getLogger("foo.bar").error("second message")
        out_expected = [
            "INFO:foo:first message",
            "ERROR:foo.bar:second message",
        ]
        self.assertEqual(cm.output, out_expected)


if __name__ == "__main__":  # pragma: no cover
    """Does not contribute to module ``util/logging_capture`` coverage.
    The point is to document the technique

    .. code-block:: shell

       python -m unittest tests.tech_niques.test_logging_capture --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k AppLoggingStateSafe.test_normalize_level_name --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k AppLoggingStateSafe.test_normalize_level --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k AppLoggingStateSafe.test_normalize_formatter --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k TestsLoggingCapture.test_capture_logs --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k TestsLoggingCapture.test_capture_decendants_msgs_nested --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k TestsLoggingCapture.test_capture_decendants_msgs --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k TestsLoggingCapture.test_py312_backport --locals

       python -m unittest tests.tech_niques.test_logging_capture \
       -k TestsLoggingCapture.test_watch_many --locals

       python -m unittest discover \
       -t . -s "tests/tech_niques" -k "test_logging_capture" --verbose --locals

       coverage run --data-file=".coverage-combine-12" \
       -m unittest discover -t. -s tests/tech_niques -p "test_logging_capture*.py" --locals

       coverage run --data-file=".coverage-combine-30" \
       -m unittest discover -t. -s tests/tech_niques -p "test_docs_logging_capture*.py" --buffer

       coverage run --data-file=".coverage-combine-32" \
       -m unittest discover -t. -s tests -p "test_check_logging*.py" --buffer

       coverage combine --keep --data-file=".coverage-recipe-12-30-32" \
       .coverage-combine-12 .coverage-combine-30 .coverage-combine-32

       coverage report --include="*logging_capture*" --no-skip-covered \
       --data-file=".coverage-recipe-12-30-32"


    """
    unittest.main(tb_locals=True)

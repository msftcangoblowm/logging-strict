.. _api_asynchronous_logging:

====================
Asynchronous logging
====================

async/await unittests are separated from synchronous unittest. The
synchronous redirector (:ref:`api_synchronous_logging`) is not suitable for async code

Package :pypi_org:`aiologger` docs are authoritative, but sparse/terse.

>>> from logging import Logger
>>> import os
>>> import unittest
>>> import sys
>>>
>>> from aiologger.filters import StdoutFilter
>>> from aiologger.formatters.base import Formatter
>>> from aiologger.handlers.streams import AsyncStreamHandler
>>> from aiologger.levels import LogLevel
>>> from aiologger.logger import Logger
>>>
>>> from logging_strict.constants import LOG_FORMAT
>>>
>>> g_app_name = "asz"  # your package
>>>
>>> class WithoutUiAsyncModules(unittest.IsolatedAsyncioTestCase):
...     logger: Logger
...
...     async def asyncSetUp(self):
...         fmt = Formatter(LOG_FORMAT)
...         handler_stdout = AsyncStreamHandler(
...             stream=os.fdopen(os.dup(sys.__stdout__.fileno())),
...             level=LogLevel.INFO,
...             filter=StdoutFilter(),
...             formatter=fmt,
...         )
...         handler_stderr = AsyncStreamHandler(
...             stream=os.fdopen(os.dup(sys.__stderr__.fileno())),
...             level=LogLevel.INFO,
...             formatter=fmt,
...         )
...         self.logger = Logger(name=g_app_name)
...         self.logger.add_handler(handler_stdout)
...         self.logger.add_handler(handler_stderr)
...
...     async def asyncTearDown(self):
...         """Complains of open read-only files (in aiologger code,
...         coroutine not awaited). Suppress the warnings on shutdown (as
...         :py:meth:`aiologger.logger.Logger.shutdown` suggests"""
...         if not sys.warnoptions:
...             warnings.simplefilter("ignore")
...             await self.logger.shutdown()
...             for handler in reversed(self.logger.handlers):
...                 if not handler.initialized:
...                     self.logger.remove_handler(handler)
...                 else:  # pragma: no cover
...                     pass
...             del self.logger
...         else:  # pragma: no cover
...             pass
...

:code:`await self.logger.info` will log asynchronously
:code:`self.logger.info` will log synchronously

Depends on the circumstances which one to use. Great to have both options.

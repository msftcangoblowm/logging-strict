.. _api_logging_handlers:

======================
logging (third party)
======================

Without :ref:`Capture logging <api_capture_logging>`, to capture python
modules or third party packages log messages, would configure
logging handlers .

Obviously this is more involved and messy.

Basic logging config captures one package level and below.

>>> import logging
>>> import sys
>>> from asz.constants import LOG_FORMAT
>>> g_module = "asz.tests_one.test_folder_contains_one"
>>> g_logger = logging.getLogger(g_module)
>>> logging.basicConfig(
...     format=LOG_FORMAT,
...     level=logging.INFO,
...     stream=sys.stdout,
... )

More advanced logging that captures root logger

>>> import logging
>>> import logging.config
>>> from asz.constants import CONFIG_THREAD_WORKER
>>> g_module = "asz.tests_one.test_folder_contains_one"
>>> g_logger = logging.getLogger(g_module)
>>> logging.config.dictConfig(CONFIG_THREAD_WORKER)

dict config configuration (CONFIG_THREAD_WORKER)

.. code-block:: text

   LOG_FMT_DETAILED = (
       "%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s"
   )
   LOG_FMT_SIMPLE = "%(name)-15s %(levelname)-8s %(processName)-10s %(message)s"
   LOG_LEVEL_WORKER = "INFO"
   CONFIG_THREAD_WORKER = {  # type: ignore
        "version": 1,
        "formatters": {
            "detailed": {"class": "logging.Formatter", "format": LOG_FMT_DETAILED},
            "simple": {"class": "logging.Formatter", "format": LOG_FMT_SIMPLE},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": LOG_LEVEL_WORKER,
            }
        },
       "root": {"handlers": ["console"], "level": LOG_LEVEL_WORKER},
    }

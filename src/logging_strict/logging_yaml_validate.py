"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("schema_logging_config", "validate_yaml_dirty")

   Module exports

"""

from __future__ import annotations

import sys
from functools import partial

import strictyaml as s

__all__ = (
    "schema_logging_config",
    "validate_yaml_dirty",
)

format_style = s.Enum(["%", "{", "$"])
format_style_default = "%"
# https://github.com/python/cpython/blob/ae7fa9fa60c7dc446c0681122037ab27adf35b51/Lib/logging/__init__.py#L98
levels = s.Enum(
    [
        "UNSET",
        "DEBUG",
        "INFO",
        "WARN",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "FATAL",
    ],
)
logger_keys = s.Enum(
    ["level", "filters", "handlers", "propagate"],
)
logging_config_keys = s.Enum(
    [
        "version",
        "formatters",
        "filters",
        "handlers",
        "loggers",
        "root",
        "incremental",
        "disable_existing_loggers",
    ]
)

if sys.version_info >= (3, 12):  # pragma: no cover
    # logging.Formatter <https://docs.python.org/3/library/logging.html#logging.Formatter>`_
    # `format <https://docs.python.org/3/library/logging.html#logrecord-attributes>`_
    formatter_map = s.MapCombined(  # map validator
        {
            s.Optional("format", default=None, drop_if_none=False): s.Str()
            | s.EmptyNone(),
            s.Optional("datefmt", default=None, drop_if_none=False): s.Str()
            | s.EmptyNone(),
            s.Optional("style", default=format_style_default): format_style,
            s.Optional("validate", default=True): s.Bool(),  # py38
            s.Optional("defaults"): s.MapPattern(s.Str(), s.Any()),  # py312
            s.Optional("class"): s.Str(),
        },
        s.Str(),  # key validator
        # value validator
        s.OrValidator(
            s.OrValidator(
                s.OrValidator(s.Bool(), s.Str()),
                format_style,
            ),
            s.MapPattern(s.Str(), s.Any()),  # defaults
        ),
    )
else:  # pragma: no cover
    formatter_map = s.MapCombined(  # map validator
        {
            s.Optional("format", default=None, drop_if_none=False): s.Str()
            | s.EmptyNone(),
            s.Optional("datefmt", default=None, drop_if_none=False): s.Str()
            | s.EmptyNone(),
            s.Optional("style", default=format_style_default): format_style,
            s.Optional("validate", default=True): s.Bool(),  # py38
            s.Optional("class"): s.Str(),
        },
        s.Str(),  # key validator
        s.OrValidator(
            s.OrValidator(s.Bool(), s.Str()),
            format_style,
        ),
    )

# filters
filters_map = s.MapCombined(
    {
        s.Optional("level"): s.Str(),
        s.Optional("()"): s.Str(),  # followed by random params
    },
    s.Str(),  # all keys are str.
    s.Str(),  # all values are str e.g. dotted path to a function
)

# handlers
#    ``All other keys are passed through as keyword arguments to the handler’s constructor``
#    Downside: unknown keys' value passthrough as str, not int
#
#    args and kwargs
#    https://docs.python.org/3/library/logging.config.html#configuration-file-format
#
#    QueueHandler and QueueListener
#    https://docs.python.org/3/library/logging.config.html#configuring-queuehandler-and-queuelistener
#
# For setting default types for these handler args/kwargs
#
# https://peps.python.org/pep-0020/ -- `explicit is better than implicit`
handlers_map = s.MapCombined(
    {
        s.Optional("class"): s.Str(),
        s.Optional("()"): s.Str(),  # '()': ext://textual.logging.TextualHandler
        s.Optional("level"): levels,
        s.Optional("formatter"): s.Str(),
        s.Optional("filters"): s.Seq(s.Str()),  # also filter instances py311 ??
        # Think this is fileConfig, not dictConfig
        # default=[] removed
        # s.Optional("args"): s.Seq(s.Any()) | s.EmptyList(),
        # default={} removed
        # s.Optional("kwargs"): s.MapPattern(s.Str(), s.Any()) | s.EmptyDict(),
        # args
        # #######
        s.Optional("filename"): s.Str(),  # FileHandler, WatchedFileHandler, ...
        s.Optional("host"): s.Str(),  # SocketHandler, DatagramHandler
        s.Optional("port"): s.Int(),  # SocketHandler, DatagramHandler
        s.Optional("appname"): s.Str(),  # NTEventLogHandler
        s.Optional("mailhost"): s.Str(),  # SMTPHandler
        s.Optional("fromaddr"): s.Str(),  # SMTPHandler
        s.Optional("toaddrs"): s.EmptyList() | s.Seq(s.Str()),  # SMTPHandler
        s.Optional("subject"): s.Str(),  # SMTPHandler
        s.Optional("capacity"): s.Int(),  # SMTPHandler
        s.Optional("queue"): s.Str(),  # QueueHandler and QueueListener
        s.Optional("listener"): s.Str(),  # QueueHandler and QueueListener
        s.Optional("handlers"): s.Seq(s.Str()),  # QueueHandler and QueueListener
        # kwargs ... due to side effect, can't set default
        # #######
        s.Optional("stream"): s.EmptyNone()
        | s.Str(),  # logging.StreamHandler. Default None
        s.Optional("mode"): s.Str(),  # logging.FileHandler. Default 'a'
        s.Optional("encoding"): s.EmptyNone()
        | s.Str(),  # logging.FileHandler. Default None
        s.Optional("delay"): s.Bool(),  # logging.FileHandler. Default False
        s.Optional("errors"): s.EmptyNone()
        | s.Str(),  # logging.FileHandler. Default None
        s.Optional("maxBytes"): s.Int(),  # RotatingFileHandler. Default 0
        s.Optional("backupCount"): s.Int(),  # RotatingFileHandler. Default 0
        s.Optional("when"): s.Str(),  # TimedRotatingFileHandler. Default 'h'
        s.Optional("interval"): s.Int(),  # TimedRotatingFileHandler. Default 1
        s.Optional("utc"): s.Bool(),  # TimedRotatingFileHandler. Default False
        # s.Optional("atTime"): s.EmptyNone() | "datetime.time"), TimedRotatingFileHandler. Default None
        s.Optional("address"): s.FixedSeq([s.Str(), s.Int()]),  # SysLogHandler
        s.Optional("facility"): s.Str(),  # SysLogHandler
        # socket.SOCK_STREAM or socket.SOCK_DGRAM
        s.Optional("socktype"): s.Int(),  # SysLogHandler
        s.Optional("dllname"): s.EmptyNone() | s.Str(),  # NTEventLogHandler
        s.Optional("logtype"): s.Str(),  # NTEventLogHandler
        s.Optional("credentials"): s.EmptyNone()
        | s.FixedSeq([s.Str(), s.Str()]),  # SMTPHandler
        # SMTPHandler. Default None. Or'ing together two FixedSeq is not allowed
        s.Optional("secure"): s.EmptyNone() | s.EmptyList() | s.Seq(s.Str()),
        s.Optional("timeout"): s.Float(),  # SMTPHandler. Default 1.0
        s.Optional("flushlevel"): s.Str(),  # MemoryHandler. Default "ERROR"
        s.Optional("target"): s.EmptyNone() | s.Str(),  # MemoryHandler. Default None
        s.Optional("flushOnClose"): s.Bool(),  # MemoryHandler. Default True
        # QueueHandler and QueueListener. Default False
        s.Optional("respect_handler_level"): s.Bool(),
    },
    s.Str(),
    s.Any(),  # s.OrValidator(s.OrValidator(s.Str(), levels), s.Seq(s.Str())),
)

# filters can be dotted path
#
#    qualname
#
#    https://docs.python.org/3/library/logging.config.html#configuration-file-format
#    hierarchical channel name used by an app to get the logger
loggers_map = s.Map(
    {
        s.Optional("level"): levels,
        s.Optional("propagate"): s.Bool(),
        s.Optional("filters"): s.Seq(s.Str()),  # dotted path. filters instances py311
        s.Optional("handlers"): s.Seq(s.Str()),
        s.Optional("qualname"): s.Str(),
    },
)

root_map = s.Map(
    {
        s.Optional("level"): levels,
        s.Optional("filters"): s.Seq(
            s.Str()
        ),  # dotted path. filters instances py311 ??
        s.Optional("handlers"): s.Seq(s.Str()),
    }
)

schema_logging_config = s.MapCombined(
    {
        "version": s.Enum([1], item_validator=s.Int()),  # must have 1 s.Optional
        s.Optional("formatters"): s.MapPattern(s.Str(), formatter_map),
        s.Optional("filters"): s.MapPattern(s.Str(), filters_map),
        s.Optional("handlers"): s.MapPattern(s.Str(), handlers_map),
        s.Optional("loggers"): s.MapPattern(s.Str(), loggers_map),
        s.Optional("root"): root_map,
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


def validate_yaml_dirty(
    yaml_snippet,
    schema=schema_logging_config,
):
    """This designed with the intent to verify :py:mod:`logging.config` yaml

    In :py:mod:`logging.config` docs, all examples shown contain
    YAML flow_style.

    YAML flow style (incorrect)

    .. code-block:: text

       somelist: [item0, item1]

    Without flow style (Correct)

    .. code-block:: text

       somelist:
         - item0
         - item1


    Eventhough it's easy to fix the yaml, logging.config.dictConfig will
    accept the non-fixed yaml

    Reluctantly ... allow flow style

    world+dog

    - refers to the :py:mod:`logging.config` docs

    - have based their code off the :py:mod:`logging.config` docs

    - won't be aware of yaml intricacies and intrigue

    :param yaml_snippet: :py:mod:`logging.config` YAML str
    :type yaml_snippet: str
    :param schema: :py:mod:`strictyaml` strict typing schema
    :type schema: strictyaml.Validator | :py:data:`.schema_logging_config`
    :returns: YAML object. Pass this to each worker
    :rtype: strictyaml.YAML | None
    :single-line-parameter-list:
    :single-line-type-parameter-list:

    .. seealso::

       `Modern way <https://github.com/python/cpython/pull/102885/files>`_
       of dealing with Traceback

    """
    # Allow flow style uz used often in logging.config cookbook
    func = partial(s.dirty_load, yaml_snippet, schema=schema, allow_flow_style=True)

    try:
        actual = func()
    except s.YAMLValidationError:
        raise

    return actual

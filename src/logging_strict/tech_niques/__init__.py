"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Conveniently exports all technique helpers

**Module private variables**

.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str, str]
   :value: ("get_locals", "is_class_attrib_kind", "ClassAttribTypes", \
   "LoggerRedirector", "captureLogs", "detect_coverage", "CaptureOutput")

   This modules exports

**Module objects**

"""

import enum
import inspect

from .context_locals import get_locals
from .coverage_misbehaves import detect_coverage
from .logger_redirect import LoggerRedirector
from .logging_capture import captureLogs
from .stream_capture import CaptureOutput

__all__ = (
    "get_locals",
    "is_class_attrib_kind",
    "ClassAttribTypes",
    "LoggerRedirector",
    "captureLogs",
    "detect_coverage",
    "CaptureOutput",
)


class ClassAttribTypes(enum.Enum):
    """As understood by py:obj:`inspect.classify_class_attrs`

    .. py:attribute:: CLASSMETHOD
       :type: str
       :value: 'class method'

       Is this a class classmethod?

    .. py:attribute:: STATICMETHOD
       :type: str
       :value: 'static method'

       Is this a class staticmethod

    .. py:attribute:: PROPERTY
       :type: str
       :value: 'property'

       Is this a class property?

    .. py:attribute:: METHOD
       :type: str
       :value: 'method'

       Is this a class normal method

    .. py:attribute:: DATA
       :type: str
       :value: 'data'

       Is this class data

    """

    CLASSMETHOD = "class method"
    STATICMETHOD = "static method"
    PROPERTY = "property"
    METHOD = "method"
    DATA = "data"


def is_class_attrib_kind(cls, str_m, kind):
    """For testing an ABC implementation

    :param cls: A class
    :type cls: type[typing.Any]
    :param str_m: A class member's name. Check the class interface is exists
    :type str_m: typing.Any
    :param kind: class attribute type
    :type kind: logging_strict.tech_niques.ClassAttribTypes
    :returns:

       ``True`` if is expected
       :paramref:`logging_strict.tech_niques.is_class_attrib_kind.params.kind`
       otherwise ``False``

    :rtype: bool
    :raises:

       - :py:exc:`TypeError` -- Expecting a str
       - :py:exc:`AssertionError` -- Expecting a class

    """
    if str_m is None or (str_m is not None and not isinstance(str_m, str)):
        msg_exc = f"Expecting a str. Received a {type(str_m)}"
        raise TypeError(msg_exc)
    else:
        if not inspect.isclass(cls):
            msg_exc = "Expecting a class. This is not a class"
            raise AssertionError(msg_exc)
        else:
            attribs = inspect.classify_class_attrs(cls)
            is_found = False
            for attrib in attribs:
                if attrib.name == str_m and attrib.kind == kind.value:
                    is_found = True

    return is_found

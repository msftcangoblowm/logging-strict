"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Detect runner to adjust logging level inconsistencies


**Module private variables**

.. py:data:: __all__
   :type: tuple[str]
   :value: ("detect_coverage",)

   This modules exports

**Module objects**

"""

import os

__all__ = ("detect_coverage",)


def detect_coverage() -> bool:
    """Running by coverage and running by unittest behavior differs!

    :returns: ``True`` if runner is coverage otherwise ``False``
    :rtype: bool

    .. seealso::

       `Detecting runner <https://stackoverflow.com/a/69994813>`_

    .. todo:: why coverage overrides logging.config?

       When run by coverage, logging level becomes logging.INFO
       When run by unittest, logging level is same as logging.config

       How to get the same behavior
    """
    return os.environ.get("COVERAGE_RUN", None) is not None

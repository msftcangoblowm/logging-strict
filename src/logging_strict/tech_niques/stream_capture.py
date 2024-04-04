"""
.. moduleauthor:: Dave Faulkmore <faulkmore telegram>

..

Context manager to capture streams stdout/stderr

Intuitive interface. Use within :code:`with` block

:py:class:`multiprocessing.pool.Pool` workers have to capture
both streams and logging output

Module private variables
-------------------------
.. py:data:: __all__
   :type: tuple[str]
   :value: ("CaptureOutput",)

   This modules exports

Module objects
---------------

"""

from __future__ import annotations

import io
import sys

__all__ = ("CaptureOutput",)


class CaptureOutput:
    def __enter__(self):
        """:pep:`343` with statement Context manager. For capturing
        - :py:data:`sys.stdout`
        - :py:data:`sys.stderr`

        :py:mod:`contextlib` has similiar functionality, but this is
        as one context manager instead of two

        :returns:

           class instance stores :py:data:`sys.stdout` and
           :py:data:`sys.stderr` initial state

        :rtype:

           logging_strict.tech_niques.stream_capture.CaptureOutput

        .. seealso::

           :pep:`20` Rule #1 Beautiful is better than ugly

        """
        self._stdout_output = ""
        self._stderr_output = ""

        self._stdout = sys.stdout
        sys.stdout = io.StringIO()

        self._stderr = sys.stderr
        sys.stderr = io.StringIO()

        return self

    def __exit__(self, *args):
        """Context Manager teardown. Restores sys.stdout and sys.stderr previous state

        :param exc_type: Exception type
        :type exc_type: type[Exception] | None
        :param exc_value: Exception value
        :type exc_value: typing.Any | None
        :param exc_tb: Exception traceback if an Exception occurred
        :type exc_tb: types.TracebackType | None
        """
        self._stdout_output = sys.stdout.getvalue()
        sys.stdout = self._stdout

        self._stderr_output = sys.stderr.getvalue()
        sys.stderr = self._stderr

    @property
    def stdout(self):
        """Getter of captured stdout

        :returns: Captured stdout
        :rtype: str
        """
        return self._stdout_output

    @property
    def stderr(self):
        """Getter of captured stderr

        :returns: Captured stderr
        :rtype: str
        """
        return self._stderr_output

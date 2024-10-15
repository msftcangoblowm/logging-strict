Stream capture
===============

.. automodule:: logging_strict.tech_niques.stream_capture
   :members:
   :private-members:
   :platform: Unix
   :synopsis: Context manager to capture streams stdout/stderr

   .. py:class:: CaptureOutput

      .. py:method:: __enter__(self) -> typing.Self

         :pep:`343` with statement Context manager. For capturing
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

      .. py:method:: __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, exc_tb: types.TracebackType | None) -> None

         Context Manager teardown. Restores sys.stdout and sys.stderr previous state

         :param exc_type: Exception type
         :type exc_type: type[BaseException] | None
         :param exc_value: Exception value
         :type exc_value: BaseException | None
         :param exc_tb: Exception traceback if an Exception occurred
         :type exc_tb: types.TracebackType | None

      .. py:property:: stdout(self) -> str

         Getter of captured stdout

         :returns: Captured stdout
         :rtype: str

      .. py:property:: stderr(self) -> str

         Getter of captured stderr

         :returns: Captured stderr
         :rtype: str

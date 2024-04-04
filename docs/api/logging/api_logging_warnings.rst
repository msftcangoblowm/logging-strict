.. _api_logging_warnings:

logging warnings
=================

.. _api_logging_warnings_capture_asyncio:

Capture asyncio
----------------

For async func/methods, :py:mod:`asyncio` allows ``0.1s`` after which
issues a (logging) warning. UI code is slow, so during UI code unittests,
these warnings often bleed thru. There is no way, providing by asyncio,
to simply turn off these warnings.

It's freak'n annoying!

The :py:mod:`asyncio` warnings are :py:func:`logging.warning`, not
warning.warn

How to handle :ref:`warning.warn messages <api_logging_warning_warn>`

How to specifically suppress asyncio logging.warning messages.

.. code-block:: text

   import unittest
   from logging_strict.tech_niques import captureLogs
   from asz.ui.textual.asz import ASZApp
   ...
   class SomeClass(unittest.IsolatedAsyncioTestCase)
       async def test_back_forth(self):
           app = ASZApp()
           async with app.run_test() as pilot:
               ...
               with captureLogs("asyncio", level="WARNING"):
                   await pilot.press(">")

   if __name__ == "__main__":  # pragma: no cover
       unittest.main(tb_locals=True)

The downside of this technique is has to be applied to all asyncio code.

.. seealso::

   :py:func:`logging_strict.tech_niques.captureLogs`

   tests.util.test_logging_capture.TestsLoggingCapture

.. _asyncio_logging_warnings_suppress:

Suppress logging warnings
~~~~~~~~~~~~~~~~~~~~~~~~~~

In each affected code module, which experiences
*asyncio logging warnings bleeding*, prevent all asyncio logging warnings
by setting the logging level beyond :py:data:`logging.WARNING` level

.. code-block:: python

    import logging

    # Supress asyncio logging.warning messages
    logging.getLogger("asyncio").setLevel(logging.ERROR)

When running :command:`coverage run && coverage report` should no longer
see these warnings. At least on screens and widgets where this technique
has been applied

After applying this technique, in affected unittests, can remove the
mitigation technique,
:py:func:`~logging_strict.tech_niques.captureLogs`

.. _api_logging_warning_warn:

warning.warn almost forgot
---------------------------

:py:mod:`warnings` are typically used for depreciation warnings.

.. testcode::

    import sys
    import warnings

    if not sys.warnoptions:
        warnings.simplefilter("ignore")

The above should suppress :py:func:`warnings.warn` messages, not
logging.warning messages.

Less common  to see warning.warn messages.

Indicates the package dependency is from a mature project that has gone
thru (major version) API breaking changes or usage depreciation.

Once a coder sees these warning messages, more likely than not would
quickly update code to use the newer usage syntax. Afterwards no warning
messages and therefore no need to suppress
warning.warn messages

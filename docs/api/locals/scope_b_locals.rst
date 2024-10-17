.. _api_locals_scope_b_locals_capture:

==============
Scope B locals
==============

When an Exception occurs the locals are available where the Exception
occurs, for that scope (scope A). Which is often within a unittest function.

Of course, once figure out where to debug, will need the locals within
that scope (scope B). Scope A and B are **always** different. To add
to the frustration, scope A locals are mostly really useless.

An advanced :py:mod:`unittest.mock` technique is used to patch a function
that has one return statement; not yield, not raises something.

All the nasty details are hidden. Can accomplish this in one function call,
:ref:`get_locals <code/tech_niques/context_locals:top>`

Function ``piggy_back``:

- signature: :code:`param_a: str` :code:`param_b: int = 10`

- locals: param_a, param_b

- returns ``"bar"``

Would like to know the locals key/value pairs and return value

.. code-block:: python

    from logging_strict.tech_niques import get_locals

    func_path = f'{__name__}.piggy_back'
    args = ("A",)
    kwargs = {}
    ret, d_locals = get_locals(func_path, piggy_back, *args, **kwargs)

    print(d_locals)
    print(ret)

.. code-block:: text

   {"param_a": "Hey A", "param_b": 30}
   "bar"

.. seealso::

   The piggy_back function is in unittest,
   ``/tests/tech_niques/test_docs_capture_traceback.py``

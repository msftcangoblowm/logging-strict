.. _api_locals_get_locals_dynamic:

Get at locals()
================

Dynamic execution context capture to retrieve local variables at runtime.

overview
---------

The :py:mod:`logging_strict.tech_niques.context_locals` module is designed for
debugging. Retrieve runtime :code:`locals()` in very hard to debug
situations; where the problem is occurring, not just later where the
test fails.

Operates by reading target callable's source code, rewriting, and
re-executing, using exec; not by runtime, avoids performance-heavy
tracing or frame inspection.

As a code debugging tool, use briefly to debug a coding issue. After finding
and fixing the bug, `get_locals_dynamic` is removed. Outside of code debugging
`get_locals_dynamic` is not used.

With both :py:func:`unittest.mock.patch` and
:py:func:`logging_strict.tech_niques.context_locals.get_locals_dynamic`
in your developer toolkit, an IDE is less necessary. Breakpoints and trace
hooks are necessary in only niche situations.

- No additional risk

  The function would have already been run unsuccessfully;
  Afterwards ``get_locals_dynamic`` is used to capture locals.
  The exact same execution occurs.

- Debugging-only use:

  Intended for test or debug contexts, afterwards is removed. Does not
  impact production, performance critical workflows, or carry any side
  effects

- Performance not a concern:

  Since it's used temporarily to diagnose issues, execution cost is acceptable.

- Single return requirement:

  Necessary for reliable AST transformation and variable tracking in
  rewritten code.

Time to refactor
-----------------

If a callable has either guard clauses or multiple return statements,
`get_locals_dynamic` will not work.

`get_locals_dynamic` **only requirement** is the target callable must have
only one return statement.

If the target callable has multiple return statements or guard clauses,
this is a great opportunity to refactor and get rid of those convenient,
but poor coding practices.

Guard clauses and multiple return statements advocates say this improves
code clarity. Not mentioned is that is comes at the expense of code being
harder to debug and the tests being more complicated. The benefits are
not worth the trade off.

To see this, compare examples with both code and respective tests. Assume
the code fails badly and without the ``locals()`` what's the cause is
impossible to discern.

In mypackage.mymodule_0

.. code-block:: text

   def do_something(): return "Nuts"
   def raise_valueerror(): ValueError("Hello")
   def raise_typeerror(): TypeError("World")

   def guard_clause(arg_0, arg_1, arg_2):
       x = 1
       if arg_1 is True: raise_valueerror()
       if arg_2 is True: raise_typeerror()
       if arg_0 is True: return

       try:
           z = do_something()
           y = x + a
       except Exception:
           return True
       else:
           return False

vs

In mypackage.mymodule_1

.. code-block:: text

   def do_something(): return "Nuts"
   def raise_valueerror(): ValueError("Hello")
   def raise_typeerror(): TypeError("World")

   def one_return(arg_0, arg_1, arg_2):
       x = 1
       if arg_1 is True:  # pragma: no branch
           raise_valueerror()
       if arg_2 is True:  # pragma: no branch
           raise_typeerror()
       if arg_0 is True:
           ret = None
       else:
           try:
               z = do_something()
           except Exception:
               ret = True
           else:
               ret = False
           y = x + a

       return ret

These callables are equivalent enough. So what are the benefits of one_return?
Cuz admittedly sacrificing code clarity. There's extra nesting and return variable.

Both contain the same hard to debug. Lets pretend we don't see the cause.

In tests/test_one_return_before.py

.. code-block:: python

    from unittest.mock import patch

    from mypackage.mymodule_1 import one_return


    def test_one_return_fails() -> None:
        """one_return fails do not receive locals"""
        arg_0 = True
        arg_1 = True
        arg_2 = True
        zz = 7
        with patch("mypackage.mymodule_1.raise_valueerror", return_value=None):
            with patch("mypackage.mymodule_1.raise_typeerror", return_value=None):
                ret = one_return(arg_0, arg_1, arg_2)
                assert zz is None

If for some inexplicable reason the code gets to the assert line,
traceback will not include the ``locals()`` within one_return.

In tests/test_one_return_after.py

.. code-block:: python

    from unittest.mock import patch

    from logging_strict.tech_niques.context_locals import get_dynamic_locals

    from mypackage.mymodule_1 import one_return


    def test_one_return_fails() -> None:
        """one_return fails do not receive locals"""
        arg_0 = True
        arg_1 = True
        arg_2 = True
        zz = 7
        with patch("mypackage.mymodule_1.raise_valueerror", return_value=None):
            with patch("mypackage.mymodule_1.raise_typeerror", return_value=None):
                args = (arg_0, arg_1, arg_2)
                kw = {}
                t_ret = get_dynamic_locals(one_return, *args, **kw)
                ret, d_locals_one_return = t_ret
                assert zz is None

As the assert fails, we will see ``d_locals_one_return``. During the test
the runtime performance impact is negligible. After finding the bug,
revert back to ``tests/test_one_return_before.py``.

mypackage.mymodule_1.guard_clause only chance at the ``locals()`` is performance
heavy frame inspection or trace hooks.

realistic situation
""""""""""""""""""""

SQLAlchemy UDF(s) are loaded but some fail to load. A query
that needs one of the missing UDF fails to find the UDF. Determining
why the UDF failed to load cannot be determined after the query fails.

the UDF load occurs way before the query. The test traceback will not
include the UDF load ``locals()``.

Refactor recommendations
--------------------------

Well written code is debuggable and has simpler tests. Here are
recommendations on how to write testable code?

Callable
"""""""""

Module level function, classmethod, and staticmethod are all callables.

lambda and partial are also callable; these can easily be refactored
into module level functions.

module level function is already testable. The surprise is that
classmethod and staticmethod don't need to be refactored to be testable.

Class instance method
""""""""""""""""""""""

Class instance method body can be refactored. Place within a module
level function that accepts either the class instance **or**
:py:class:`types.SimpleNamespace`.

The class instance calls the module level function.

The module level function 1st arg named ``self`` would
raise a few eyebrows. Thus the naming convention is ``inst``. This
carries the additional connotation that accepts both ``self`` and
:py:class:`types.SimpleNamespace`.

In tests, :py:class:`types.SimpleNamespace` mocks the class instance
attributes. Passing the class instance has almost no additional benefit.
The call to the module level function should be exactly equivalent to
call to the class instance method.

If the class instance method would need to call other class instance methods.
Well those were refactored into testable module level functions too!

The class becomes an empty shell providing scaffolding with accessible
public facing documentation. Whereas the module level function documentation
can focus on implementation concerns.

Unsupported
""""""""""""

2-4 simply lack support, not that support couldn't be added.

Of the three, adding support for async functions is the most important.

1. Source code is not available for: ``.pyc`` files or frozen executables

2. Decorated functions

3. Async functions

4. Closures or nested functions

5. lambda, partial

Impact on other tools
----------------------

Being able to inspect other context's locals enhances development and
makes testing easier. Once the problem is resolved, ``get_locals_dynamic``
is removed. So there are no side-effects. that would impact:

- profilers

- coverage tools

- other debuggers

If other debuggers were pulling their weight ``get_locals_dynamic``
wouldn't be necessary.

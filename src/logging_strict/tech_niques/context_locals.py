"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Want desired context's locals
------------------------------

From a module function, **get the locals** and return value

When testing and an Exception occurs, the locals are only available in
the context of where the error occurred, not necessarily where need to
debug.

.. epigraph::

   As you read this, keep in mind

   To understand our motivation, how badly we want to see those locals,
   background on those locals:

   - param_a -- Satoshi Nakamoto's private key to the genesis block

   - param_b -- the passphrase to that private key

   ^^ is exactly how it feels when don't have access to those locals and
   then suddenly do!

   -- Betty White <-- everything is attributed to her

Limited to:

- module function; not a: class method, Generator, Iterator, or Iterable

- function must end in a single ``return`` statement; not ``yield``,
  ``yield from``, or ``raise``

And wait! There's more
^^^^^^^^^^^^^^^^^^^^^^^^^

In return, value can be: normal or **tuple (packed values)**

Wow!

Great!

Yea!

One return value example
-------------------------

Example function found in :py:mod:`logging_strict.tech_niques.context_locals`.
Lets pretend this is the module level function would like to see the locals

.. code-block:: text

   def _func(param_a: str, param_b: Optional[int] = 10) -> str:
       param_a = f"Hey {param_a}"  # Local only
       param_b += 20  # Local only
       return "bar"


So there are two locals we'd really really like to see:

- param_a
- param_b

Returns ``"bar"``

.. testcode::

    from logging_strict.tech_niques.context_locals import get_locals, _func


    def main():
        # If in same script file try, f"{__name__}._func"
        func_path = f"logging_strict.tech_niques.context_locals._func"

        args = ("A",)
        kwargs = {}
        t_ret = get_locals(func_path, _func, *args, **kwargs)
        ret, d_locals = t_ret
        assert ret == "bar"
        assert "param_a" in d_locals.keys()
        assert "param_b" in d_locals.keys()
        print(d_locals)


    main()

.. testoutput::

   {'param_a': 'Hey A', 'param_b': 30}

Woooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo-
oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooah!

.. note:: pretty print is your friend

   For better readability, :py:func:`pprint.pprint` is better than
   :py:func:`print`

.. note:: ``__name__`` is also your friend

   This technique requires the absolute dotted path to the module
   function. **if** in the same (python script) file, use
   :code:`f"{__name__}.myfunc"` instead.

   Useful knowhow, if the module function is in the same file as a unittest

.. caution:: Especially applies to JSON

   tl;dr;

   In a str, preserve escape characters, use raw string, e.g. r"\\\\\\\\n"

   "\\\\\\\\n" --> "\\\\n"

   Unpreserved, ^^ may happen

   Escape characters need to be preserved. JSON str is an example where
   a raw string would preserve the escaped characters and remain valid JSON.

.. seealso::

   `Credit <https://stackoverflow.com/a/56469201>`_


**Module private variables**

.. py:data:: __all__
   :type: tuple[str]
   :value: ("get_locals",)

   This modules exports

.. py:data:: _T
   :type: typing.TypeVar
   :value: typing.TypeVar("_T")

   Equivalent to :py:data:`~typing.Any`

.. py:data:: _P
   :type: typing.ParamSpec
   :value: typing_extensions.ParamSpec('_P')

   Equivalent to :py:data:`~typing.Any`

**Module objects**

"""

from __future__ import annotations

import inspect
import re
import sys
from textwrap import dedent
from typing import (
    Any,
    Callable,
    TypeVar,
)
from unittest.mock import (
    MagicMock,
    patch,
)

from logging_strict.util.check_type import is_not_ok

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

__all__ = ("get_locals",)

_T = TypeVar("_T")  # Can be anything
_P = ParamSpec("_P")


def _func(param_a: str, param_b: int | None = 10) -> str:
    """Sample function to inspect the locals

    :param param_a: To whom am i speaking to? Name please
    :type param_a: str
    :param param_b: Default 10. A int to be modified
    :type param_b: int | None
    :returns: Greetings from this function to our adoring fans
    :rtype: str
    """
    if is_not_ok(param_a):
        param_a = ""
    else:  # pragma: no cover
        pass

    if param_b is None or not isinstance(param_b, int):
        param_b = 10
    else:  # pragma: no cover
        pass

    param_a = f"Hey {param_a}"  # Local only
    param_b += 20  # Local only

    return "bar"


class MockFunction:
    """Defines a Mock, for functions, to explore the execution details.

    :var func: Function to mock
    :vartype func: collections.abc.Callable[..., typing.Any]

    .. seealso::

       Used by :py:func:`logging_strict.tech_niques.get_locals`

    """

    def __init__(self, func: Callable[..., Any]) -> None:
        """Class constructor"""
        self.func = func

    def __call__(  # type: ignore[misc]  # missing self non-static method
        mock_instance: MagicMock,
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> Any:
        """Mock modifies a target function.
        The locals are included into the :paramref:`mock_instance`.
        Return value passes through

        Must use on a function with a single return value. Not yield or raise.

        :param mock_instance:

           A generic module level function. Is modified and executed. piggy backing
           the module level function ``locals`` onto the return statement

        :type mock_instance: collections.abc.Callable[logging_strict.tech_niques.context_locals._P, logging_strict.tech_niques.context_locals._T]
        :param args: Generic positional args
        :type args: logging_strict.tech_niques.context_locals._P.args
        :param kwargs: Generic keyword args
        :type kwargs: logging_strict.tech_niques.context_locals._P.kwargs
        :returns:

            Module levels function normal return value

        :rtype: logging_strict.tech_niques.context_locals._T

        .. seealso::

           :py:class:`typing.ParamSpec`

        """
        # Modify ``return`` statement, to include ``locals()``. Returns a tuple
        code = re.sub(
            "[\\s]return\\b",
            " return locals(), ",
            dedent(inspect.getsource(mock_instance.func)),
        )

        # Modify to call the modified function
        # code = code + f"\nloc, ret = {mock_instance.func.__name__}(*args, **kwargs)"
        support_return_tuple = (
            f"\nt_ret = {mock_instance.func.__name__}(*args, **kwargs)\n"
            "loc = t_ret[0]\n"
            "ret = t_ret[1] if len(t_ret[1:]) == 1 else t_ret[1:]"
        )
        code += support_return_tuple

        # Execute the modified function code passing in the params
        loc = {"args": args, "kwargs": kwargs}
        exec(code, mock_instance.func.__globals__, loc)

        # Put execution locals into mock instance. ``l`` is locals variable name
        for locals_name, locals_val in loc["loc"].items():  # type: ignore[attr-defined]
            setattr(mock_instance, locals_name, locals_val)

        # Return normal return value as if nothing was ever modified
        return loc["ret"]


def get_locals(
    func_path,
    func,
    /,
    *args,
    **kwargs,
):
    """Uses :py:func:`patch <unittest.mock.patch>` to retrieve the
    tested functions locals and return value!

    See this module docs for example

    Limitation: the function must end with a single ``return``, not
    ``yield`` or ``raise``.

    :param func_path: dotted path to func
    :type func_path: str
    :param func: The func
    :type func: collections.abc.Callable[..., typing.Any]
    :param args: Positional arguments
    :type args: typing.ParamSpecArgs
    :param kwargs: Optional (keyword) arguments
    :type kwargs: typing.ParamSpecKwargs
    :returns: Tuple containing return value and the locals
    :rtype: tuple[logging_strict.tech_niques.context_locals._T, dict[str, typing.Any]]
    """
    with patch(
        func_path,
        autospec=True,
        side_effect=MockFunction(func),
    ) as mocked:
        # mocked type is function
        ret = mocked(*args, **kwargs)
        # print(inspect.getmembers(mocked.side_effect))
        d_locals = {}
        for k, v in mocked.side_effect.__dict__.items():
            if k != "func":
                d_locals[k] = v

        return ret, d_locals

"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Must know technique for peering into the function under test and inspecting
the functions locals

"""

from __future__ import annotations

import unittest

from logging_strict.constants import g_app_name
from logging_strict.tech_niques.context_locals import (
    _func,
    get_locals,
)
from logging_strict.util.check_type import is_not_ok


def piggy_back(
    param_a: str,
    param_b: int | None = 10,
) -> str:
    """Example module level function that has locals and returns something

    :param param_a: A positional argument
    :type param_a: str
    :param param_b: Default 10. A kwarg argument
    :type param_b: int | None
    :returns: Literal ``"bar"``
    :rtype: str

    :raises:

       - :py:exc:`TypeError` -- Tripped when signature is inspected.
         param_a is ``None``, positional arg required. Or param_a is
         unsupported type


    .. note::

       This module level function is for illustrative purposes

       Although defensive coding techniques are used to protect against
       unsupported types and the signature params annotations could be
       changed to :py:class:`~typing.Any`, purposefully unaltered

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


class CaptureLocals(unittest.TestCase):
    """Super useful testing algo to get all local variables values"""

    def test_capture_locals(self):
        """Capture locals from a module-level function, not where exception occurs

        :py:func:`.piggy_back` is used as an example function.

        If placed into a script, this technique also works outside of unittest context
        """
        # module level function only for illustrative purposes
        valids = (
            (piggy_back, f"{__name__}.piggy_back"),
            (_func, f"{g_app_name}.tech_niques.context_locals._func"),
        )

        # param_a cannot be ``()``
        values = (
            (("A",), {}, "Hey A", "bar"),
            (("",), {}, "Hey ", "bar"),
            (("B",), {"param_b": 0.12345}, "Hey B", "bar"),
        )
        for func, func_path in valids:
            for args, kwargs, param_a_expected, ret_expected in values:
                ret, d_locals = get_locals(func_path, func, *args, **kwargs)
                self.assertIsInstance(ret, str)
                self.assertIsInstance(d_locals, dict)
                self.assertIn("param_a", d_locals)
                self.assertIn("param_b", d_locals)
                self.assertEqual(d_locals["param_a"], param_a_expected)
                self.assertEqual(d_locals["param_b"], 30)
                self.assertEqual(ret, ret_expected)
                # Call directly so coverage has something to do
                func(*args, **kwargs)

        for func, func_path in valids:
            values = (
                ((), {}, "Hey ", "bar"),  # missing a required argument: 'param_a'
                ((1.1), {}, "Hey ", "bar"),
            )
            for args, kwargs, param_a_expected, ret_expected in values:
                with self.assertRaises(TypeError):
                    get_locals(func_path, func, *args, **kwargs)
                    # Call directly so coverage has something to do
                    func(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    """
    .. code-block:: shell

       python -m tests.tech_niques.test_context_locals

       coverage run --data-file=".coverage-combine-3" \
       -m unittest discover -t. -s tests -p "test_context_locals*.py"

       coverage report --data-file=".coverage-combine-3" \
       --no-skip-covered --include="*context_locals*"

    """
    unittest.main(tb_locals=True)

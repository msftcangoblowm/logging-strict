"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Must know technique for peering into the function under test and inspecting
the functions locals

"""

import unittest
from contextlib import nullcontext as does_not_raise
from functools import partial
from pathlib import PurePath
from types import (
    FunctionType,
    ModuleType,
)
from typing import (
    TYPE_CHECKING,
    cast,
)
from unittest.mock import patch

from logging_strict.tech_niques import (
    FuncWrapper,
    get_locals,
    get_locals_dynamic,
)
from logging_strict.tech_niques.context_locals import (
    _func,  # pyright: ignore[reportPrivateUsage]  # fmt: skip
)
from logging_strict.util.check_type import is_not_ok
from logging_strict.util.util_root import IsRoot

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager
    from typing import Any

    from typing_extensions import TypeAlias

    DOES_NOT_OR_DOES: TypeAlias = (
        does_not_raise[None] | AbstractContextManager[TypeError, bool | None]
    )


def piggy_back(param_a: str, param_b: "int | None" = 10) -> str:
    """Example module level function that has locals and returns something

    Careful! In function signature, do not use ``|``. Results in
    impossible to track down ImportError

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

    if param_b is None or not isinstance(param_b, int):  # pyright: ignore[reportUnnecessaryIsInstance]  # fmt: skip
        param_b = 10
    else:  # pragma: no cover
        pass

    param_a = f"Hey {param_a}"  # Local only
    param_b += 20  # Local only

    return "bar"


class CaptureLocals(unittest.TestCase):
    """Super useful testing algo to get all local variables values"""

    def test_capture_locals(self) -> None:
        """Capture locals from a module-level function, not where exception occurs

        :py:func:`.piggy_back` is used as an example function.

        If placed into a script, this technique also works outside of unittest context
        """
        if TYPE_CHECKING:
            func_path: str
            func: Callable[..., Any]
            fcns: list[tuple[Callable[..., Any], str]]
            args: tuple[Any] | float
            kwargs: dict[Any, Any]
            expectation: DOES_NOT_OR_DOES
            param_a_expected: str
            ret_expected: str
            valids: tuple[
                tuple[tuple[Any] | float, dict[Any, Any], DOES_NOT_OR_DOES, str, str],
                ...,
            ]

        # module level function only for illustrative purposes
        fcns = []
        #    no longer need to hardcode func dotted path
        fw_0 = FuncWrapper(cast("FunctionType", piggy_back))
        fcns.append((piggy_back, fw_0.get_dotted_path()))
        fw_1 = FuncWrapper(cast("FunctionType", _func))
        fcns.append((_func, fw_1.get_dotted_path()))

        # param_a cannot be ``()``
        valids = (
            (("A",), {}, cast("DOES_NOT_OR_DOES", does_not_raise()), "Hey A", "bar"),
            (("",), {}, cast("DOES_NOT_OR_DOES", does_not_raise()), "Hey ", "bar"),
            (
                ("B",),
                {"param_b": 0.12345},
                cast("DOES_NOT_OR_DOES", does_not_raise()),
                "Hey B",
                "bar",
            ),
            # missing a required argument: 'param_a'
            (
                cast("tuple[Any]", ()),
                {},
                cast("DOES_NOT_OR_DOES", self.assertRaises(TypeError)),
                "Hey ",
                "bar",
            ),
            (
                1.1,
                {},
                cast("DOES_NOT_OR_DOES", self.assertRaises(TypeError)),
                "Hey ",
                "bar",
            ),
        )
        for func, func_path in fcns:
            for args, kwargs, expectation, param_a_expected, ret_expected in valids:
                with expectation:
                    t_out = get_locals(
                        func_path,
                        func,
                        *args,  # type: ignore[misc]
                        **kwargs,
                    )
                if isinstance(expectation, does_not_raise):
                    ret, d_locals = t_out
                    self.assertIsInstance(ret, str)
                    self.assertIsInstance(d_locals, dict)
                    self.assertIn("param_a", d_locals)
                    self.assertIn("param_b", d_locals)
                    self.assertEqual(d_locals["param_a"], param_a_expected)
                    self.assertEqual(d_locals["param_b"], 30)
                    self.assertEqual(ret, ret_expected)
                    # Call directly so coverage has something to do
                    func(
                        *args,  # type: ignore[misc]
                        **kwargs,
                    )

    def test_get_locals_dynamic_module_function(self) -> None:
        """Get locals of a module function. Without func_path"""
        if TYPE_CHECKING:
            valids: tuple[
                tuple[tuple[Any] | float, dict[Any, Any], DOES_NOT_OR_DOES, str, str],
                ...,
            ]
            kwargs_1: dict[Any, Any]
            kwargs_2: dict[Any, Any]

        fcns = (piggy_back, _func)
        valids = (
            (("A",), {}, cast("DOES_NOT_OR_DOES", does_not_raise()), "Hey A", "bar"),
            (("",), {}, cast("DOES_NOT_OR_DOES", does_not_raise()), "Hey ", "bar"),
            (
                ("B",),
                {"param_b": 0.12345},
                cast("DOES_NOT_OR_DOES", does_not_raise()),
                "Hey B",
                "bar",
            ),
            # missing a required argument: 'param_a'
            (
                cast("tuple[Any]", ()),
                {},
                cast("DOES_NOT_OR_DOES", self.assertRaises(TypeError)),
                "Hey ",
                "bar",
            ),
            (
                1.1,
                {},
                cast("DOES_NOT_OR_DOES", self.assertRaises(TypeError)),
                "Hey ",
                "bar",
            ),
        )
        for func_0 in fcns:
            for args_0, kwargs_0, expectation, param_a_expected, ret_expected in valids:
                with expectation:
                    t_out = get_locals_dynamic(
                        func_0,
                        *args_0,  # type: ignore[misc]
                        **kwargs_0,
                    )
                if isinstance(expectation, does_not_raise):
                    self.assertIsInstance(t_out, tuple)
                    self.assertEqual(len(t_out), 2)
                    ret, d_locals = t_out
                    self.assertIsInstance(ret, str)
                    self.assertIsInstance(d_locals, dict)
                    self.assertIn("param_a", d_locals)
                    self.assertIn("param_b", d_locals)
                    self.assertEqual(d_locals["param_a"], param_a_expected)
                    self.assertEqual(d_locals["param_b"], 30)
                    self.assertEqual(ret, ret_expected)

        # staticmethod
        func_1 = IsRoot.is_root
        args_1 = cast("tuple[Any]", ())
        kwargs_1 = {}
        expectation = cast("DOES_NOT_OR_DOES", does_not_raise())
        with expectation:
            t_out = get_locals_dynamic(
                cast("Callable[..., Any]", func_1),
                *args_1,
                **kwargs_1,
            )
            meth_ret, meth_locals = t_out  # pyright: ignore[reportUnusedVariable]
            locals_ret_actual = meth_locals["ret"]
            locals_ret_type_expected = bool
            self.assertIsInstance(locals_ret_actual, locals_ret_type_expected)

        # classmethod
        func_2 = IsRoot.path_home_root
        args_2 = ()
        kwargs_2 = {}
        expectation = does_not_raise()
        with expectation:
            t_out = get_locals_dynamic(
                cast("Callable[..., Any]", func_2),
                *args_2,
                **kwargs_2,
            )
            meth_ret, meth_locals = t_out  # pyright: ignore[reportUnusedVariable]
            self.assertTrue(issubclass(type(meth_locals["ret"]), PurePath))

    def test_func_wrapper(self) -> None:
        """Test class FuncWrapper"""
        # func created with :py:func:`functools.partial`
        fcns = (
            (piggy_back, "piggy_back"),
            (_func, "_func"),
        )
        expectation = does_not_raise()
        args = ("A",)
        for func_0, full_name_expected in fcns:
            func_1 = cast("Callable[..., Any]", partial(func_0, *args))
            with expectation:
                fw_0 = FuncWrapper(func_1)
            if isinstance(expectation, does_not_raise):
                # None on py39. But not consistent
                # py310 '/home/faulkmore/.pyenv/versions/3.10.14/lib/python3.10/functools.py'
                module_filename = fw_0.module_filename
                if module_filename is not None:
                    self.assertIsInstance(module_filename, str)

                # Had to normalize the behavior.
                #     None on py39 empty str on py310+
                package_name = fw_0.package_name
                self.assertIsInstance(package_name, str)

                root_package_name = fw_0.root_package_name
                self.assertIsInstance(root_package_name, str)

                full_name_actual = fw_0.full_name
                self.assertEqual(full_name_actual, full_name_expected)

            # module not found --> None
            expectation_2 = does_not_raise()
            with patch("inspect.getmodule", return_value=None):
                with expectation_2:
                    fw_2 = FuncWrapper(func_1)
                    self.assertIsNone(fw_2.module_name)
                    self.assertIsNone(fw_2.module_filename)
                    self.assertEqual(fw_2.package_name, "")
                    self.assertEqual(fw_2.root_package_name, "")
                with self.assertRaises(ModuleNotFoundError):
                    fw_2.get_dotted_path()

        # str.join
        FuncWrapper(str.join)
        FuncWrapper(int.__add__)
        FuncWrapper(set().union)
        # unbound method aka Classmethod
        fw_1 = FuncWrapper(unittest.TestCase.setUpClass)
        self.assertIsNotNone(fw_1.cls_name)
        self.assertIsInstance(fw_1.cls_name, str)
        module_1 = fw_1.module
        self.assertIsInstance(module_1, ModuleType)
        module_name_1 = fw_1.module_name
        self.assertIsInstance(module_name_1, str)
        module_filename_1 = fw_1.module_filename
        self.assertIsInstance(module_filename_1, str)
        self.assertIsInstance(fw_1.package_name, str)
        self.assertIsInstance(fw_1.root_package_name, str)
        self.assertIsInstance(fw_1.full_name, str)
        self.assertIsInstance(fw_1.get_dotted_path(), str)


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

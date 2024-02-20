import unittest

from logging_strict import LoggingYamlType
from logging_strict.logging_api import LoggingConfigYaml
from logging_strict.tech_niques import (
    ClassAttribTypes,
    is_class_attrib_kind,
)


class UncategorizedTricks(unittest.TestCase):
    def test_is_classmethod(self):
        """For testing ABC registering"""
        # These classmethods are required by the ABC's interface
        self.assertTrue(
            is_class_attrib_kind(
                LoggingConfigYaml,
                "extract",
                ClassAttribTypes.METHOD,
            ),
        )
        self.assertTrue(
            is_class_attrib_kind(
                LoggingConfigYaml,
                "file_name",
                ClassAttribTypes.PROPERTY,
            ),
        )
        self.assertTrue(
            is_class_attrib_kind(
                LoggingConfigYaml,
                "setup",
                ClassAttribTypes.METHOD,
            ),
        )
        self.assertTrue(
            is_class_attrib_kind(
                LoggingConfigYaml,
                "as_str",
                ClassAttribTypes.METHOD,
            ),
        )

        self.assertTrue(issubclass(LoggingConfigYaml, LoggingYamlType))

        # not a class
        with self.assertRaises(AssertionError):
            is_class_attrib_kind(
                42,
                "file_name",
                ClassAttribTypes.PROPERTY,
            )

        # method name not a str
        invalids = (
            None,
            0.12345,
            42,
        )
        for invalid in invalids:
            with self.assertRaises(TypeError):
                is_class_attrib_kind(
                    LoggingConfigYaml,
                    invalid,
                    ClassAttribTypes.PROPERTY,
                )


if __name__ == "__main__":  # pragma: no cover
    """
    .. code-block:: shell

       python -m tests.ui.test_uncategorized_underappreciated --locals

       coverage run --data-file=".coverage-combine-42" \
       -m unittest discover -t. -s tests/tech_niques \
       -p "test_uncategorized_underappreciated*.py" --locals

       coverage report --include="**/tech_niques/__init__*" --no-skip-covered \
       --data-file=".coverage-combine-42"

       coverage report --data-file=".coverage-combine-42" --no-skip-covered

    """
    unittest.main(tb_locals=True)

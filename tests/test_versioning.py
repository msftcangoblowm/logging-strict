"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Rolled my own semantic versioning module rather than using package, packaging.

Was ported from/to logging-strict and drain-swamp. Not DRY at all.
drain-swamp implementation is more up-to-date. drain-swamp is not a base package,
so consider versioning as vendored.

``packaging`` has built-in design issue of differentiating between prerelease
and non-prerelease versions. The maintainers know this is a problem. Would
take a very brave soul to both understand the problem and rewrite the
entire package.

.. py:data:: testdata_v
   :type tuple[tuple[str, str]]

   Demonstrate removing prepended ``v`` in semantic version str.
   Both logging-strict and drain-swamp downplay prepending a ``v``

"""

import unittest

from logging_strict import LoggingConfigCategory
from logging_strict._version import (
    __version__,
    __version_tuple__,
)
from logging_strict.constants import g_app_name
from logging_strict.version_semantic import (
    Version,
    _map_release,
    get_version,
    readthedocs_url,
    remove_v,
    sanitize_tag,
)

testdata_v = (
    ("v1.0.1", "1.0.1"),
    ("0!v1.0.1", "0!1.0.1"),
    ("1!v1.0.1", "1!1.0.1"),
    ("0!v1.0.1+g4b33a80.d20240129", "0!1.0.1+g4b33a80.d20240129"),
    ("1!v1.0.1+g4b33a80.d20240129", "1!1.0.1+g4b33a80.d20240129"),
    ("v0.1.1.dev0+g4b33a80.d20240129", "0.1.1.dev0+g4b33a80.d20240129"),
    ("v0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0+g4b33a80.d20240129"),
    ("v0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1.a1dev1+g4b33a80.d20240129"),
    ("v0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1.alpha1dev1+g4b33a80.d20240129"),
    ("v0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1.b1dev1+g4b33a80.d20240129"),
    ("v0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1.beta1dev1+g4b33a80.d20240129"),
    ("v0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1.rc1dev1+g4b33a80.d20240129"),
)


class PackageVersioning(unittest.TestCase):
    """Test semantic versioning functionality. drain-swamp is more definitive."""

    def setUp(self):
        """Provide semantic versioning data to test against."""
        self.vals = (
            (
                (0, 0, 1),
                {"releaselevel": "alpha", "serial": 0, "dev": 0},
                "0.0.1a0",
            ),
            (
                (0, 0, 1),
                {"releaselevel": "beta", "serial": 0, "dev": 0},
                "0.0.1b0",
            ),
            (
                (0, 0, 1),
                {"releaselevel": "candidate", "serial": 0, "dev": 0},
                "0.0.1rc0",
            ),
            (
                (0, 0, 1),
                {"releaselevel": "", "serial": 0, "dev": 0},
                "0.0.1",
            ),
            (
                (0, 0, 1),
                {"releaselevel": "alpha", "serial": 3, "dev": 10},
                "0.0.1a3.dev10",
            ),
            (
                (0, 0, 1),
                {"releaselevel": "post", "serial": 3, "dev": 0},
                "0.0.1post3",
            ),
        )
        self.valids = (
            ("0.0.1", "0.0.1"),  # tagged final version
            ("0.1.1.dev0+g4b33a80.d20240129", "0.1.1.dev0"),
            ("0.1.1.dev1+g4b33a80.d20240129", "0.1.1.dev1"),
            ("0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0"),
            ("0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
            ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
            ("0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
            ("0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
            ("0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),
        )
        self.invalids = (("0.1.1.candidate1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),)

    def test_advertised_version_and_url(self):
        """Check excepted versions and url occur"""
        for v_in, v_expected in self.valids:
            v_actual = sanitize_tag(v_in)
            self.assertEqual(v_actual, v_expected)
            self.assertIn(v_actual, readthedocs_url(g_app_name, ver_=v_in))

    def test_setuptools_scm_version_file(self):
        """Autogenerated file by setuptools-scm"""
        if len(__version_tuple__) == 3:
            # 0.0.1
            ver = list(__version_tuple__)
            ver_short = ".".join(map(str, ver))
            ver_long = ver_short

            #    0.0.1.post1 --> __version_tuple__ does not contain post1
            #    remove post release
            version_actual = __version__.split(".post")[0]

            self.assertEqual(version_actual, f"{ver_long}")
        else:
            # 0.0.1a1.dev8
            ver = list(__version_tuple__[:3])
            ver_short = ".".join(map(str, ver))
            ver_dev = __version_tuple__[3]
            # ver_git = __version_tuple__[-1]
            ver_long = f"{ver_short}"
            if len(ver_dev) != 0:
                ver_long += f".{ver_dev}"

            # If no tags ver_git will not match, ignore (version) local
            # Will fail '0.0.1a1.post1.dev8' __version_tuple__ does not contain post1
            if ".post" not in __version__:
                left_side = sanitize_tag(__version__)
                right_side = sanitize_tag(ver_long)
                self.assertEqual(left_side, right_side)

    def test_sanitize_tag(self):
        """Convert repo version --> semantic version"""
        for v_in, v_expected in self.valids:
            v_actual = sanitize_tag(v_in)
            self.assertEqual(v_actual, v_expected)

        # candidate not recognized
        for v_in, v_expected in self.invalids:
            with self.assertRaises(ValueError):
                sanitize_tag(v_in)

        # Strip epoch and locals
        valids = (
            ("1!1.0.1a1.dev1", "1.0.1a1.dev1"),
            ("1.0.1a1.dev1+4b33a80.4b33a80", "1.0.1a1.dev1"),
        )
        for orig, expected in valids:
            actual = sanitize_tag(orig)
            self.assertEqual(actual, expected)

    def test_get_version(self):
        """Used for display only. Allows release level, final"""
        # Flip the logic backwards
        finals = (
            None,
            0.12345,  # unsupported type
            False,
        )
        for final in finals:
            for args, kwargs, actual in self.vals:
                expect_info, expect_dev = get_version(
                    actual,
                    is_use_final=final,
                )
                self.assertEqual(kwargs["dev"], expect_dev)
                self.assertEqual(kwargs["serial"], expect_info[-1])
                if len(kwargs["releaselevel"]) == 0:
                    self.assertEqual(len(expect_info[-2]), 0)
                else:
                    self.assertEqual(kwargs["releaselevel"], expect_info[-2])
                self.assertEqual(args, expect_info[:3])

        # Allow final
        actual = "1.0.1"
        l_actual = actual.split(".")
        l_actual2 = map(int, iter(l_actual))
        t_actual = tuple(l_actual2)
        expect_info, expect_dev = get_version(
            actual,
            is_use_final=True,
        )
        self.assertEqual(0, expect_dev)
        self.assertEqual(0, expect_info[-1])
        self.assertEqual("final", expect_info[-2])
        self.assertEqual(t_actual, expect_info[:3])

        # Has both dev and is a prerelease
        dev_pres = (
            ("0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
            ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1a1.dev1"),
            ("0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
            ("0.1.1.beta1dev1+g4b33a80.d20240129", "0.1.1b1.dev1"),
            ("0.1.1.rc1dev1+g4b33a80.d20240129", "0.1.1rc1.dev1"),
        )

        for dev_pre in dev_pres:
            expected = sanitize_tag(dev_pre[1])
            expect_info, expect_dev = get_version(expected)

            v = Version(expected)

            v_pre = v.pre
            v_pre_is = v.is_prerelease
            v_dev = v.dev

            # long format
            pre = expect_info[-2]
            self.assertIn(pre, _map_release.keys())

            found_k = None
            for k, v in _map_release.items():
                if pre == k:
                    found_k = k

            self.assertEqual(expect_dev, v_dev)

            self.assertIsNotNone(found_k)
            # pre is long format. So ``alpha`` rather than ``a``
            self.assertEqual(pre, found_k)

        # Has dev and no releaselevel
        dev_pres = (
            ("0.1.1.a1dev1+g4b33a80.d20240129", "0.1.1.dev1"),
            ("0.1.1.alpha1dev1+g4b33a80.d20240129", "0.1.1.dev0"),
            ("0.1.1.b1dev1+g4b33a80.d20240129", "0.1.1dev8"),
        )
        for dev_pre in dev_pres:
            expected = sanitize_tag(dev_pre[1])
            expect_info, expect_dev = get_version(expected)

            v = Version(expected)

            v_pre = v.pre
            v_pre_is = v.is_prerelease
            v_dev = v.dev
            self.assertEqual(expect_dev, v_dev)
            self.assertIsNone(v_pre)

        # post only
        dev_pres = (
            ("0.1.1.post0+g4b33a80.d20240129", "0.1.1.post0", 0),
            ("0.1.1.post8", "0.1.1.post8", 8),
            ("0.1.1.post5", "0.1.1post5", 5),
        )
        for dev_pre in dev_pres:
            expected_post = dev_pre[2]
            expected = sanitize_tag(dev_pre[1])
            expect_info, expect_dev = get_version(expected)

            v = Version(expected)

            v_post = v.post
            v_post_is = v.is_postrelease
            v_pre_is = v.is_prerelease
            self.assertTrue(v_post_is)
            self.assertFalse(v_pre_is)
            self.assertEqual(v_post, expected_post)
            self.assertEqual(expect_info[-2], "post")

    def test_v_remove(self):
        """Test function remove_v"""
        for v_in, expected in testdata_v:
            actual = remove_v(v_in)
            self.assertEqual(actual, expected)

    def test_readthedocs_package_name(self):
        """test get rtd url given package name and semantic version str"""
        testdata_package_name = (
            ("this-that"),
            ("this_that"),
        )
        ver_ = (
            None,
            "latest",
            "0.0.1",
        )
        for package_name in testdata_package_name:
            for ver in ver_:
                str_url = readthedocs_url(package_name, ver_=ver)
                protocol_len = len("https://")
                uri = str_url[protocol_len:]
                package_name = uri.split(".")[0]
                self.assertNotIn("_", package_name)


class EnhancedEnumFeature(unittest.TestCase):
    """Test Generator LoggingConfigCategory.categories"""

    def test_enum_values(self):
        """LoggingConfigCategory is types of logging config YAML files"""
        gen = LoggingConfigCategory.categories()
        # execute Generator
        values = list(gen)

        # verify
        self.assertIn("worker", values)
        self.assertIn("app", values)
        self.assertGreaterEqual(len(values), 2)


if __name__ == "__main__":  # pragma: no cover
    """
    w/o coverage

    .. code-block:: shell

       python -m unittest tests.test_versioning --locals

       python -m unittest tests.test_versioning \
       -k PackageVersioning.test_get_version --locals --buffer

       python -m unittest tests.test_versioning \
       -k PackageVersioning.test_sanitize_tag --locals --buffer

    W/ coverage

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-31" \
       -m unittest discover -t. -s tests -p "test_versioning*.py" --locals

       coverage report --data-file=".coverage-combine-31" --no-skip-covered \
       --include="**/logging_strict/constants*"

       coverage report --data-file=".coverage-combine-31" --no-skip-covered \
       --include="**/logging_strict/*_version*"

    """
    unittest.main(tb_locals=True)

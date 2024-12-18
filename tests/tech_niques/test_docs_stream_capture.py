"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Demonstrate technique to capture steams using context manager,
:py:class:`logging_strict.tech_niques.CaptureOutput`

"""

import sys
import unittest

from logging_strict.tech_niques import CaptureOutput


class PlayCaptureTheStreams(unittest.TestCase):
    """Context manager to capture streams stdout and stderr"""

    def test_worker_capture_streams(self):
        """Capturing streams context manager. Used within multiprocess Worker"""
        msg_0 = "Hello"
        msg_1 = "World!"
        with CaptureOutput() as cm:
            # Avoids unsightly newlines
            sys.stdout.write(msg_0)
            sys.stderr.write(msg_1)
        self.assertEqual(cm.stdout, msg_0)
        self.assertEqual(cm.stderr, msg_1)


if __name__ == "__main__":
    """
    .. code-block:: shell

       python -m unittest tests.tech_niques.test_docs_stream_capture --locals

    .. code-block:: shell

       coverage run --data-file=".coverage-combine-35" \
       -m unittest discover -t. -s tests/tech_niques -p "test_docs_stream_capture*.py"

       coverage report --no-skip-covered  --data-file=".coverage-combine-35" \
       --include="**/tech_niques/stream_capture*"

    """
    unittest.main(tb_locals=True)

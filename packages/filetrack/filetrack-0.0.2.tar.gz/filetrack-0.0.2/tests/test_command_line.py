import sys
import os.path
import io
import unittest
from unittest.mock import patch

import consolecmdtools as cct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from filetrack import command_line  # noqa: linter (pycodestyle) should not lint this line.


class test_filetrack(unittest.TestCase):
    """command-line filetrack unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-c", "filetrack.toml"])
            self.assertIn("filetrack.toml", fake_out.getvalue())
            command_line.main(["--config", "filetrack.toml"])
            self.assertIn("filetrack.toml", fake_out.getvalue())

    def test_folder(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            command_line.main(["-f", cct.get_path(__file__).parent])
            self.assertIn("tests", fake_out.getvalue())
            command_line.main(["--folder", cct.get_path(__file__).parent])
            self.assertIn("tests", fake_out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)

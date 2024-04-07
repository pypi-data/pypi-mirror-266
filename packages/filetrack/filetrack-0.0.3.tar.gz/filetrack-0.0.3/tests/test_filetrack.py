import sys
import os.path
import io
import unittest
from unittest.mock import patch

import consolecmdtools as cct

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import filetrack  # noqa: linter (pycodestyle) should not lint this line.


class test_filetrack(unittest.TestCase):
    """filetrack unittest"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        self.assertIsInstance(filetrack.__version__, str)

    def test_parse_config(self):
        folder = cct.get_path(__file__).parent
        config_path = os.path.join(folder, 'filetrack.toml')
        self.assertEqual(filetrack.parse_config(config_path, folder)['vars']['name'], 'TF')

    def test_run_filetrack(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            folder = cct.get_path(__file__).parent
            config_path = os.path.join(folder, 'filetrack.toml')
            filetrack.run_filetrack(config_path=config_path, folder=folder)
            self.assertIn(..., fake_out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)

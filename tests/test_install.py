import unittest
import os
import tempfile
import shutil
import subprocess


class TestInstall(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        subprocess.check_call(["virtualenv", self.tempdir])

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def virtualenv_bin(self, cmd):
        return os.path.join(self.tempdir, "bin", cmd)

    def test_install(self):
        subprocess.check_call([self.virtualenv_bin("python"), "setup.py", "install"])

    def test_cli(self):
        self.test_install()
        subprocess.check_call([self.virtualenv_bin("acme-tiny"), "-h"])

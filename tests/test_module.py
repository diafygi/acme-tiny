import unittest, os, tempfile
from subprocess import Popen

import acme_tiny
from . import monkey

class TestModule(unittest.TestCase):
    "Tests for acme_tiny.get_crt()"

    def setUp(self):
        self.CA = "https://acme-staging.api.letsencrypt.org"
        self.keys = monkey.gen_keys()
        self.tempdir = tempfile.mkdtemp()
        self.fuse_proc = Popen(["python", "tests/monkey.py", self.tempdir])

    def tearDown(self):
        self.fuse_proc.terminate()
        self.fuse_proc.wait()
        os.rmdir(self.tempdir)

    def test_success(self):
        result = acme_tiny.get_crt(
            self.keys['account_key'].name,
            self.keys['domain_csr'].name,
            self.tempdir,
            CA=self.CA)

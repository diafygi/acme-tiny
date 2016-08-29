import unittest, os, sys, tempfile
from subprocess import Popen, PIPE
try:
    from StringIO import StringIO # Python 2
except ImportError:
    from io import StringIO # Python 3

import acme_tiny
from .monkey import gen_keys

KEYS = gen_keys()

class TestModule(unittest.TestCase):
    "Tests for acme_tiny.get_crt()"

    def setUp(self):
        self.CA = "https://acme-staging.api.letsencrypt.org"
        self.tempdir = tempfile.mkdtemp()
        self.fuse_proc = Popen(["python", "tests/monkey.py", self.tempdir])

    def tearDown(self):
        self.fuse_proc.terminate()
        self.fuse_proc.wait()
        os.rmdir(self.tempdir)

    def test_success_cn(self):
        """ Successfully issue a certificate via common name """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", KEYS['account_key'].name,
            "--csr", KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--ca", self.CA,
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE,
            stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn("Issuer: CN=Fake LE Intermediate", out.decode("utf8"))

    def test_success_san(self):
        """ Successfully issue a certificate via subject alt name """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", KEYS['account_key'].name,
            "--csr", KEYS['san_csr'].name,
            "--acme-dir", self.tempdir,
            "--ca", self.CA,
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE,
            stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn("Issuer: CN=Fake LE Intermediate", out.decode("utf8"))

    def test_success_cli(self):
        """ Successfully issue a certificate via command line interface """
        crt, err = Popen([
            "python", "acme_tiny.py",
            "--account-key", KEYS['account_key'].name,
            "--csr", KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--ca", self.CA,
        ], stdout=PIPE, stderr=PIPE).communicate()
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE,
            stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn("Issuer: CN=Fake LE Intermediate", out.decode("utf8"))

    def test_missing_account_key(self):
        """ OpenSSL throws an error when the account key is missing """
        try:
            result = acme_tiny.main([
                "--account-key", "/foo/bar",
                "--csr", KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, IOError)
        self.assertIn("Error opening Private Key", result.args[0])

    def test_missing_csr(self):
        """ OpenSSL throws an error when the CSR is missing """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", "/foo/bar",
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, IOError)
        self.assertIn("Error loading /foo/bar", result.args[0])

    def test_weak_key(self):
        """ Let's Encrypt rejects weak keys """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['weak_key'].name,
                "--csr", KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("Key too small", result.args[0])

    def test_invalid_domain(self):
        """ Let's Encrypt rejects invalid domains """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", KEYS['invalid_csr'].name,
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("Invalid character in DNS name", result.args[0])

    def test_nonexistant_domain(self):
        """ Should be unable verify a nonexistent domain """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", KEYS['nonexistent_csr'].name,
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("but couldn't download", result.args[0])

    def test_account_key_domain(self):
        """ Can't use the account key for the CSR """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", KEYS['account_csr'].name,
                "--acme-dir", self.tempdir,
                "--ca", self.CA,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("Certificate public key must be different than account key", result.args[0])


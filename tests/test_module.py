import unittest, os, sys, tempfile
from subprocess import Popen, PIPE
try:
    from StringIO import StringIO # Python 2
except ImportError:
    from io import StringIO # Python 3
try:
    from urllib.request import urlopen # Python 3
except ImportError:
    from urllib2 import urlopen # Python 2

import acme_tiny
import writecheck, removecheck
from .monkey import gen_keys

KEYS = gen_keys()

class TestModule(unittest.TestCase):
    "Tests for acme_tiny.get_crt()"

    def setUp(self):
        self.CA = "https://acme-staging.api.letsencrypt.org"
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        os.rmdir(self.tempdir)

    def test_success_cn(self):
        """ Successfully issue a certificate via common name """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", KEYS['account_key'].name,
            "--csr", KEYS['domain_csr'].name,
            "--ca", self.CA,
            "--challenge-helper", "tests/monkey.py",
            "--challenge-helper-remove", "true",
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
            "--ca", self.CA,
            "--challenge-helper", "tests/monkey.py",
            "--challenge-helper-remove", "true",
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
            "--ca", self.CA,
            "--challenge-helper", "tests/monkey.py",
            "--challenge-helper-remove", "true",
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
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
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
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
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
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("key too small", result.args[0])

    def test_invalid_domain(self):
        """ Let's Encrypt rejects invalid domains """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", KEYS['invalid_csr'].name,
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
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
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("404.gethttpsforfree.com challenge did not pass", result.args[0])

    def test_account_key_domain(self):
        """ Can't use the account key for the CSR """
        try:
            result = acme_tiny.main([
                "--account-key", KEYS['account_key'].name,
                "--csr", KEYS['account_csr'].name,
                "--ca", self.CA,
                "--challenge-helper", "tests/monkey.py",
                "--challenge-helper-remove", "true",
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("certificate public key must be different than account key", result.args[0])

    def test_write_remove_check(self):
        """ Test writecheck script """
        urlopen("http://{0}/.well-known/acme-challenge/?{1}".format(
            os.getenv("TRAVIS_DOMAIN", "not_set"),
            os.getenv("TRAVIS_SESSION", "not_set")), "testtoken")
        os.environ['WEBROOT'] = tempfile.mkdtemp()
        os.environ['DOMAIN'] = os.getenv("TRAVIS_DOMAIN", "not_set")
        stdin = sys.stdin
        sys.stdin = StringIO("testtoken")
        writecheck.main("testtoken")
        sys.stdin = stdin
        removecheck.main("testtoken")


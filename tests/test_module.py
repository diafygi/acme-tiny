import os
import sys
import json
import time
import shutil
import logging
import unittest
import tempfile
from subprocess import Popen, PIPE

try:
    from urllib.request import urlopen, Request # Python 3
except ImportError: # pragma: no cover
    from urllib2 import urlopen, Request # Python 2

try:
    from StringIO import StringIO # Python 2
except ImportError: # pragma: no cover
    from io import StringIO # Python 3

import acme_tiny
from . import utils

# test settings based on environmental variables
PEBBLE_BIN = os.getenv("ACME_TINY_PEBBLE_BIN") or "{}/go/bin/pebble".format(os.getenv("HOME"))  # default pebble install path
DOMAIN = os.getenv("ACME_TINY_DOMAIN") or "local.gethttpsforfree.com"  # default to domain that resolves to 127.0.0.1
USE_STAGING = bool(os.getenv("ACME_TINY_USE_STAGING"))  # default to false
SSHFS_CHALLENGE_DIR = os.getenv("ACME_TINY_SSHFS_CHALLENGE_DIR")  # default to None (only used if USE_STAGING is True)

class TestModule(unittest.TestCase):
    """
    Tests for acme_tiny.py functionality itself
    """
    def setUp(self):
        """
        Set up ACME server for each test (or use Let's Encrypt's staging server)
        """
        # create new account keys every test
        self.KEYS = utils.gen_keys(DOMAIN)

        # use Let's Encrypt staging server
        if USE_STAGING: # pragma: no cover
            os.unsetenv("SSL_CERT_FILE")  # use the default ssl trust store
            # config references
            self.tempdir = SSHFS_CHALLENGE_DIR
            self.check_port = "80"
            self.DIR_URL = "https://acme-staging-v02.api.letsencrypt.org/directory"
            # staging server errors
            self.account_key_error = "certificate public key must be different than account key"
            self.ca_issued_string = "(STAGING) Let's Encrypt"
            self.bad_character_error = "Domain name contains an invalid character"

        # default to using pebble server
        else:
            # config references
            self.tempdir = None  # generated below
            self.DIR_URL = "https://localhost:14000/dir"
            self._pebble_server, self._pebble_config = utils.setup_pebble(PEBBLE_BIN)
            self.check_port = str(self._pebble_config['pebble']['httpPort'])
            self._challenge_file_server, self._base_tempdir, self.tempdir = utils.setup_local_fileserver(self.check_port, pebble_proc=self._pebble_server)
            # pebble server errors
            self.account_key_error = "CSR contains a public key for a known account"
            self.ca_issued_string = "Pebble Intermediate CA"
            self.bad_character_error = "Order included DNS identifier with a value containing an illegal character"

    def tearDown(self):
        """
        Shut down sub processes (pebble, etc.)
        """
        # only need to shut down stuff if using local servers (pebble)
        if not USE_STAGING:

            self._pebble_server.terminate()
            self._pebble_server.wait()
            os.remove(self._pebble_config['pebble']['certificate'])
            os.remove(self._pebble_config['pebble']['privateKey'])

            self._challenge_file_server.terminate()
            self._challenge_file_server.wait()
            shutil.rmtree(self._base_tempdir)

    def test_success_domain(self):
        """ Successfully issue a certificate via subject alt name """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", self.KEYS['account_key'].name,
            "--csr", self.KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--directory-url", self.DIR_URL,
            "--check-port", self.check_port,
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn(self.ca_issued_string, out.decode("utf8"))

    def test_skip_valid_authorizations(self):
        """ Authorizations that are already valid should be skipped """
        # issue a valid cert
        self.test_success_domain()

        # add a logging handler that captures the info log output
        log_output = StringIO()
        debug_handler = logging.StreamHandler(log_output)
        acme_tiny.LOGGER.addHandler(debug_handler)

        # issue the cert again, where challenges should already be valid
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", self.KEYS['account_key'].name,
            "--csr", self.KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--directory-url", self.DIR_URL,
            "--check-port", self.check_port,
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        log_output.seek(0)
        log_string = log_output.read().encode("utf8")

        # remove logging capture
        acme_tiny.LOGGER.removeHandler(debug_handler)

        # should say the domain is already verified
        self.assertIn("Already verified: {0}, skipping...".format(DOMAIN), log_string.decode("utf8"))

    def test_success_cli(self):
        """ Successfully issue a certificate via command line interface """
        crt, err = Popen([
            "python", "acme_tiny.py",
            "--account-key", self.KEYS['account_key'].name,
            "--csr", self.KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--directory-url", self.DIR_URL,
            "--check-port", self.check_port,
        ], stdout=PIPE, stderr=PIPE).communicate()
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn(self.ca_issued_string, out.decode("utf8"))

    def test_missing_account_key(self):
        """ OpenSSL throws an error when the account key is missing """
        try:
            result = acme_tiny.main([
                "--account-key", "/foo/bar",
                "--csr", self.KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, IOError)
        self.assertIn("unable to load Private Key", result.args[0])

    def test_missing_csr(self):
        """ OpenSSL throws an error when the CSR is missing """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", "/foo/bar",
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, IOError)
        self.assertIn("Error loading /foo/bar", result.args[0])

    def test_invalid_domain(self):
        """ Let's Encrypt rejects invalid domains """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['invalid_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn(self.bad_character_error, result.args[0])

    def test_nonexistent_domain(self):
        """ Should be unable verify a nonexistent domain """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['nonexistent_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("but couldn't download", result.args[0])

    def test_account_key_domain(self):
        """ Can't use the account key for the CSR """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['account_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn(self.account_key_error, result.args[0])

    def test_contact(self):
        """ Make sure optional contact details can be set """
        # add a logging handler that captures the info log output
        log_output = StringIO()
        debug_handler = logging.StreamHandler(log_output)
        acme_tiny.LOGGER.addHandler(debug_handler)
        # call acme_tiny with new contact details
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", self.KEYS['account_key'].name,
            "--csr", self.KEYS['domain_csr'].name,
            "--acme-dir", self.tempdir,
            "--directory-url", self.DIR_URL,
            "--check-port", self.check_port,
            "--contact", "mailto:devteam@gethttpsforfree.com", "mailto:boss@gethttpsforfree.com",
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        log_output.seek(0)
        log_string = log_output.read().encode("utf8")
        # make sure the certificate was issued and the contact details were updated
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn(self.ca_issued_string, out.decode("utf8"))
        self.assertTrue((  # can be in either order
            "Updated contact details:\nmailto:devteam@gethttpsforfree.com\nmailto:boss@gethttpsforfree.com" in log_string.decode("utf8")
            or "Updated contact details:\nmailto:boss@gethttpsforfree.com\nmailto:devteam@gethttpsforfree.com" in log_string.decode("utf8")
        ))
        # remove logging capture
        acme_tiny.LOGGER.removeHandler(debug_handler)

    def test_challenge_failure(self):
        """ Raises error if challenge doesn't pass """
        # man-in-the-middle ACME requests to modify valid challenges so we raise that exception
        def urlopenMITM(*args, **kwargs):
            resp = urlopenOriginal(*args, **kwargs)
            resp._orig_read = resp.read()
            # modify valid challenges and authorizations to invalid
            try:
                resp_json = json.loads(resp._orig_read.decode("utf8"))
                if (
                    len(resp_json.get("challenges", [])) == 1
                    and resp_json['challenges'][0]['status'] == "valid"
                    and resp_json['status'] == "valid"
                ):
                    resp_json['challenges'][0]['status'] = "invalid"
                    resp_json['status'] = "invalid"
                    resp._orig_read = json.dumps(resp_json).encode("utf8")
            except ValueError:
                pass
            # serve up modified response when read
            def multi_read():
                return resp._orig_read
            resp.read = multi_read
            return resp

        # call acme-tiny with MITM'd urlopen
        urlopenOriginal = acme_tiny.urlopen
        acme_tiny.urlopen = urlopenMITM
        try:
            acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except ValueError as e:
            result = e
        acme_tiny.urlopen = urlopenOriginal

        # should raise error that challenge didn't pass
        self.assertIn("Challenge did not pass for", result.args[0])

    def test_malicious_challenge_token(self):
        """ Raises error if malicious challenge token is provided by the CA """

        # assume the CA wants to try to fool you into serving up your password file
        malicious_token = "../../../../etc/passwd"
        cleaned_token = "____________etc_passwd"

        # man-in-the-middle ACME requests to modify the challenge token to something malicious
        def urlopenMITM(*args, **kwargs):
            resp = urlopenOriginal(*args, **kwargs)
            resp._orig_read = resp.read()
            try:
                resp_json = json.loads(resp._orig_read.decode("utf8"))
                if len([c for c in resp_json.get("challenges", []) if c['type'] == "http-01"]) == 1:
                    challenge = [c for c in resp_json['challenges'] if c['type'] == "http-01"][0]
                    challenge['token'] = malicious_token
                    resp._orig_read = json.dumps(resp_json).encode("utf8")
            except ValueError:
                pass
            # serve up modified response when read
            def multi_read():
                return resp._orig_read
            resp.read = multi_read
            return resp

        # call acme-tiny with MITM'd urlopen
        urlopenOriginal = acme_tiny.urlopen
        acme_tiny.urlopen = urlopenMITM
        try:
            acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except ValueError as e:
            result = e
        acme_tiny.urlopen = urlopenOriginal

        # should raise error that challenge didn't pass
        self.assertIn("Challenge did not pass for", result.args[0])

        # challenge file actually saved as a cleaned version
        resp = urlopen(Request("http://{0}:{1}/.well-known/acme-challenge/{2}".format(DOMAIN, self.check_port, cleaned_token)))
        token_data = resp.read().decode("utf8")
        self.assertIn(cleaned_token, token_data)

    def test_order_failure(self):
        """ Raises error if order doesn't complete """
        # man-in-the-middle ACME requests to modify valid orders so we raise that exception
        def urlopenMITM(*args, **kwargs):
            resp = urlopenOriginal(*args, **kwargs)
            resp._orig_read = resp.read()
            # modify valid orders to invalid
            try:
                resp_json = json.loads(resp._orig_read.decode("utf8"))
                if (
                    resp_json.get("finalize", None) is not None
                    and resp_json.get("status", None) == "valid"
                ):
                    resp_json['status'] = "invalid"
                    resp._orig_read = json.dumps(resp_json).encode("utf8")
            except ValueError:
                pass
            # serve up modified response when read
            def multi_read():
                return resp._orig_read
            resp.read = multi_read
            return resp

        # call acme-tiny with MITM'd urlopen
        urlopenOriginal = acme_tiny.urlopen
        acme_tiny.urlopen = urlopenMITM
        try:
            acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except ValueError as e:
            result = e
        acme_tiny.urlopen = urlopenOriginal

        # should raise error that challenge didn't pass
        self.assertIn("Order failed", result.args[0])

    ###########################
    ## Pebble-specific tests ##
    ###########################

    @unittest.skipIf(USE_STAGING, "only checked on pebble server since staging can't have nonce retries set")
    def test_nonce_retry(self):
        """ Still works when lots of nonce retries """
        # kill current pebble server
        self._pebble_server.terminate()
        self._pebble_server.wait()
        os.remove(self._pebble_config['pebble']['certificate'])
        os.remove(self._pebble_config['pebble']['privateKey'])
        # restart with new bad nonce rate
        self._pebble_server, self._pebble_config = utils.setup_pebble(PEBBLE_BIN, bad_nonces=90)
        # normal success test
        self.test_success_domain()

    @unittest.skipIf(USE_STAGING, "only checked on pebble server since ")
    def test_pebble_doesnt_support_cn_domains(self):
        """ Test that pebble server doesn't support CN subject domains """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['account_key'].name,
                "--csr", self.KEYS['cn_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                "--check-port", self.check_port,
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("Order includes different number of DNSnames identifiers than CSR specifies", result.args[0])

    ############################
    ## Staging-specific tests ##
    ############################

    @unittest.skipIf((not USE_STAGING), "only checked on staging since pebble doesn't support CN names")
    def test_success_cn(self): # pragma: no cover
        """ Successfully issue a certificate via common name """
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        result = acme_tiny.main([
            "--account-key", self.KEYS['account_key'].name,
            "--csr", self.KEYS['cn_csr'].name,
            "--acme-dir", self.tempdir,
            "--directory-url", self.DIR_URL,
            #"--check-port", self.check_port, # defaults to port 80 anyway, so test that the default works
        ])
        sys.stdout.seek(0)
        crt = sys.stdout.read().encode("utf8")
        sys.stdout = old_stdout
        out, err = Popen(["openssl", "x509", "-text", "-noout"], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(crt)
        self.assertIn(self.ca_issued_string, out.decode("utf8"))

    @unittest.skipIf((not USE_STAGING), "only checked on staging since pebble doesn't check for weak keys")
    def test_weak_key(self): # pragma: no cover
        """ Let's Encrypt rejects weak keys """
        try:
            result = acme_tiny.main([
                "--account-key", self.KEYS['weak_key'].name,
                "--csr", self.KEYS['domain_csr'].name,
                "--acme-dir", self.tempdir,
                "--directory-url", self.DIR_URL,
                #"--check-port", self.check_port, # defaults to port 80 anyway, so test that the default works
            ])
        except Exception as e:
            result = e
        self.assertIsInstance(result, ValueError)
        self.assertIn("key too small", result.args[0])


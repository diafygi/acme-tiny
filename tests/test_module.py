import unittest
import acme_tiny

class TestModule(unittest.TestCase):
    "Tests for acme_tiny.get_crt()"

    def setUp(self):
        self.CA = "https://acme-staging.api.letsencrypt.org"

    def test_ca(self):
        self.assertEqual(self.CA, "https://acme-staging.api.letsencrypt.org")

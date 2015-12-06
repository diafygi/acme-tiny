import os, sys
from tempfile import NamedTemporaryFile
from subprocess import Popen
from fuse import FUSE, Operations, LoggingMixIn
try:
    from urllib.request import urlopen # Python 3
except ImportError:
    from urllib2 import urlopen # Python 2

# domain with server.py running on it for testing
DOMAIN = os.getenv("TRAVIS_DOMAIN", "travis-ci.gethttpsforfree.com")

# generate account and domain keys
def gen_keys():
    # good account key
    account_key = NamedTemporaryFile()
    Popen(["openssl", "genrsa", "-out", account_key.name, "2048"]).wait()

    # good domain key
    domain_key = NamedTemporaryFile()
    domain_csr = NamedTemporaryFile()
    Popen(["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", domain_key.name,
        "-subj", "/CN={0}".format(DOMAIN), "-out", domain_csr.name]).wait()
    return {
        "account_key": account_key,
        "domain_key": domain_key,
        "domain_csr": domain_csr,
    }

# fake a folder structure to catch the key authorization file
FS = {}
class Passthrough(LoggingMixIn, Operations):
    def getattr(self, path, fh=None):
        f = FS.get(path, None)
        if f is None:
            return super(Passthrough, self).getattr(path, fh=fh)
        return f

    def write(self, path, buf, offset, fh):
        urlopen("http://{0}/.well-known/acme-challenge/?{1}".format(DOMAIN,
            os.getenv("TRAVIS_SESSION", "not_set")), buf)
        return len(buf)

    def create(self, path, mode, fi=None):
        FS[path] = {"st_mode": 33204}
        return 0

    def unlink(self, path):
        del(FS[path])
        return 0

if __name__ == "__main__":
    FUSE(Passthrough(), sys.argv[1], nothreads=True, foreground=True)

import os
import sys
import json
import time
from tempfile import NamedTemporaryFile, mkdtemp
from subprocess import Popen
try:
    from urllib.request import urlopen # Python 3
except ImportError: # pragma: no cover
    from urllib2 import urlopen # Python 2

def gen_keys(domain):
    """ Generate test account and domain keys """

    # openssl config is system dependent
    openssl_cnf = None
    for possible_cnf in ['/etc/pki/tls/openssl.cnf', '/etc/ssl/openssl.cnf']:
        if os.path.exists(possible_cnf):
            with open(possible_cnf) as f:
                openssl_cnf = f.read().encode("utf8")

    # good account key
    account_key = NamedTemporaryFile()
    Popen(["openssl", "genrsa", "-out", account_key.name, "2048"]).wait()

    # weak 1024 bit key
    weak_key = NamedTemporaryFile()
    Popen(["openssl", "genrsa", "-out", weak_key.name, "1024"]).wait()

    # good domain key
    domain_key = NamedTemporaryFile()
    Popen(["openssl", "genrsa", "-out", domain_key.name, "2048"]).wait()

    # good domain csr
    domain_csr = NamedTemporaryFile()
    domain_conf = NamedTemporaryFile()
    domain_conf.write(openssl_cnf)
    domain_conf.write("\n[SAN]\nsubjectAltName=DNS:{0}\n".format(domain).encode("utf8"))
    domain_conf.flush()
    domain_conf.seek(0)
    Popen(["openssl", "req", "-new", "-sha256", "-key", domain_key.name,
        "-subj", "/", "-reqexts", "SAN", "-config", domain_conf.name,
        "-out", domain_csr.name]).wait()

    # good domain via the Common Name
    cn_key = NamedTemporaryFile()
    cn_csr = NamedTemporaryFile()
    Popen(["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", cn_key.name,
        "-subj", "/CN={0}".format(domain), "-out", cn_csr.name]).wait()

    # invalid domain csr
    invalid_csr = NamedTemporaryFile()
    invalid_conf = NamedTemporaryFile()
    invalid_conf.write(openssl_cnf)
    invalid_conf.write(u"\n[SAN]\nsubjectAltName=DNS:\xC3\xA0\xC2\xB2\xC2\xA0_\xC3\xA0\xC2\xB2\xC2\xA0.com\n".encode("utf8"))
    invalid_conf.seek(0)
    Popen(["openssl", "req", "-new", "-sha256", "-key", domain_key.name,
        "-subj", "/", "-reqexts", "SAN", "-config", invalid_conf.name,
        "-out", invalid_csr.name]).wait()

    # nonexistent domain csr
    nonexistent_csr = NamedTemporaryFile()
    nonexistent_conf = NamedTemporaryFile()
    nonexistent_conf.write(openssl_cnf)
    nonexistent_conf.write("\n[SAN]\nsubjectAltName=DNS:404.gethttpsforfree.com\n".encode("utf8"))
    nonexistent_conf.seek(0)
    Popen(["openssl", "req", "-new", "-sha256", "-key", domain_key.name,
        "-subj", "/", "-reqexts", "SAN", "-config", nonexistent_conf.name,
        "-out", nonexistent_csr.name]).wait()

    # account-signed domain csr
    account_csr = NamedTemporaryFile()
    account_conf = NamedTemporaryFile()
    account_conf.write(openssl_cnf)
    account_conf.write("\n[SAN]\nsubjectAltName=DNS:{0}\n".format(domain).encode("utf8"))
    account_conf.seek(0)
    Popen(["openssl", "req", "-new", "-sha256", "-key", account_key.name,
        "-subj", "/", "-reqexts", "SAN", "-config", account_conf.name,
        "-out", account_csr.name]).wait()

    return {
        "account_key": account_key,
        "weak_key": weak_key,
        "cn_key": cn_key,
        "cn_csr": cn_csr,
        "domain_key": domain_key,
        "domain_csr": domain_csr,
        "invalid_csr": invalid_csr,
        "nonexistent_csr": nonexistent_csr,
        "account_csr": account_csr,
    }

# Pebble server TLS certs
# !!! DO NOT USE FOR ANYTHING EXCEPT TESTS !!!
# Generated using the following commands:
#   openssl genrsa -out pebble_cert.key 4096
#   openssl req -x509 -new -nodes -key pebble_cert.key -days 9999 -subj "/" -addext "subjectAltName=DNS:localhost" -out pebble_cert.crt
PEBBLE_CERT_KEY = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""
PEBBLE_CERT = """
-----BEGIN CERTIFICATE-----
MIIE9zCCAt+gAwIBAgIUTKfSOxaM/Gy3XrDc/3+xn4uy44YwDQYJKoZIhvcNAQEL
BQAwADAeFw0yMTA4MDIyMTQ3MjZaFw00ODEyMTcyMTQ3MjZaMAAwggIiMA0GCSqG
SIb3DQEBAQUAA4ICDwAwggIKAoICAQDm9avXjGUpl3gdhnZYvIhl2xMO1WcEVHt6
DermNjF9lEfPU13XtPcz3gajl6mHkbeHx/eWlA2IsIIZ6cwDXitC3BJ5SiUUgDPn
zP0/H7EEzaFbHrTJx8nylEC9jmCH1uSBn9xkNVrfc8WJgBcAn41yPAxDNWLBfLqy
OYrdC2CNBplbZBTz/UAdW9nJUgJSFFKWyvYt9Oq2gjI2yOZZKq5pYHZsEJxUAqtx
/CHg5QPFYMdmXddELAGeu8CpVdrrxN1hwfjvO07G5mTYAf39nw2ZNtcMnrlplZVb
Ud1v4fd+fhb5mDVzIA7TawR7LoppUlq7KeJmE/atryeDmFjmX3g0JTiWXplhogOe
SOD4Rvttj9aJFVx6yBJN609eVtzQTsM+MTdT6XHilCFU/zJRfZVAumhV4pwyf0xs
K/prRs1HXbGZBuW5HRUPeEcoC+N/3YUVWqvUqIP/Jkr1oBCPBE3ZO+uoi1mkOYlz
raDBmAtFKlCGl88ZpKa0QS6EppIcnGDZbHM1Q/RC1pMuNPUWYG7BklNw33Pkir2k
Q0urxc+vYvWDaSb8IrVafnzhaaay8sTXJZK4gxE9TmBDqsvvdborn493zY0Y1xQc
mBqlUScddt0pyAJUjF5VgFPD2x9HsxG9VuX07x6yt5l/IWM1O0OXe3PDrJDxSAsr
NL8A80WxzwIDAQABo2kwZzAdBgNVHQ4EFgQUsA4MGHUxvlXDhDUm2K7LN9u7DhUw
HwYDVR0jBBgwFoAUsA4MGHUxvlXDhDUm2K7LN9u7DhUwDwYDVR0TAQH/BAUwAwEB
/zAUBgNVHREEDTALgglsb2NhbGhvc3QwDQYJKoZIhvcNAQELBQADggIBAILebPEw
06Fow41ZbnSxTiuD9AaAL4PJe4l0gO33BoaES/kmoJMa9cEEkRTzScwljhC4eekc
EnbqT2H1pgBwYSg9SW/fYrhGzSlKHCA62VNQ1benZSO78IY12ld+g6OaYT+QLtXf
lBiRF4+L/9BOzYprfymr2HwdyaOLZc6Mf3YhGmMYqMdKriqrsqMYZmLEZ5Z2pNoF
kiIFnWJeXcuSMkML/TWHMqL1IY1PN07bXeeWWsC8xD+YsLQIfdbEbf/hGSoby6nO
JDDVUNHiSwEEhreXgBc/sLj/7G/BEEuU/u/fOi+NoK/gy4PHzNE7ZmmsDVyedByh
3L5bBsZGJwK+Rbz7fnthKe3ghhd+fSwRvfx07V3QBwlcD1iq/Im/UR5p3zbSR0gt
zplW4F6fLAjkkGBNVNKEgRdYTF8FzHJWoHH1+kBKylb9L1p6kbUhJAbtYfkhZf2E
5QehOPt3WnVJDeDVKTyhFUWsOrOVmXuY5QV114jJaEfrBKrsJ/DTDrBiOS0jKDdI
MQ2xZK0fvI15Osnr2OCggZk5kdAyaOM3ERWPVetBF9aKKFpIQMi1keOM/U5vBAJy
LYEIK0jwMTf3vctsHkeWGVVMf2P498/+KHbomtUBBJU/0jp9G62xWukle5pfzfM9
F5OzP6TuNVIGpCKuPMLZTfcSCPV3ZUEizOVX
-----END CERTIFICATE-----
"""

class PebbleServerException(Exception):
    pass

def setup_pebble(pebble_bin_path, bad_nonces=0):
    """ Start a pebble server and challenge file server """

    # make testing cert temp files
    pebble_crt = NamedTemporaryFile(delete=False)  # keep until manually cleaned up in tearDown
    pebble_crt.write(PEBBLE_CERT.encode("utf8"))
    pebble_crt.flush()

    pebble_key = NamedTemporaryFile(delete=False)  # keep until manually cleaned up in tearDown
    pebble_key.write(PEBBLE_CERT_KEY.encode("utf8"))
    pebble_key.flush()

    # generate the pebble config
    pebble_config = {
        "pebble": {
            "listenAddress": "127.0.0.1:14000",
            "managementListenAddress": "127.0.0.1:15000",
            "certificate": pebble_crt.name,
            "privateKey": pebble_key.name,
            "httpPort": 5002,
            "tlsPort": 5001,
            "ocspResponderURL": "",
            "externalAccountBindingRequired": False,
        }
    }
    pebble_conf_file = NamedTemporaryFile()
    pebble_conf_file.write(json.dumps(pebble_config, indent=4, sort_keys=True).encode("utf8"))
    pebble_conf_file.flush()

    # start the pebble server
    os.environ['PEBBLE_AUTHZREUSE'] = str(100)
    os.environ['PEBBLE_WFE_NONCEREJECT'] = str(bad_nonces)
    pebble_server_proc = Popen([pebble_bin_path, "-config", pebble_conf_file.name])

    # trust the pebble server cert by default
    os.environ['SSL_CERT_FILE'] = pebble_config['pebble']['certificate']

    # wait until the pebble server responds
    wait_start = time.time()
    MAX_WAIT = 10  # 10 seconds
    while (time.time() - wait_start) < MAX_WAIT:
        try:
            resp = urlopen("https://localhost:14000/dir")
            if resp.getcode() == 200:
                break  # done!
        except IOError:
            pass  # don't care about failed connections
        time.sleep(0.5)  # wait a bit and try again
    else: # pragma: no cover
        pebble_server_proc.terminate()
        raise PebbleServerException("pebble failed to start :(")

    return pebble_server_proc, pebble_config

class ChallengeFileServerException(Exception):
    pass

def setup_local_fileserver(test_port, pebble_proc=None):
    """ Start a local challenge file server """

    # set challenge file temporary directory
    base_tempdir = mkdtemp()
    acme_tempdir = os.path.join(base_tempdir, ".well-known", "acme-challenge")
    os.makedirs(acme_tempdir)

    # start a fileserver for serving up challenges
    local_fileserver_proc = Popen([
        "python",
        "-m", "SimpleHTTPServer" if sys.version_info.major == 2 else "http.server",
        test_port,
    ], cwd=base_tempdir)

    # make sure the fileserver is running
    testchallenge_text = "aaa".encode("utf8")
    testchallenge_path = os.path.join(acme_tempdir, "a.txt")
    testchallenge_file = open(testchallenge_path, "wb")
    testchallenge_file.write(testchallenge_text)
    testchallenge_file.close()
    wait_start = time.time()
    MAX_WAIT = 10  # 10 seconds
    while (time.time() - wait_start) < MAX_WAIT:
        try:
            resp = urlopen("http://localhost:{}/.well-known/acme-challenge/a.txt".format(test_port))
            if resp.getcode() == 200 and resp.read() == testchallenge_text:
                os.remove(testchallenge_path)
                break  # done!
        except IOError:
            pass  # don't care about failed connections
        time.sleep(0.5)  # wait a bit and try again
    else: # pragma: no cover
        os.remove(testchallenge_path)
        local_fileserver_proc.terminate()
        if pebble_proc is not None:
            pebble_proc.terminate()  # also shut down pebble server (if any) before raising exception
        raise ChallengeFileServerException("challenge file server failed to start :(")

    return local_fileserver_proc, base_tempdir, acme_tempdir


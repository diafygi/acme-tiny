#!/usr/bin/env python
#
# Helper script for writing acme challenge from stdin to a file named by
# the first agument to this script, then check if it's reachable over http
#
import os, sys, subprocess
try:
    from urllib.request import urlopen # Python 3
except ImportError:
    from urllib2 import urlopen # Python 2

def main(token):
    keyauthorization = sys.stdin.read()
    wellknown_path = "{0}/.well-known/acme-challenge/".format(os.getenv('WEBROOT', ''))
    if not os.path.isdir(wellknown_path):
        os.makedirs(wellknown_path)
    with open(wellknown_path + token, 'wb') as f:
        f.write(keyauthorization)
    domain = os.getenv('DOMAIN')
    # check that the file is in place
    wellknown_url = "http://{0}/.well-known/acme-challenge/{1}".format(domain, token)

    resp = urlopen(wellknown_url)
    resp_data = resp.read().decode('utf8').strip()
    assert resp_data == keyauthorization

if __name__ == "__main__": # pragma: no cover
    main(sys.argv[1:])

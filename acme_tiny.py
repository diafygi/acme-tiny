#!/usr/bin/env python
import argparse, subprocess, json, os, urllib2, sys, base64, binascii, time, \
    hashlib, re, copy, textwrap

#CA = "https://acme-staging.api.letsencrypt.org"
CA = "https://acme-v01.api.letsencrypt.org"

def get_crt(account_key, csr, acme_dir):

    # helper function base64 encode for jose spec
    def _b64(b):
        return base64.urlsafe_b64encode(b).replace("=", "")

    # parse account key to get public key
    sys.stderr.write("Parsing account key...")
    proc = subprocess.Popen(["openssl", "rsa", "-in", account_key, "-noout", "-text"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise IOError("OpenSSL Error: {}".format(err))
    pub_hex, pub_exp = re.search(
        "modulus:\n\s+00:([a-f0-9\:\s]+?)\npublicExponent: ([0-9]+)",
        out, re.MULTILINE|re.DOTALL).groups()
    pub_mod = binascii.unhexlify(re.sub("(\s|:)", "", pub_hex))
    pub_mod64 = _b64(pub_mod)
    pub_exp = "{0:x}".format(int(pub_exp))
    pub_exp = "0{}".format(pub_exp) if len(pub_exp) % 2 else pub_exp
    pub_exp64 = _b64(binascii.unhexlify(pub_exp))
    header = {
        "alg": "RS256",
        "jwk": {
            "e": pub_exp64,
            "kty": "RSA",
            "n": pub_mod64,
        },
    }
    accountkey_json = json.dumps(header['jwk'], sort_keys=True, separators=(',', ':'))
    thumbprint = _b64(hashlib.sha256(accountkey_json).digest())
    sys.stderr.write("parsed!\n")

    # helper function make signed requests
    def _send_signed_request(url, payload):
        nonce = urllib2.urlopen(CA + "/directory").headers['Replay-Nonce']
        payload64 = _b64(json.dumps(payload))
        protected = copy.deepcopy(header)
        protected.update({"nonce": nonce})
        protected64 = _b64(json.dumps(protected))
        proc = subprocess.Popen(["openssl", "dgst", "-sha256", "-sign", account_key],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate("{}.{}".format(protected64, payload64))
        if proc.returncode != 0:
            raise IOError("OpenSSL Error: {}".format(err))
        data = json.dumps({
            "header": header,
            "protected": protected64,
            "payload": payload64,
            "signature": _b64(out),
        })
        try:
            resp = urllib2.urlopen(url, data)
            return resp.getcode(), resp.read()
        except urllib2.HTTPError as e:
            return e.code, e.read()

    # find domains
    sys.stderr.write("Parsing CSR...")
    proc = subprocess.Popen(["openssl", "req", "-in", csr, "-noout", "-text"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise IOError("Error loading {}: {}".format(csr, err))
    domains = set([])
    common_name = re.search("Subject:.*? CN=([^\s,;/]+)", out)
    if common_name is not None:
        domains.add(common_name.group(1))
    subject_alt_names = re.search("X509v3 Subject Alternative Name: \n +([^\n]+)\n", out, re.MULTILINE|re.DOTALL)
    if subject_alt_names is not None:
        for san in subject_alt_names.group(1).split(", "):
            if san.startswith("DNS:"):
                domains.add(san[4:])
    sys.stderr.write("parsed!\n")

    # get the certificate domains and expiration
    sys.stderr.write("Registering account...")
    code, result = _send_signed_request(CA + "/acme/new-reg", {
        "resource": "new-reg",
        "agreement": "https://letsencrypt.org/documents/LE-SA-v1.0.1-July-27-2015.pdf",
    })
    if code == 201:
        sys.stderr.write("registered!\n")
    elif code == 409:
        sys.stderr.write("already registered!\n")
    else:
        raise ValueError("Error registering: {} {}".format(code, result))

    # verify each domain
    for domain in domains:
        sys.stderr.write("Verifying {}...".format(domain))

        # get new challenge
        code, result = _send_signed_request(CA + "/acme/new-authz", {
            "resource": "new-authz",
            "identifier": {
                "type": "dns",
                "value": domain,
            },
        })
        if code != 201:
            raise ValueError("Error registering: {} {}".format(code, result))

        # make the challenge file
        challenge = [c for c in json.loads(result)['challenges'] if c['type'] == "http-01"][0]
        keyauthorization = "{}.{}".format(challenge['token'], thumbprint)
        acme_dir = acme_dir[:-1] if acme_dir.endswith("/") else acme_dir
        wellknown_path = "{}/{}".format(acme_dir, challenge['token'])
        wellknown_file = open(wellknown_path, "w")
        wellknown_file.write(keyauthorization)
        wellknown_file.close()

        # check that the file is in place
        wellknown_url = "http://{}/.well-known/acme-challenge/{}".format(
            domain, challenge['token'])
        try:
            resp = urllib2.urlopen(wellknown_url)
            assert resp.read().strip() == keyauthorization
        except (urllib2.HTTPError, urllib2.URLError, AssertionError):
            os.remove(wellknown_path)
            raise ValueError("Wrote file to {}, but couldn't download {}".format(
                wellknown_path, wellknown_url))

        # notify challenge are met
        code, result = _send_signed_request(challenge['uri'], {
            "resource": "challenge",
            "keyAuthorization": keyauthorization,
        })
        if code != 202:
            raise ValueError("Error triggering challenge: {} {}".format(code, result))

        # wait for challenge to be verified
        while True:
            try:
                resp = urllib2.urlopen(challenge['uri'])
                challenge_status = json.loads(resp.read())
            except urllib2.HTTPError as e:
                raise ValueError("Error checking challenge: {} {}".format(
                    e.code, json.loads(e.read())))
            if challenge_status['status'] == "pending":
                time.sleep(2)
            elif challenge_status['status'] == "valid":
                sys.stderr.write("verified!\n")
                os.remove(wellknown_path)
                break
            else:
                raise ValueError("{} challenge did not pass: {}".format(
                    domain, challenge_status))

    # get the new certificate
    sys.stderr.write("Signing certificate...")
    proc = subprocess.Popen(["openssl", "req", "-in", csr, "-outform", "DER"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    csr_der, err = proc.communicate()
    code, result = _send_signed_request(CA + "/acme/new-cert", {
        "resource": "new-cert",
        "csr": _b64(csr_der),
    })
    if code != 201:
        raise ValueError("Error signing certificate: {} {}".format(code, result))

    # return signed certificate!
    sys.stderr.write("signed!\n")
    return """-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----\n""".format(
        "\n".join(textwrap.wrap(base64.b64encode(result), 64)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
This script automates the process of getting a signed TLS certificate from
Let's Encrypt using the ACME protocol. It will need to be run on your server
and have access to your private account key, so PLEASE READ THROUGH IT! It's
only ~200 lines, so it won't take long.

===Example Usage===
python acme_tiny.py --account-key ./account.key --csr ./domain.csr --acme-dir /usr/share/nginx/html/.well-known/acme-challenge/ > signed.crt
===================

===Example Crontab Renewal (once per month)===
0 0 1 * * python /path/to/acme_tiny.py --account-key /path/to/account.key --csr /path/to/domain.csr --acme-dir /usr/share/nginx/html/.well-known/acme-challenge/ > /path/to/signed.crt 2>> /var/log/acme_tiny.log
==============================================

""")
    parser.add_argument("--account-key", required=True, help="path to your Let's Encrypt account private key")
    parser.add_argument("--csr", required=True, help="path to your certificate signing request")
    parser.add_argument("--acme-dir", required=True, help="path to the .well-known/acme-challenge/ directory")

    args = parser.parse_args()
    signed_crt = get_crt(args.account_key, args.csr, args.acme_dir)
    sys.stdout.write(signed_crt)


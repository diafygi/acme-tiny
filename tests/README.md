# How to test acme-tiny

Testing acme-tiny requires a bit of setup since it interacts with other servers
(Let's Encrypt's staging server) to test issuing fake certificates. This readme
explains how to setup and test acme-tiny yourself.

## Setup instructions

1. Make a test subdomain for a server you control. Set it as an environmental
variable on your local test setup.
  * On your local: `export TRAVIS_DOMAIN=travis-ci.gethttpsforfree.com`
2. Generate a shared secret between your local test setup and your server.
  * `openssl rand -base64 32`
  * On your local: `export TRAVIS_SESSION="<random_string_here>"`
3. Copy and run the test suite mini-server on your server:
  * `scp server.py ubuntu@travis-ci.gethttpsforfree.com`
  * `ssh ubuntu@travis-ci.gethttpsforfree.com`
  * `export TRAVIS_SESSION="<random_string_here>"`
  * `sudo server.py`
4. Install the test requirements on your local (FUSE and optionally coveralls).
  * `sudo apt-get install fuse`
  * `virtualenv /tmp/venv`
  * `source /tmp/venv/bin/activate`
  * `pip install -r requirements.txt`
5. Run the test suit on your local.
  * `cd /path/to/acme-tiny`
  * `coverage run --source ./ --omit ./tests/server.py -m unittest tests`

## Why use FUSE?

Acme-tiny writes the challenge files for certificate issuance. In order to do
full integration tests, we actually need to serve correct challenge files to
the Let's Encrypt staging server on a real domain that they can verify. However,
Travis-CI doesn't have domains associated with their test VMs, so we need to
send the files to the remote server that does have a real domain.

The test suite uses FUSE to do this. It creates a FUSE folder that simulates
being a real folder to acme-tiny. When acme-tiny writes the challenge files
in the mock folder, FUSE POSTs those files to the real server (which is running
the included server.py), and the server starts serving them. That way, both
acme-tiny and Let's Encrypt staging can verify and issue the test certificate.
This technique allows for high test coverage on automated test runners (e.g.
Travis-CI).


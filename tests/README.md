# How to test acme-tiny

Testing acme-tiny requires a bit of setup since it interacts with other servers
(Let's Encrypt's staging server) to test issuing fake certificates. This readme
explains how to setup and test acme-tiny yourself.

## Setup instructions

1. Make a test subdomain for a server you control. Set it as an environmental
variable on your local test setup.
  * On your local: `export TRAVIS_DOMAIN=travis-ci.gethttpsforfree.com`
  * Configure the webserver on `$TRAVIS_DOMAIN` for redirection of
    `http://$TRAVIS_DOMAIN/.well-known/acme-challenge/` to
    `http://localhost:8888/`
2. Generate a shared secret between your local test setup and your server.
  * `openssl rand -base64 32`
  * On your local: `export TRAVIS_SESSION="<random_string_here>"`
3. Copy and run the test suite mini-server on your server:
  * `scp server.py ubuntu@travis-ci.gethttpsforfree.com`
  * `ssh ubuntu@travis-ci.gethttpsforfree.com`
  * `export TRAVIS_SESSION="<random_string_here>"`
  * `sudo server.py`
4. Install the test requirements on your local (optionally coveralls).
  * `virtualenv /tmp/venv`
  * `source /tmp/venv/bin/activate`
  * `pip install -r requirements.txt`
5. Run the test suit on your local.
  * `cd /path/to/acme-tiny`
  * `coverage run --source ./ --omit ./tests/server.py -m unittest tests`

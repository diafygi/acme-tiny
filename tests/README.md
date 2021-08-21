# How to test acme-tiny

Testing acme-tiny requires a bit of setup since it needs to interact with a local Let's Encrypt CA test server. This readme explains how to set up your local environment so you can run `acme-tiny` tests yourself.

## Setup instructions (default)

In the default test setup, we use [pebble](https://github.com/letsencrypt/pebble) as the mock Let's Encrypt CA server on your local computer. So you need to install that before running the test suite.

1. Install the Let's Encrypt test server: `pebble` (instructions below are for Ubuntu 20.04, adjust as needed)
  * `sudo apt install golang`
  * `go get -u github.com/letsencrypt/pebble/...`
  * `cd ~/go/src/github.com/letsencrypt/pebble && go install ./...`
  * `~/go/bin/pebble -h` (should print out pebble usage help)
2. Setup a virtual environment for python:
  * `virtualenv -p python3 /tmp/venv` (creates the virtualenv)
  * `source /tmp/venv/bin/activate` (starts using the virtualenv)
3. Install `acme-tiny` test dependencies:
  * `cd /path/to/acme-tiny`
  * `pip install -U -r tests/requirements.txt`
4. Run the test suite on your local.
  * `cd /path/to/acme-tiny`
  * `unset ACME_TINY_USE_STAGING` (optional, if set previously to use staging)
  * `unset ACME_TINY_DOMAIN` (optional, if set previously to use staging)
  * `export ACME_TINY_PEBBLE_BIN="..."` (optional, if different from `"$HOME/go/bin/pebble"`)
  * `coverage erase` (removes any previous coverage data files)
  * `coverage run --source . --omit ./setup.py -m unittest tests` (runs the test suite)
  * `coverage report -m` (optional, prints out coverage summary in console)
  * `coverage html` (optional, generates html coverage report you can browse at `htmlcov/index.html`)

## Setup instructions (staging)

We also allow running the test suite against the official Let's Encrypt [staging](https://letsencrypt.org/docs/staging-environment/) server. Since the staging server is run by Let's Encrypt, you need to actually host a real domain an serve real challenge files. The simplest way to do this is to mount your remote server's static challenge file directory (see example instructions below).

1. Run a static server with a real domain (e.g. `test.mydomain.com`) with a challenge directory (instructions below are for Ubuntu 20.04, adjust as needed).
  * `ssh ubuntu@test.mydomain.com` (log into your server)
  * `mkdir -p /tmp/testfiles/.well-known/acme-challenge` (make the ACME challenge file directory)
  * `cd /tmp/testfiles` (go to the test file base directory)
  * `sudo python3 -m http.server 80 --bind 0.0.0.0` (start listening on port 80, NOTE: needs to run as root)
  * Alternatively, if you are already have a web server running on port 80, adjust that server's config to serve files statically from your test directory.
2. Mount your server's challenge directory on your local system (instructions below are for Ubuntu 20.04, adjust as needed).
  * `sudo apt install sshfs` (if not already done, install sshfs)
  * `sshfs ubuntu@test.mydomain.com:/tmp/testfiles/.well-known/acme-challenge /tmp/challenge-files`
3. Setup a virtual environment for python:
  * `virtualenv -p python3 /tmp/venv` (creates the virtualenv)
  * `source /tmp/venv/bin/activate` (starts using the virtualenv)
4. Install `acme-tiny` test dependencies:
  * `cd /path/to/acme-tiny`
  * `pip install -U -r tests/requirements.txt`
5. Run the test suite on your local.
  * `cd /path/to/acme-tiny`
  * `export ACME_TINY_USE_STAGING="1"`
  * `export ACME_TINY_DOMAIN="test.mydomain.com"`
  * `export ACME_TINY_SSHFS_CHALLENGE_DIR="/tmp/challenge-files"`
  * `coverage erase` (removes any previous coverage data files)
  * `coverage run --source . --omit ./setup.py -m unittest tests` (runs the test suite)
  * `coverage report -m` (optional, prints out coverage summary in console)
  * `coverage html` (optional, generates html coverage report you can browse at `htmlcov/index.html`)
6. When done, unmount the remote directory
  * `umount /tmp/challenge-files`


# How to test acme-tiny

Testing acme-tiny requires a bit of setup since it interacts with other servers
(Let's Encrypt's staging server) to test issuing fake certificates. This readme
explains how to setup and test acme-tiny yourself.

## Setup instructions

Install the test requirements on your local machine (FUSE and optionally coveralls). <br/>
  * `sudo apt-get install fuse`
  * install ngrok: https://ngrok.com/
  * `cd /path/to/acme-tiny`
  * `chmod u+x tests/tests.sh`
  * `./tests/tests.sh`
  * `pip install -r tests/requirements.txt`
  * `export TRAVIS_DOMAIN=$(grep -Eoi "hostname:[A-za-z0-9]+.ngrok.io" url.log| head -1 | cut -d ":" -f2)`
  * `export TRAVIS_SESSION=$(openssl rand -base64 32)`
  * `python ./tests/server.py &`
  * `coverage run --source ./ --omit ./tests/server.py -m unittest tests`

## Why use FUSE?

Acme-tiny writes the challenge files for certificate issuance. In order to do
full integration tests, we actually need to serve correct challenge files to
the Let's Encrypt staging server on a test domain that they can verify. However,
Travis-CI doesn't have domains associated with their test VMs, so we need to
send the files to the local server that does have a test domain. Ngrok provides a secure tunnel to hosts behind a NAT/Firewall such as travis-ci so that the tests can be automated

The test suite uses FUSE to do this. It creates a FUSE folder that simulates
being a real folder to acme-tiny. When acme-tiny writes the challenge files
in the mock folder, FUSE POSTs those files to the test server (which is running
the included server.py), and the server starts serving them. That way, both
acme-tiny and Let's Encrypt staging can verify and issue the test certificate.
This technique allows for high test coverage on automated test runners (e.g.
Travis-CI).


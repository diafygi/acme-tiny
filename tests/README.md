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
  * `python ./tests/server.py &`
  * `coverage run --source ./ --omit ./tests/server.py -m unittest tests`


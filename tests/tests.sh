#!/bin/bash
sudo apt-get -y install unzip
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip
unzip ngrok.zip ngrok
chmod u+x ngrok
./ngrok http 8888 --log stdout --log-format logfmt --log-level debug > url.log a& 
#TRAVIS_DOMAIN=$(grep -Eo "Hostname:[a-z0-9]+.ngrok.io" url.log | head -1 | cut -d':' -f2)
#TRAVIS_SESSION=$(openssl rand -base64 32)
python ./tests/server.py &


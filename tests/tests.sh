#!/bin/bash
sudo apt-get -y install unzip fuse
sudo chmod a+r /etc/fuse.conf
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip
unzip ngrok.zip ngrok
chmod u+x ngrok
./ngrok http 8888 --log stdout --log-format logfmt --log-level debug > url.log &
python ./tests/server.py &


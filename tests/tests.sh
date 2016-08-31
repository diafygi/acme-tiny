#!/bin/bash
sudo apt-get -y install unzip nginx
#sudo mkdir -p /var/www/html/.well-known/acme-challenge
#sudo chmod -R o+rwx /var/www/html/.well-known
sudo service nginx restart
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip
unzip ngrok.zip ngrok
chmod u+x ngrok
sudo ./ngrok http 80 --log stdout --log-format logfmt --log-level debug > url.log &

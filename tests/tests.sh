#!/bin/bash
sudo apt-get -y install unzip nginx
sudo mkdir -p /var/www/html/.well-known/acme-challenge
sudo chown -R $(whoami):www-data /var/www/html/.well-known/
sudo chmod -R 770 /var/www/html/.well-known
if [ $(head -n 1 /etc/issue | awk '{print $2}'  | cut -d "." -f1) == 14 ]
then
	sed -i '/root \/usr.*/s//root \/var\/www\/html;/g' /etc/nginx/sites-available/default	
fi
sudo service nginx restart
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok.zip
unzip ngrok.zip ngrok
chmod u+x ngrok
sudo ./ngrok http 80 --log stdout --log-format logfmt --log-level debug > url.log &

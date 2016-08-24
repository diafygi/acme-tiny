#!/bin/bash
document_root=/var/www/html # change to your document root
nginx_location=$(which nginx)
nginx_config_location=/etc/nginx #change if this is not your config directory
scripts_location=/usr/local/scripts # change if necessary
certs_location=ssl
mkdir -p ${scripts_location}
mkdir -p ${scripts_location}/acme
useradd -r -d /nodir -s /usr/sbin/nologin acme
chown acme:acme /usr/local/scripts/acme
chmod 750 /usr/local/scripts/acme
cd /usr/local/scripts/acme
openssl genrsa -out priv.key 4096 # generating private key for registering to lets encrypt and certificate generation, keep it very secure
git clone 
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
exit
mkdir -p ${document_root}/.well-known
mkdir -p ${document_root}/.well-known/acme-challenge
chown www-data:acme ${document_root}/.well-known
chmod 770 ${document_root}/.well-known
chown www-data:acme ${document_root}/.well-known/acme-challenge
chmod 770 ${document_root}/.well-known/acme-challenge
echo "acme ALL = NOPASSWD: ${nginx_location} -s reload" > /etc/sudoers.d/acme
mkdir -p ${nginx_config_location}/${certs_location}
mkdir -p ${nginx_config_location}/${certs_location}/certs
mkdir -p ${nginx_config_location}/${certs_location}/private
chown -R  acme:root ${nginx_config_location}/${certs_location}
chmod -R 770 ${nginx_config_location}/${certs_location}

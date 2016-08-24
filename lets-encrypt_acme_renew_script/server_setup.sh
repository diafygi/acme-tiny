#!/bin/bash
document_root=/var/www/html # change to your document root
nginx_location=$(which nginx)
nginx_config_location=/etc/nginx #change if this is not your config directory
scripts_location=/usr/local/scripts # change if necessary
certs_location=ssl
mkdir -p ${scripts_location}
useradd -r -d /nodir -s /usr/sbin/nologin acme
cd /usr/local/scripts/
git clone https://github.com/frezbo/acme-tiny.git
cd acme-tiny/lets-encrypt_acme_renew_script/
openssl genrsa -out priv.key 4096 # generating private key for registering to lets encrypt and certificate generation, keep it very secure
chmod 400 priv.key
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
chown -R acme:acme ${scripts_location}/acme-tiny
chmod 750 ${scripts_location}/acme-tiny
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
touch /var/log/renew.log
chown acme:acme /var/log/renew.log

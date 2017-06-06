#!/bin/bash
document_root=/var/www/html # change to your document root
nginx_location=$(which nginx)
nginx_config_location=/etc/nginx #change if this is not your config directory
scripts_location=/usr/local/scripts # change if necessary
renew_scripts_location=${scripts_location}/acme-tiny/lets-encrypt_acme_renew_script
key_file=priv.key #if already has a key change this and set ownership to acme
certs_location=ssl
log_file=/var/log/acme_renew.log #log file
mkdir -p ${scripts_location}
useradd -r -d /nodir -s /usr/sbin/nologin acme #creating a user acme with no home directory and no login
git clone https://github.com/frezbo/acme-tiny.git ${scripts_location}/acme-tiny
openssl genrsa -out ${renew_scripts_location}/$key_file 4096 # generating private key for registering to lets encrypt and certificate generation, keep it very secure
chmod 400 ${renew_scripts_location}/$key_file
wget -O ${renew_scripts_location}/intermediate.pem https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem
chown -R acme:acme ${scripts_location}/acme-tiny
chmod 750 ${scripts_location}/acme-tiny
mkdir -p ${document_root}/.well-known/acme-challenge
chown -R www-data:acme ${document_root}/.well-known
chmod -R 770 ${document_root}/.well-known
echo "acme ALL = NOPASSWD: ${nginx_location} -s reload" > /etc/sudoers.d/acme
mkdir -p ${nginx_config_location}/${certs_location}/certs
mkdir -p ${nginx_config_location}/${certs_location}/private
chown -R  acme:root ${nginx_config_location}/${certs_location}
chmod -R 770 ${nginx_config_location}/${certs_location}
touch $log_file
chown acme:acme $log_file

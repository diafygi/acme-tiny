# Lets Encrypt Renewal script
* Please read the scripts before you run them.

## Setup

### Assumes that the server has already been configured with an SSL certifciate as per the README in acme-tiny

1. Download the server_setup.sh script: `wget https://raw.githubusercontent.com/frezbo/acme-tiny/master/lets-encrypt_acme_renew_script/server_setup.sh`
2. Make the script executable: `chmod u+x server_setup.sh`
3. Run server_setup.sh as root: `./server_setup.sh`
4. If you did not modify the locations in your scrips, follow the steps below, otherwise make changes as necessary
5. Copy the existing certificate to /etc/nginx/ssl/certs, make sure it follows the format domain.crt. For example if your domain is example.com and has subdomains like mail.example.com do the following: <br/> `cp <path to your certificate> /etc/nginx/ssl/certs`. Make sure to copy the certificates of all the subdomains too.
6. Copy the domain keys to /etc/nginx/ssl/private, make sure it follows the format domian.key. For example if your domain is example.com and has subdomains like mail.example.com do the following: <br/> `cp <path to your domain key> /etc/nginx/ssl/private`. Make sure to copy the certificates of all the subdomains too.
7. Make the necessary location changes in your nginx configuration
8. Run `nginx -t` and make sure there are no errors.
9. The script creates a user named *acme* which renews the certificates, the script also creates your private key used for authenticating with lets-encrypt and signing necessary files. Please keep this key very private. The key is located in */usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script*.
10. Make a cron job to run every month as user acme to check for renewals: `crontab -eu acme`
11. At the end of line add this: `* * 3 * * /usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh > /var/log/renew.log 2>&1`
12. Make the script executable: `chmod u+x /usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh`

### Enjoy

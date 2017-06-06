# Lets Encrypt Renewal script
* Please read the scripts before you run them.

## Setup

### Assumes that the server has already been configured with nginx with SSL as per the README in acme-tiny

1. Download the server_setup.sh script: 
```
wget https://raw.githubusercontent.com/frezbo/acme-tiny/master/lets-encrypt_acme_renew_script/server_setup.sh
```
<br/>
2. Make the script executable: `chmod u+x server_setup.sh` <br/>
3. Run server_setup.sh as root: `./server_setup.sh` <br/>
4. If you did not modify the locations in your scrips, follow the steps below, otherwise make changes as necessary <br/>
5. Copy the existing certificate to /etc/nginx/ssl/certs, make sure it follows the format domain.tld.ec.crt for ec certificates or domain.tld.rsa.crt for rsa certificates. For example if your domain is domain.tld and has subdomains like subdomain.domain.tld do the following: <br/><br/> `cp <path to your certificate> /etc/nginx/ssl/certs` <br/><br/> Make sure to copy the certificates of all the subdomains too. <br/>
6. Copy the domain keys to /etc/nginx/ssl/private, make sure it follows the format domian.com.ec.key for ec keys or domain.tld.rsa.crt for rsa keys. For example if your domain is domain.tld and has subdomains like subdomain.domain.tld do the following: <br/><br/> `cp <path to your domain key> /etc/nginx/ssl/private` <br/><br/> Make sure to copy the certificates of all the subdomains too. <br/>
7. Make the necessary location changes for the domain private key and certificate location in your nginx configuration <br/>
8. Run `nginx -t` and make sure there are no errors. <br/>
9. The script creates a user named *acme* which renews the certificates, the script also creates your private key used for authenticating with lets-encrypt and signing necessary files. Please keep this key very private. The key is located in */usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script*. <br/>
10. Edit the file domains.cnf located at */usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/domains.cnf* and add the email id at line 8, add necessary country code, state,location and organizaion info as required. <br/>
11. Edit the file domains.txt located at */usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/domains.txt* and add your domains on each line. For example if your domain is domain.tld and has subdomains like subdomain.domain.tld do the following:
```
domain
subdomain.domain
```
<br/>
12. Edit the file renew.sh located at */usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh* and add your tld in quotes on line 3. <br/>
13. Make a cron job to run every month as user acme to check for renewals: 
```
crontab -eu acme
``` 
<br/>
At the end of line add this: 
```
* * 3 * * /usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh >> /var/log/renew.log 2>&1
```
<br/>
14. Make the script executable: `chmod u+x /usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh` <br/>
15. If you want to manually run the script:
```
sudo -u acme /usr/local/scripts/acme-tiny/lets-encrypt_acme_renew_script/renew.sh
```
<br/>
16. Set the nginx configuration as follows:

### nginx configuration <br/> nginx versions above 1.10.0 supports both ECDSA and RSA certificates together otherwise stick with a single type

#### Base domain
```
server {
          server_name domain.tld
          ssl_certificate /etc/nginx/ssl/certs/domain.tld.ec.crt;
          ssl_certificate_key /etc/nginx/ssl/private/domain.tld.ec.key;
          ssl_certificate /etc/nginx/ssl/certs/domain.tld.rsa.crt;
          ssl_certificate_key /etc/nginx/ssl/private/domain.tld.rsa.key;
          location ~ .well-known/ {
                        root /var/www/html; #change as per your document root
                        try_files $uri =404;
                        log_not_found off;
                }
        }
```

#### Sub-domain
  ```
  server {
          server_name subdomain.domain.tld
          ssl_certificate /etc/nginx/ssl/certs/subdomain.domain.tld.ec.crt;
          ssl_certificate_key /etc/nginx/ssl/private/subdomain.domain.tld.ec.key;
          ssl_certificate /etc/nginx/ssl/certs/subdomain.domain.tld.rsa.crt;
          ssl_certificate_key /etc/nginx/ssl/private/subdomain.domain.tld.rsa.key;
          location ~ .well-known/ {
                        root /var/www/html; #change as per your document root
                        try_files $uri =404;
                        log_not_found off;
                }
          }
  ```

## Enjoy

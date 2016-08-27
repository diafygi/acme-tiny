#!/bin/bash
sudo apt-get install nginx
cat > /etc/nginx/sites-enabled/test.frezbo.com << EOF
server {
                listen 80;
                server_name test.frezbo.com;
                root /var/www/html;
                index index.html;

        location / {
                        try_files \$uri =404;
                }

        location ~ .well-known/ {
                        try_files \$uri =404;
                        log_not_found off;
                }
}
EOF
mkdir -p /var/www/html/.well-known
mkdir -p /var/www/html/.well-known/acme-challenge
nginx -s reload
ip=$(dig +short myip.opendns.com @resolver1.opendns.com)
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$dns_record" -H "X-Auth-Email: $mail" -H "X-Auth-Key: $token" -H "Content-Type: application/json" -d "{\"id\":\"$zone_id\",\"type\":\"A\",\"name\":\"test.frezbo.com\",\"content\":\"$ip\"}"
opemssl genrsa -out priv.key
openssl req -new -newkey rsa:2048 -nodes -subj "/CN=test.frezbo.com" -out sign.csr
rm -f privkey.pem
python acme_tiny.py --ca https://acme-staging.api.letsencrypt.org --account-key priv.key --csr sign.csr --acme-dir /var/www/html/.well-known/acme-challenge > test.crt
rm -f test.crt
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$zone_id/dns_records/$dns_record" -H "X-Auth-Email: $mail" -H "X-Auth-Key: $token" -H "Content-Type: application/json" -d "{\"id\":\"$zone_id\",\"type\":\"A\",\"name\":\"test.frezbo.com\",\"content\":\"0.0.0.0\"}"



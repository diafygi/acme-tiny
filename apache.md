<VirtualHost *:80>
   ServerName www.yoursite.com
   ServerAlias yoursite.com

   Alias /.well-known/acme-challenge/ /usr/local/www/apache24/letsencrypt-challenges/
   <Directory /usr/local/www/apache24/letsencrypt-challenges>
      AllowOverride None
      Require all granted
      Satisfy Any
   </Directory>

   # rest of your config for this server
   # DocumentRoot, ErrorLog, CustomLog...
</VirtualHost>

<VirtualHost _default_:443>
   ServerName www.yoursite.com
   ServerAlias yoursite.com

   SSLEngine On
   SSLCertificateFile "/usr/local/etc/apache24/keys/domain.crt"
   SSLCertificateKeyFile "/usr/local/etc/apache24/keys/domain.key"
   # CA certificate from https://letsencrypt.org/certs/lets-encrypt-x1-cross-signed.pem
   SSLCertificateChainFile "/usr/local/etc/apache24/keys/lets-encrypt-x1-cross-signed.pem"

   # SSL config according to https://bettercrypto.org/static/applied-crypto-hardening.pdf
   SSLProtocol All -SSLv2 -SSLv3
   SSLHonorCipherOrder On
   SSLCompression Off
   Header always add Strict-Transport-Security "max-age=15768000"
   SSLCipherSuite 'EDH+CAMELLIA:EDH+aRSA:EECDH+aRSA+AESGCM:EECDH+aRSA+SHA384:EECDH+aRSA+SHA256:EECDH:+CAMELLIA256:+AES256:+CAMELLIA128:+AES128:+SSLv3:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!DSS:!RC4:!SEED:!ECDSA:CAMELLIA256-SHA:AES256-SHA:CAMELLIA128-SHA:AES128-SHA'
   BrowserMatch "MSIE [2-6]" nokeepalive ssl-unclean-shutdown downgrade-1.0 force-response-1.0
   BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown

   # rest of your SSL/TLS config
   # DocumentRoot, ErrorLog, CustomLog...
</VirtualHost>

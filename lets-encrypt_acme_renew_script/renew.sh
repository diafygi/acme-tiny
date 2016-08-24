#!/bin/bash
#Author: TechnoMan, mail: git@frezbo.com

#certificate file location
certs_location=/etc/nginx/ssl/certs
#domain keys location
keys_location=/etc/nginx/ssl/private
#file containing list of domains
domain_file=/usr/local/scripts/acme/domains.txt
#file containing CSR genreation parameters
csr_params=/usr/local/scripts/acme/domains.cnf
#intermediate certificate
int_cert=/usr/local/scripts/acme/intermediate.pem
#current unix time
curr_time=$(date +%s)
##set umask
#umask 335
#check whether certifcate expires within 30 days
for i in $(cat $domain_file)
do
#certifcate expiry unix time
((cert_expire_time=$(date -d "$(openssl x509 -in ${certs_location}/$i.crt -noout -enddate | sed s/notAfter=//g)" +%s)))
#days to expire
((days_to_expire=(cert_expire_time-curr_time)/86400))
if [ $days_to_expire -le 30 ]
then
echo "$days_to_expire days untill expiry"
openssl genrsa -out /usr/local/scripts/acme/$i.key 4096
sed -i "8!s/example.com/$i/g" $csr_params
openssl req -new -config $csr_params -key /usr/local/scripts/acme/$i.key -out /usr/local/scripts/acme/$i.csr
sed -i "8!s/$i/example.com/g" $csr_params
mv ${certs_location}/$i.crt ${certs_location}/$i.crt.old
mv /usr/local/scripts/acme/$i.key ${keys_location}
python acme-tiny/acme_tiny.py --account-key /usr/local/scripts/acme/technoman.key --csr /usr/local/scripts/acme/$i.csr --acme-dir /mnt/data/www/.well-known/acme-challenge > /usr/local/scripts/acme/$i.tmp.crt
cat /usr/local/scripts/acme/$i.tmp.crt $int_cert > ${certs_location}/$i.crt
rm /usr/local/scripts/acme/$i.tmp.crt
fi
done
sudo nginx -s reload

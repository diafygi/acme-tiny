#!/bin/bash
#Author: TechnoMan, mail: git@frezbo.com
document_root=/var/www/html # change to your document root
scripts_directory=/usr/local/scripts # scripts directory
acme_directory=acme-tiny/lets-encrypt_acme_renew_script
nginx_config_location=/etc/nginx #change if this is not your config directory
#certificate file location
certs_location=${nginx_config_location}/ssl/certs
#domain keys location
keys_location=${nginx_config_location}/ssl/private
#file containing list of domains
domain_file=${scripts_directory}/${acme_directory}/domains.txt
#file containing CSR genreation parameters
csr_params=${scripts_directory}/${acme_directory}/domains.cnf
#intermediate certificate
int_cert=${scripts_directory}/${acme_directory}/intermediate.pem
#current unix time
curr_time=$(date +%s)
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
openssl genrsa -out ${scripts_directory}/${acme_directory}/$i.key 4096
sed -i "8!s/example.com/$i/g" $csr_params
openssl req -new -config $csr_params -key ${scripts_directory}/${acme_directory}/$i.key -out ${scripts_directory}/${acme_directory}/$i.csr
sed -i "8!s/$i/example.com/g" $csr_params
mv ${certs_location}/$i.crt ${certs_location}/$i.crt.old
mv ${keys_location}/$i.key ${keys_location}/$i.key.old
mv ${scripts_directory}/${acme_directory}/$i.key ${keys_location}
python ${scripts_directory}/acme-tiny/acme_tiny.py --account-key ${scripts_directory}/${acme_directory}/priv.key --csr ${scripts_directory}/${acme_directory}/$i.csr --acme-dir ${document_root}/.well-known/acme-challenge > ${scripts_directory}/${acme_directory}/$i.tmp.crt
cat ${scripts_directory}/${acme_directory}/$i.tmp.crt $int_cert > ${certs_location}/$i.crt
rm ${scripts_directory}/${acme_directory}/$i.tmp.crt
rm ${scripts_directory}/${acme_directory}/$i.csr
fi
done
sudo nginx -s reload

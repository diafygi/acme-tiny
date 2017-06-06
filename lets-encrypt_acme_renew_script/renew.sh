#!/bin/bash
#Author: TechnoMan, mail: git@frezbo.com
tld="com" #set your domain extension, eg: com, edu, org etc
days_to_expire=30 #certificates are renewed before a month of expiry
document_root=/var/www/html # change to your document root
scripts_directory=/usr/local/scripts # scripts directory
acme_directory=acme-tiny/lets-encrypt_acme_renew_script
nginx_config_location=/etc/nginx #change if this is not your config directory
#certificate file location
#private key file
priv_key_file=priv.key
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
touch ${scripts_directory}/${acme_directory}/.rnd
export RANDFILE=${scripts_directory}/${acme_directory}/.rnd
#check whether certifcate expires within the days specified in days_to_expire
for i in $(cat $domain_file)
        do
        for cert_type in {ec,rsa}
                do
                if [ ! -e ${keys_location}/$i.$tld.$cert_type.key ]
                then
                        echo "$cert_type key file not found. Copy the $cert_type key file in $i.$tld.$cert_type.key format as specified in README to ${keys_location}"
                fi
                if [ -e ${certs_location}/$i.$tld.$cert_type.crt ]
                then
                        #certifcate expiry unix time
                        ((cert_expire_time=$(date -d "$(openssl x509 -in ${certs_location}/$i.$tld.$cert_type.crt -noout -enddate | sed s/notAfter=//g)" +%s)))
                        #days to expire
                        ((cert_days_untill_expiry=(cert_expire_time-curr_time)/86400))
                        if [ $cert_days_untill_expiry -le $days_to_expire ]
                        then
                                echo "$cert_days_untill_expiry days untill expiry for $cert_type cert"
                                if [ $cert_type == 'ec' ]
                                then
                                        openssl genrsa -out ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.key 4096
                                else
                                        openssl ecparam -genkey -name secp384r1 | openssl ec -out ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.key
                                fi
                                chmod 600 ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.key
                                sed -i "s/__DOMAIN__/$i.$tld/g" $csr_params
                                openssl req -new -config $csr_params -key ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.key -out ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.csr
                                sed -i "s/$i.$tld/__DOMAIN__/g" $csr_params
                                mv ${certs_location}/$i.$tld.$cert_type.crt ${certs_location}/$i.$tld.$cert_type.crt.old
                                mv ${keys_location}/$i.$tld.$cert_type.key ${keys_location}/$i.$tld.$cert_type.key.old
                                mv ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.key ${keys_location}
				python ${scripts_directory}/acme-tiny/acme_tiny.py --account-key ${scripts_directory}/${acme_directory}/$priv_key_file --csr ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.csr --acme-dir ${document_root}/.well-known/acme-challenge > ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.tmp.crt
                                cat ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.tmp.crt ${scripts_directory}/${acme_directory}/$int_cert > ${certs_location}/$i.$tld.$cert_type.crt
                                rm -f ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.tmp.crt
                                rm -f ${scripts_directory}/${acme_directory}/$i.$tld.$cert_type.csr
                        fi
                else
                        echo "$cert_type certificate file not found. Copy the $cert_type certificate file in $i.$tld.$cert_type.crt format as specified in README to ${certs_location}"
                fi
        done
done
rm -f ${scripts_directory}/${acme_directory}/.rnd
sudo nginx -s reload

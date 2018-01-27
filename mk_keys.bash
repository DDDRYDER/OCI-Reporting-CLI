#!/bin/bash
#
# Create OCI API and SSH keys
# ./mk_keys.bash ociapikey ocisshkey DDR26Jan2018
#
APIKEYNAME=$1
SSHKEYNAME=$2
SSH_COMMENT=$3

if [ -n "$APIKEYNAME" ]; then
# Generate API Keys
echo "Generating API key " $APIKEYNAME

openssl genrsa -out $APIKEYNAME.pem 2048
chmod 0600 $APIKEYNAME.pem
openssl rsa -pubout -in "$APIKEYNAME.pem" -out $APIKEYNAME"_pub.pem"
openssl rsa -pubout -outform DER -in "$APIKEYNAME.pem" | openssl md5 -c
openssl rsa -pubout -outform DER -in "$APIKEYNAME.pem" | openssl md5 -c > $APIKEYNAME"_fingerprint"

ls -al $KEYNAME*
fi

if [ -n "$SSHKEYNAME" ]; then
# Generate SSH Keys
echo "Generating SSH key " $SSHKEYNAME
ssh-keygen -t rsa -b 2048 -C $SSH_COMMENT -f $SSHKEYNAME -N ""
fi

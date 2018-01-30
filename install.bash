#!/bin/bash
#
# Install
#
PYTHON_VERSION=3.6.4

sudo yum update -y
sudo yum install git -y
sudo yum install python-devel gcc zlib-devel openssl openssl-devel -y

#wget https://bootstrap.pypa.io/get-pip.py
#sudo python get-pip.py

wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
tar xJf Python-$PYTHON_VERSION.tar.xz

cd Python-$PYTHON_VERSION
./configure
make
sudo make install
cd ..

sudo /usr/local/bin/pip3 install requests configparser

# Install Oracle  OCI Python SDK
sudo /usr/local/bin/pip3 install oci

git clone https://github.com/DDDRYDER/OCI-Reporting-CLI.git
git clone https://github.com/DDDRYDER/OCIC-Reporting-CLI.git

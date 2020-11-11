#!/bin/bash

apt-get update
apt-get -y upgrade
apt-get install python3 -y
apt-get install build-essential checkinstall -y
apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev -y

cd /opt
wget https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tgz
tar xzf Python-3.8.1.tgz
cd Python-3.8.1
./configure --enable-optimizations
make altinstall
update-alternatives --install /usr/bin/python python /usr/local/bin/python3.8 1

apt-get install curl -y
curl -sL https://deb.nodesource.com/setup_14.x | bash -
apt-get install nodejs -y
#!/bin/bash

set -e

echo
echo "========================================"
echo "Removing older packages"
echo "----------------------------------------"
sudo apt-get remove -y cmake
echo "----------------------------------------"

echo
echo "========================================"
echo "Update the CA certificates"
echo "----------------------------------------"
sudo apt-get install -y ca-certificates
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"

echo
echo "========================================"
echo "Remove the expire letsencrypt.org cert "
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"
sudo rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"


echo
echo "========================================"
echo "Host adding PPAs"
echo "----------------------------------------"
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | sudo apt-key add -
sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ xenial main'
sudo add-apt-repository ppa:openjdk-r/ppa
echo "----------------------------------------"

echo
echo "========================================"
echo "Host updating packages"
echo "----------------------------------------"
sudo apt-get update
echo "----------------------------------------"

echo
echo "========================================"
echo "Host remove packages"
echo "----------------------------------------"
sudo apt-get remove -y \
	python-pytest \


sudo apt-get autoremove -y

echo "----------------------------------------"
echo
echo "========================================"
echo "Host install packages"
echo "----------------------------------------"
sudo apt-get install -y \
        bash \
        bison \
        build-essential \
        ca-certificates \
        clang-format \
        cmake \
        colordiff \
        coreutils \
        curl \
        flex \
        git \
        graphviz \
        inkscape \
        jq \
        make \
        nodejs \
        psmisc \
        python \
        python3 \
        python3-dev \
        python3-virtualenv \
        python3-yaml \
        virtualenv \
        openjdk-11-jdk

if [ -z "${BUILD_TOOL}" ]; then
    export BUILD_TOOL=make
fi

echo "----------------------------------------"

echo
echo "========================================"
echo "Setting up conda environment"
echo "----------------------------------------"
(
	echo " Set JAVA 11 as default"
	echo "----------------------------------------"
	sudo update-alternatives --set java /usr/lib/jvm/java-11-openjdk-amd64/bin/java
	java -version
	echo "----------------------------------------"

	echo " Installing symbiflow and quicklogic"
	echo "----------------------------------------"
	make install_symbiflow
	make install_quicklogic
	make install_interchange
	echo "----------------------------------------"

	echo
	echo " Configuring conda environment"
	echo "----------------------------------------"
	TOOLCHAIN=symbiflow make env
	TOOLCHAIN=quicklogic make env
	TOOLCHAIN=nextpnr make env
	echo "----------------------------------------"
)

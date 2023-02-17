#!/bin/bash

# Update packages
sudo apt update -y
sudo apt upgrade -y

# Install Git
sudo apt install -y git

# Install docker environment and configure
echo "*** Installing Docker ***"

sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo apt install -y docker-compose

echo "*** Completed Installing Docker"

echo "*** Cloning Sources ***"
# Get application sources
mkdir workspace
cd workspace
git clone https://github.com/drac98/robot-shop.git
git clone https://github.com/drac98/bsc-fyp.git
echo "*** Source Cloning Complete ***"

# Create docker network for the applications
echo "*** Creating Docker Network ***"
sudo docker network create -d bridge robot-shop_robot-shop

cd robot-shop
git checkout response-time # Checkout to development branch
sudo docker-compose build # Build the docker images
cd ..

# Run docker containers of robot-shop, load generator and prometheus
echo "*** Starting Docker Containers ***"
sudo docker-compose -f bsc-fyp/monitoring/docker-compose.yml up & sudo docker-compose -f robot-shop/docker-compose.yaml up & sudo docker-compose -f robot-shop/docker-compose-load.yaml up &

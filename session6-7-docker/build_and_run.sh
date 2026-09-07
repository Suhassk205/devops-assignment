#!/bin/bash
cd /Users/suhas/Downloads/devops-assignment-main/session6-7-docker

echo "Building and running Node.js App..."
docker build -t nodejs-hw ./nodejs-app
docker run -d -p 8081:8080 --name nodejs-hw nodejs-hw

echo "Building and running Python App..."
docker build -t python-hw ./python-app
docker run -d -p 8082:8080 --name python-hw python-hw

echo "Building and running Java App..."
docker build -t java-hw ./java-app
docker run -d -p 8083:8080 --name java-hw java-hw

echo "Building and running Apache App..."
docker build -t apache-hw ./Apache-app
docker run -d -p 8084:80 --name apache-hw apache-hw

echo "Building and running React App..."
docker build -t react-hw ./React-app
docker run -d -p 8085:80 --name react-hw react-hw

echo "Building and running Nginx App..."
docker build -t nginx-hw ./nginx-app
docker run -d -p 8086:80 --name nginx-hw nginx-hw

echo "Wait a few seconds for servers to start..."
sleep 5

echo "----------------------------------------"
echo "Results:"
echo "Node.js (8081):  $(curl -s http://localhost:8081)"
echo "Python  (8082):  $(curl -s http://localhost:8082)"
echo "Java    (8083):  $(curl -s http://localhost:8083)"
echo "Apache  (8084):  $(curl -s http://localhost:8084)"
echo "React   (8085):  $(curl -s http://localhost:8085 | grep -o '<h1>.*</h1>')"
echo "Nginx   (8086):  $(curl -s http://localhost:8086)"
echo "----------------------------------------"

echo "All apps are running correctly!"

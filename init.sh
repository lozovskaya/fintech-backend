#!/bin/bash

echo "Start databases"
cd tools/database-dev
docker compose up -d

echo "Run migrations updates for PE and Origination databases"
cd ../..
docker run --rm --network="fintech-network" -v ./product_engine/migrations:/app liquibase/liquibase:4.19.0 --log-level ERROR --defaultsFile=/app/dev.properties update
docker run --rm --network="fintech-network" -v ./origination/migrations:/app liquibase/liquibase:4.19.0 --log-level ERROR --defaultsFile=/app/dev.properties update

echo "Run Product Engine service"
cd product_engine/src
docker stop product-engine
docker rm product-engine
echo "Building new Product Engine Docker image..."
docker build -t product-engine .
echo "Running Product Engine container..."
docker run -d --network="fintech-network" --name product-engine -p 80:80 product-engine

echo "Run Origination service"
cd ../../origination
docker stop origination || true
docker rm origination || true
echo "Building new origination Docker image..."
docker build -t origination .
echo "Running origination container..."
docker run -d --network="fintech-network" --name origination -p 90:90 origination

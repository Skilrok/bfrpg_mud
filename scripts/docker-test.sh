#!/bin/bash

# Script to test the Docker setup locally
# This will build the Docker image, spin up the containers with docker-compose,
# and run some basic health checks

set -e  # Exit on any error

echo "=== Building Docker images ==="
docker-compose build

echo "=== Starting containers ==="
docker-compose up -d

# Give services time to start
echo "=== Waiting for services to start ==="
sleep 10

echo "=== Checking API health ==="
curl -f http://localhost:8000/health || {
  echo "Health check failed!"
  docker-compose logs
  docker-compose down
  exit 1
}

echo "=== Testing authentication endpoint ==="
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password" || {
  echo "Auth endpoint check failed!"
  docker-compose logs
  docker-compose down
  exit 1
}

echo "=== Checking hirelings endpoint ==="
curl -f http://localhost:8000/api/hirelings/ -H "Authorization: Bearer test_token" || {
  echo "Hirelings endpoint check failed!"
  docker-compose logs
  docker-compose down
  exit 1
}

echo "=== All tests passed! ==="

# Cleanup
echo "=== Stopping containers ==="
docker-compose down

echo "Docker setup test completed successfully!" 
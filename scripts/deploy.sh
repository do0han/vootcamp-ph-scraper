#!/bin/bash

# Vootcamp PH Deployment Script
set -e

echo "🚀 Starting Vootcamp PH deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env.local exists
if [ ! -f .env.local ]; then
    print_warning ".env.local not found. Creating from .env.production template..."
    cp .env.production .env.local
    print_warning "Please edit .env.local with your production values before running again."
    exit 1
fi

# Build and start the application
print_status "Building Docker image..."
docker-compose build --no-cache

print_status "Starting application..."
docker-compose up -d

# Wait for health check
print_status "Waiting for application to be ready..."
sleep 10

# Check health
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        print_status "✅ Application is healthy and ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    print_status "Waiting for health check... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "❌ Health check failed after $MAX_ATTEMPTS attempts"
    print_error "Check logs: docker-compose logs app"
    exit 1
fi

print_status "🎉 Deployment completed successfully!"
print_status "🌐 Application is running at: http://localhost:3000"
print_status "📊 Health check: http://localhost:3000/api/health"

# Show running containers
print_status "Running containers:"
docker-compose ps
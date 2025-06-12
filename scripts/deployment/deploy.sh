#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_env_vars() {
    local required_vars=(
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_DB"
        "AIRFLOW_ADMIN_USER"
        "AIRFLOW_ADMIN_PASSWORD"
        "AIRFLOW_ADMIN_EMAIL"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        exit 1
    fi
}

# Function to check if required ports are available
check_ports() {
    local ports=(8080 5432 6379)
    for port in "${ports[@]}"; do
        if lsof -i :$port > /dev/null 2>&1; then
            print_error "Port $port is already in use"
            exit 1
        fi
    done
}

# Function to backup existing data
backup_data() {
    if [ -d "data" ]; then
        print_status "Backing up existing data..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        tar -czf "backup_${timestamp}.tar.gz" data/
    fi
}

# Function to deploy the application
deploy() {
    print_status "Starting deployment..."

    # Pull latest images
    print_status "Pulling latest Docker images..."
    docker-compose pull

    # Build images
    print_status "Building Docker images..."
    docker-compose build

    # Start services
    print_status "Starting services..."
    docker-compose up -d

    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30

    # Check if services are running
    print_status "Checking service health..."
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi

    print_status "Deployment completed successfully!"
}

# Function to perform health checks
health_check() {
    print_status "Performing health checks..."

    # Check Airflow webserver
    if ! curl -s http://localhost:8080/health | grep -q "healthy"; then
        print_error "Airflow webserver is not healthy"
        exit 1
    fi

    # Check PostgreSQL
    if ! docker-compose exec postgres pg_isready -U $POSTGRES_USER > /dev/null 2>&1; then
        print_error "PostgreSQL is not healthy"
        exit 1
    fi

    # Check Redis
    if ! docker-compose exec redis redis-cli ping | grep -q "PONG"; then
        print_error "Redis is not healthy"
        exit 1
    fi

    print_status "All health checks passed!"
}

# Main deployment process
main() {
    print_status "Starting deployment process..."

    # Perform pre-deployment checks
    check_env_vars
    check_docker
    check_ports
    backup_data

    # Deploy the application
    deploy

    # Perform health checks
    health_check

    print_status "Deployment process completed successfully!"
}

# Run main function
main 
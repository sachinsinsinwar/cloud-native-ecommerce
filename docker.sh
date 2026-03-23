#!/bin/bash

# =============================================================================
# Docker Quick Start Script
# Purpose: Simplified commands for common Docker operations
# =============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Function to check if .env exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f .env.docker ]; then
            cp .env.docker .env
            print_success "Created .env from .env.docker template"
            print_warning "⚠ Please edit .env and set your passwords!"
        else
            print_error ".env.docker template not found!"
            exit 1
        fi
    else
        print_success ".env file exists"
    fi
}

# Start services
start() {
    print_info "Starting all services..."
    check_docker
    check_env
    docker-compose up --build "$@"
}

# Stop services
stop() {
    print_info "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

# Restart services
restart() {
    print_info "Restarting all services..."
    stop
    start -d
}

# View logs
logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Check status
status() {
    print_info "Service Status:"
    docker-compose ps
    echo ""
    print_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Clean everything (⚠️ removes volumes)
clean() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" == "yes" ]; then
        print_info "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup complete"
    else
        print_info "Cancelled"
    fi
}

# Run tests
test() {
    print_info "Running tests..."
    
    # Test backend
    print_info "Testing backend..."
    curl -f http://localhost:5000/health || print_error "Backend health check failed"
    
    # Test frontend
    print_info "Testing frontend..."
    curl -f http://localhost:3000 || print_error "Frontend health check failed"
    
    # Test database
    print_info "Testing database..."
    docker-compose exec -T postgres psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM products;" || print_error "Database test failed"
    
    # Test Redis
    print_info "Testing Redis..."
    docker-compose exec -T redis redis-cli ping || print_error "Redis test failed"
    
    print_success "All tests passed!"
}

# Shell access
shell() {
    if [ -z "$1" ]; then
        print_error "Usage: ./docker.sh shell <service>"
        print_info "Available services: backend, frontend, postgres, redis"
        exit 1
    fi
    
    case "$1" in
        backend)
            docker-compose exec backend /bin/sh
            ;;
        frontend)
            docker-compose exec frontend /bin/sh
            ;;
        postgres)
            docker-compose exec postgres psql -U postgres -d ecommerce_db
            ;;
        redis)
            docker-compose exec redis redis-cli
            ;;
        *)
            print_error "Unknown service: $1"
            exit 1
            ;;
    esac
}

# Show help
help() {
    cat << EOF
Docker Quick Start Script for E-Commerce Application

Usage: ./docker.sh <command>

Commands:
    start       Start all services (detached: add -d flag)
    stop        Stop all services
    restart     Restart all services
    logs        View logs (optional: specify service name)
    status      Show service status and resource usage
    clean       Remove all containers, networks, and volumes
    test        Run health checks on all services
    shell       Open shell in container (usage: shell <service>)
    help        Show this help message

Examples:
    ./docker.sh start          # Start in foreground
    ./docker.sh start -d       # Start in background
    ./docker.sh logs backend   # View backend logs
    ./docker.sh shell postgres # Open PostgreSQL shell
    ./docker.sh status         # View all services
    ./docker.sh clean          # Clean everything

Services: backend, frontend, postgres, redis
EOF
}

# Main script logic
case "$1" in
    start)
        shift
        start "$@"
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$2"
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    test)
        test
        ;;
    shell)
        shell "$2"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac

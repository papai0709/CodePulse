#!/bin/bash

# CodePulse - Docker Management Script
# Build and run CodePulse using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🐳 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_warning "docker-compose not found. Trying 'docker compose'..."
        if ! docker compose version >/dev/null 2>&1; then
            print_error "Neither 'docker-compose' nor 'docker compose' is available."
            exit 1
        else
            DOCKER_COMPOSE="docker compose"
        fi
    else
        DOCKER_COMPOSE="docker-compose"
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building CodePulse Docker image..."
    docker build -t codepulse:latest .
    print_success "Docker image built successfully!"
}

# Function to run with docker-compose (production)
run_production() {
    print_status "Starting CodePulse in production mode..."
    $DOCKER_COMPOSE up -d
    print_success "CodePulse is running at http://localhost:5050"
    print_status "Use 'docker-compose logs -f' to view logs"
    print_status "Use 'docker-compose down' to stop"
}

# Function to run with docker-compose (development)
run_development() {
    print_status "Starting CodePulse in development mode..."
    $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
    print_success "CodePulse dev server is running at http://localhost:5050"
    print_status "Code changes will be reflected automatically"
    print_status "Use 'docker-compose -f docker-compose.dev.yml logs -f' to view logs"
    print_status "Use 'docker-compose -f docker-compose.dev.yml down' to stop"
}

# Function to run standalone container
run_standalone() {
    print_status "Running CodePulse as standalone container..."
    
    # Stop existing container if running
    docker stop codepulse-standalone 2>/dev/null || true
    docker rm codepulse-standalone 2>/dev/null || true
    
    # Run new container
    docker run -d \
        --name codepulse-standalone \
        -p 5050:5050 \
        --env-file .env 2>/dev/null || \
        codepulse:latest
    
    print_success "CodePulse is running at http://localhost:5050"
    print_status "Use 'docker logs -f codepulse-standalone' to view logs"
    print_status "Use 'docker stop codepulse-standalone' to stop"
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all CodePulse containers..."
    
    # Stop docker-compose services
    $DOCKER_COMPOSE down 2>/dev/null || true
    $DOCKER_COMPOSE -f docker-compose.dev.yml down 2>/dev/null || true
    
    # Stop standalone container
    docker stop codepulse-standalone 2>/dev/null || true
    docker rm codepulse-standalone 2>/dev/null || true
    
    print_success "All CodePulse containers stopped"
}

# Function to show logs
show_logs() {
    if docker ps | grep -q codepulse-app; then
        print_status "Showing production logs..."
        $DOCKER_COMPOSE logs -f
    elif docker ps | grep -q codepulse-dev; then
        print_status "Showing development logs..."
        $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f
    elif docker ps | grep -q codepulse-standalone; then
        print_status "Showing standalone logs..."
        docker logs -f codepulse-standalone
    else
        print_warning "No CodePulse containers are currently running"
    fi
}

# Function to show status
show_status() {
    print_status "CodePulse Container Status:"
    echo ""
    
    if docker ps | grep -q codepulse; then
        docker ps | grep codepulse
        echo ""
        print_success "CodePulse is running at http://localhost:5050"
    else
        print_warning "No CodePulse containers are currently running"
    fi
}

# Function to clean up
cleanup() {
    print_status "Cleaning up CodePulse Docker resources..."
    
    # Stop and remove containers
    stop_all
    
    # Remove images (optional)
    read -p "Do you want to remove CodePulse Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi codepulse:latest 2>/dev/null || true
        print_success "Docker images removed"
    fi
    
    # Remove volumes (optional)
    read -p "Do you want to remove Docker volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_success "Docker volumes cleaned"
    fi
}

# Main script
main() {
    echo "🐳 CodePulse Docker Management"
    echo "=============================="
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    case "${1:-help}" in
        "build")
            build_image
            ;;
        "run"|"start")
            build_image
            run_production
            ;;
        "dev")
            build_image
            run_development
            ;;
        "standalone")
            build_image
            run_standalone
            ;;
        "stop")
            stop_all
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "restart")
            stop_all
            sleep 2
            build_image
            run_production
            ;;
        "clean")
            cleanup
            ;;
        "help"|*)
            echo "Usage: $0 {build|run|dev|standalone|stop|logs|status|restart|clean|help}"
            echo ""
            echo "Commands:"
            echo "  build      - Build the Docker image"
            echo "  run/start  - Build and run in production mode (docker-compose)"
            echo "  dev        - Build and run in development mode (with live reload)"
            echo "  standalone - Build and run as standalone container"
            echo "  stop       - Stop all CodePulse containers"
            echo "  logs       - Show logs from running containers"
            echo "  status     - Show container status"
            echo "  restart    - Stop, rebuild, and start"
            echo "  clean      - Clean up containers, images, and volumes"
            echo "  help       - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 run          # Start in production mode"
            echo "  $0 dev          # Start in development mode"
            echo "  $0 logs         # View logs"
            echo "  $0 stop         # Stop all containers"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
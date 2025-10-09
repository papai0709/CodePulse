#!/bin/bash

# CodePulse - Docker Management Script
# Comprehensive Docker orchestration for CodePulse application

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
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

# Function to ensure we're in the right directory
ensure_project_root() {
    if [ ! -f "$PROJECT_ROOT/app.py" ]; then
        print_error "app.py not found. Please run this script from the CodePulse project directory."
        exit 1
    fi
    cd "$PROJECT_ROOT"
}

# Function to check environment file
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found."
        if [ -f ".env.docker" ]; then
            print_info "Found .env.docker template. Creating .env from template..."
            cp .env.docker .env
            print_success "Created .env file from template. Please update with your values."
        else
            print_warning "No environment template found. Some features may not work."
        fi
    fi
}

# Function to build the Docker image
build_image() {
    local dockerfile=${1:-"docker/Dockerfile"}
    local tag=${2:-"codepulse:latest"}
    
    print_status "Building CodePulse Docker image using $dockerfile..."
    
    if docker build -f "$dockerfile" -t "$tag" .; then
        print_success "Docker image '$tag' built successfully!"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run with docker-compose (production)
run_production() {
    print_status "Starting CodePulse in production mode..."
    
    cd "$DOCKER_DIR"
    if $DOCKER_COMPOSE up -d; then
        print_success "CodePulse is running at http://localhost:5050"
        print_info "Use '$DOCKER_COMPOSE logs -f' to view logs"
        print_info "Use '$DOCKER_COMPOSE down' to stop"
        show_status
    else
        print_error "Failed to start CodePulse in production mode"
        exit 1
    fi
}

# Function to run with docker-compose (development)
run_development() {
    print_status "Starting CodePulse in development mode..."
    
    cd "$DOCKER_DIR"
    if $DOCKER_COMPOSE -f docker-compose.dev.yml up -d; then
        print_success "CodePulse dev server is running at http://localhost:5050"
        print_info "Code changes will be reflected automatically"
        print_info "Use '$DOCKER_COMPOSE -f docker-compose.dev.yml logs -f' to view logs"
        print_info "Use '$DOCKER_COMPOSE -f docker-compose.dev.yml down' to stop"
        show_status
    else
        print_error "Failed to start CodePulse in development mode"
        exit 1
    fi
}

# Function to run standalone container
run_standalone() {
    print_status "Running CodePulse as standalone container..."
    
    # Stop existing container if running
    docker stop codepulse-standalone 2>/dev/null || true
    docker rm codepulse-standalone 2>/dev/null || true
    
    # Build image first
    build_image "docker/Dockerfile" "codepulse:latest"
    
    # Run new container
    local run_cmd="docker run -d \
        --name codepulse-standalone \
        -p 5050:5050"
    
    # Add env file if it exists
    if [ -f ".env" ]; then
        run_cmd="$run_cmd --env-file .env"
    fi
    
    run_cmd="$run_cmd codepulse:latest"
    
    if eval $run_cmd; then
        print_success "CodePulse is running at http://localhost:5050"
        print_info "Use 'docker logs -f codepulse-standalone' to view logs"
        print_info "Use 'docker stop codepulse-standalone' to stop"
        show_status
    else
        print_error "Failed to start standalone container"
        exit 1
    fi
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all CodePulse containers..."
    
    cd "$DOCKER_DIR"
    
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
    cd "$DOCKER_DIR"
    
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
    print_header "CodePulse Container Status"
    echo "==============================="
    
    local running_containers=$(docker ps --filter "name=codepulse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")
    
    if [ -n "$running_containers" ]; then
        echo "$running_containers"
        echo ""
        print_success "CodePulse is accessible at:"
        print_info "🌐 Local: http://localhost:5050"
        print_info "🌐 Network: http://$(hostname -I | awk '{print $1}'):5050"
    else
        print_warning "No CodePulse containers are currently running"
    fi
    
    echo "==============================="
}

# Function to clean up
cleanup() {
    print_status "Cleaning up CodePulse Docker resources..."
    
    # Stop containers first
    stop_all
    
    # Remove images (optional)
    read -p "Do you want to remove CodePulse Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi codepulse:latest codepulse:dev 2>/dev/null || true
        print_success "Docker images removed"
    fi
    
    # Remove volumes (optional)
    read -p "Do you want to remove Docker volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_success "Docker volumes cleaned"
    fi
    
    # Remove networks (optional)
    read -p "Do you want to remove Docker networks? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker network prune -f
        print_success "Docker networks cleaned"
    fi
}

# Function to pull latest updates
update() {
    print_status "Updating CodePulse Docker setup..."
    
    # Stop containers
    stop_all
    
    # Rebuild images
    build_image "docker/Dockerfile" "codepulse:latest"
    build_image "docker/Dockerfile.dev" "codepulse:dev"
    
    print_success "Update completed. Use 'run' or 'dev' to start the updated application."
}

# Function to show system info
system_info() {
    print_header "CodePulse Docker System Information"
    echo "==============================="
    
    echo "📁 Project Root: $PROJECT_ROOT"
    echo "🐳 Docker Dir: $DOCKER_DIR"
    echo "🔧 Docker Compose: $DOCKER_COMPOSE"
    echo ""
    
    print_info "Docker Version:"
    docker version --format "{{.Server.Version}}"
    
    print_info "Docker Compose Version:"
    $DOCKER_COMPOSE version --short
    
    echo ""
    print_info "Available Images:"
    docker images | grep codepulse || echo "No CodePulse images found"
    
    echo ""
    print_info "Running Containers:"
    docker ps --filter "name=codepulse" || echo "No CodePulse containers running"
    
    echo "==============================="
}

# Main script
main() {
    print_header "CodePulse Docker Management v2.0"
    echo "==============================="
    
    # Check prerequisites
    check_docker
    check_docker_compose
    ensure_project_root
    check_env_file
    
    case "${1:-help}" in
        "build")
            build_image "docker/Dockerfile" "codepulse:latest"
            ;;
        "build-dev")
            build_image "docker/Dockerfile.dev" "codepulse:dev"
            ;;
        "run"|"start"|"prod")
            build_image "docker/Dockerfile" "codepulse:latest"
            run_production
            ;;
        "dev"|"development")
            build_image "docker/Dockerfile.dev" "codepulse:dev"
            run_development
            ;;
        "standalone")
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
            build_image "docker/Dockerfile" "codepulse:latest"
            run_production
            ;;
        "update")
            update
            ;;
        "clean")
            cleanup
            ;;
        "info")
            system_info
            ;;
        "help"|*)
            echo "Usage: $0 {command}"
            echo ""
            echo "🔧 Build Commands:"
            echo "  build       - Build production Docker image"
            echo "  build-dev   - Build development Docker image"
            echo ""
            echo "🚀 Run Commands:"
            echo "  run/start   - Build and run in production mode"
            echo "  dev         - Build and run in development mode"
            echo "  standalone  - Build and run as standalone container"
            echo ""
            echo "📊 Management Commands:"
            echo "  stop        - Stop all CodePulse containers"
            echo "  restart     - Stop, rebuild, and start production"
            echo "  logs        - Show logs from running containers"
            echo "  status      - Show container status"
            echo ""
            echo "🧹 Maintenance Commands:"
            echo "  update      - Update images and restart"
            echo "  clean       - Clean up containers, images, and volumes"
            echo "  info        - Show system information"
            echo "  help        - Show this help message"
            echo ""
            echo "📖 Examples:"
            echo "  $0 run      # Start in production mode"
            echo "  $0 dev      # Start in development mode"
            echo "  $0 logs     # View logs"
            echo "  $0 status   # Check running containers"
            echo "  $0 clean    # Clean up everything"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
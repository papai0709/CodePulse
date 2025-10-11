#!/bin/bash

# CodePulse Docker Quick Start Script
# Convenience script to run Docker from project root

echo "🐳 Starting CodePulse with Docker"
echo "=================================="

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Change to docker directory and run
cd docker

case "${1:-up}" in
    "up"|"start")
        echo "🚀 Starting CodePulse in detached mode..."
        docker compose up -d
        ;;
    "logs")
        echo "📋 Showing CodePulse logs..."
        docker compose logs -f
        ;;
    "stop")
        echo "🛑 Stopping CodePulse..."
        
        # Stop Docker containers
        docker compose down
        
        # Also kill any non-Docker processes on port 5050
        echo "🔍 Checking for processes on port 5050..."
        PORT_PIDS=$(lsof -ti :5050 2>/dev/null || true)
        if [ ! -z "$PORT_PIDS" ]; then
            echo "🛑 Stopping processes on port 5050: $PORT_PIDS"
            kill -9 $PORT_PIDS 2>/dev/null || true
        fi
        
        echo "✅ CodePulse stopped!"
        ;;
    "restart")
        echo "🔄 Restarting CodePulse..."
        docker compose down
        docker compose up -d
        ;;
    "status")
        echo "📊 CodePulse status:"
        echo ""
        echo "🐳 Docker containers:"
        docker compose ps
        echo ""
        echo "🔍 Processes on port 5050:"
        lsof -i :5050 2>/dev/null || echo "   No processes found on port 5050"
        echo ""
        echo "🌐 Port accessibility test:"
        curl -s --max-time 2 "http://localhost:5050" >/dev/null && echo "   ✅ Application responding on http://localhost:5050" || echo "   ❌ Application not responding on http://localhost:5050"
        ;;
    "clean")
        echo "🧹 Cleaning up Docker resources and processes..."
        
        # Stop Docker containers
        docker compose down --rmi all --volumes
        
        # Kill any remaining CodePulse processes on port 5050
        echo "🔍 Checking for processes on port 5050..."
        PORT_PIDS=$(lsof -ti :5050 2>/dev/null || true)
        if [ ! -z "$PORT_PIDS" ]; then
            echo "🛑 Stopping processes on port 5050: $PORT_PIDS"
            kill -9 $PORT_PIDS 2>/dev/null || true
        fi
        
        # Additional cleanup for any CodePulse processes
        echo "🔍 Checking for CodePulse Python processes..."
        CODEPULSE_PIDS=$(ps aux | grep -E "python.*app\.py" | grep -v grep | awk '{print $2}' 2>/dev/null || true)
        if [ ! -z "$CODEPULSE_PIDS" ]; then
            echo "🛑 Stopping CodePulse processes: $CODEPULSE_PIDS"
            kill -9 $CODEPULSE_PIDS 2>/dev/null || true
        fi
        
        echo "✅ Cleanup completed!"
        ;;
    *)
        echo "Usage: $0 {up|start|logs|stop|restart|status|clean}"
        echo ""
        echo "Commands:"
        echo "  up/start  - Start CodePulse (default)"
        echo "  logs      - Show live logs"
        echo "  stop      - Stop CodePulse (Docker + any processes on port 5050)"
        echo "  restart   - Restart CodePulse"
        echo "  status    - Show comprehensive status (containers, processes, connectivity)"
        echo "  clean     - Stop and remove everything (containers, images, processes)"
        exit 1
        ;;
esac

# Show status after up/start
if [[ "${1:-up}" == "up" ]] || [[ "$1" == "start" ]]; then
    echo ""
    echo "✅ CodePulse is running!"
    echo "🌐 Access the application at: http://localhost:5050"
    echo "📊 Container status:"
    docker compose ps
    echo ""
    echo "💡 Use './docker-quick.sh logs' to view logs"
    echo "💡 Use './docker-quick.sh stop' to stop the application"
fi
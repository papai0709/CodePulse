@echo off
REM CodePulse - Docker Management Script for Windows
REM Build and run CodePulse using Docker

setlocal enabledelayedexpansion

REM Function to print status messages
:print_status
echo 🐳 %~1
exit /b

:print_success
echo ✅ %~1
exit /b

:print_warning
echo ⚠️  %~1
exit /b

:print_error
echo ❌ %~1
exit /b

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker is not running. Please start Docker and try again."
    pause
    exit /b 1
)
exit /b

REM Function to check docker-compose
:check_docker_compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :print_warning "docker-compose not found. Trying 'docker compose'..."
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        call :print_error "Neither 'docker-compose' nor 'docker compose' is available."
        pause
        exit /b 1
    ) else (
        set DOCKER_COMPOSE=docker compose
    )
) else (
    set DOCKER_COMPOSE=docker-compose
)
exit /b

REM Function to build Docker image
:build_image
call :print_status "Building CodePulse Docker image..."
docker build -t codepulse:latest .
if %errorlevel% equ 0 (
    call :print_success "Docker image built successfully!"
) else (
    call :print_error "Failed to build Docker image"
    pause
    exit /b 1
)
exit /b

REM Function to run production mode
:run_production
call :print_status "Starting CodePulse in production mode..."
%DOCKER_COMPOSE% up -d
if %errorlevel% equ 0 (
    call :print_success "CodePulse is running at http://localhost:5050"
    call :print_status "Use 'docker-compose logs -f' to view logs"
    call :print_status "Use 'docker-compose down' to stop"
) else (
    call :print_error "Failed to start CodePulse"
)
exit /b

REM Function to run development mode
:run_development
call :print_status "Starting CodePulse in development mode..."
%DOCKER_COMPOSE% -f docker-compose.dev.yml up -d
if %errorlevel% equ 0 (
    call :print_success "CodePulse dev server is running at http://localhost:5050"
    call :print_status "Code changes will be reflected automatically"
    call :print_status "Use 'docker-compose -f docker-compose.dev.yml logs -f' to view logs"
    call :print_status "Use 'docker-compose -f docker-compose.dev.yml down' to stop"
) else (
    call :print_error "Failed to start CodePulse in development mode"
)
exit /b

REM Function to run standalone
:run_standalone
call :print_status "Running CodePulse as standalone container..."

REM Stop existing container if running
docker stop codepulse-standalone >nul 2>&1
docker rm codepulse-standalone >nul 2>&1

REM Run new container
docker run -d --name codepulse-standalone -p 5050:5050 --env-file .env codepulse:latest >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "CodePulse is running at http://localhost:5050"
    call :print_status "Use 'docker logs -f codepulse-standalone' to view logs"
    call :print_status "Use 'docker stop codepulse-standalone' to stop"
) else (
    REM Try without env file
    docker run -d --name codepulse-standalone -p 5050:5050 codepulse:latest
    if %errorlevel% equ 0 (
        call :print_success "CodePulse is running at http://localhost:5050"
        call :print_warning "Started without .env file"
    ) else (
        call :print_error "Failed to start standalone container"
    )
)
exit /b

REM Function to stop all containers
:stop_all
call :print_status "Stopping all CodePulse containers..."

%DOCKER_COMPOSE% down >nul 2>&1
%DOCKER_COMPOSE% -f docker-compose.dev.yml down >nul 2>&1
docker stop codepulse-standalone >nul 2>&1
docker rm codepulse-standalone >nul 2>&1

call :print_success "All CodePulse containers stopped"
exit /b

REM Function to show logs
:show_logs
docker ps | findstr codepulse-app >nul
if %errorlevel% equ 0 (
    call :print_status "Showing production logs..."
    %DOCKER_COMPOSE% logs -f
    exit /b
)

docker ps | findstr codepulse-dev >nul
if %errorlevel% equ 0 (
    call :print_status "Showing development logs..."
    %DOCKER_COMPOSE% -f docker-compose.dev.yml logs -f
    exit /b
)

docker ps | findstr codepulse-standalone >nul
if %errorlevel% equ 0 (
    call :print_status "Showing standalone logs..."
    docker logs -f codepulse-standalone
    exit /b
)

call :print_warning "No CodePulse containers are currently running"
exit /b

REM Function to show status
:show_status
call :print_status "CodePulse Container Status:"
echo.

docker ps | findstr codepulse >nul
if %errorlevel% equ 0 (
    docker ps | findstr codepulse
    echo.
    call :print_success "CodePulse is running at http://localhost:5050"
) else (
    call :print_warning "No CodePulse containers are currently running"
)
exit /b

REM Main script
echo 🐳 CodePulse Docker Management
echo ==============================

REM Check prerequisites
call :check_docker
call :check_docker_compose

if "%1"=="build" (
    call :build_image
) else if "%1"=="run" (
    call :build_image
    call :run_production
) else if "%1"=="start" (
    call :build_image
    call :run_production
) else if "%1"=="dev" (
    call :build_image
    call :run_development
) else if "%1"=="standalone" (
    call :build_image
    call :run_standalone
) else if "%1"=="stop" (
    call :stop_all
) else if "%1"=="logs" (
    call :show_logs
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="restart" (
    call :stop_all
    timeout /t 2 /nobreak >nul
    call :build_image
    call :run_production
) else (
    echo Usage: %0 {build^|run^|dev^|standalone^|stop^|logs^|status^|restart^|help}
    echo.
    echo Commands:
    echo   build      - Build the Docker image
    echo   run/start  - Build and run in production mode ^(docker-compose^)
    echo   dev        - Build and run in development mode ^(with live reload^)
    echo   standalone - Build and run as standalone container
    echo   stop       - Stop all CodePulse containers
    echo   logs       - Show logs from running containers
    echo   status     - Show container status
    echo   restart    - Stop, rebuild, and start
    echo   help       - Show this help message
    echo.
    echo Examples:
    echo   %0 run          # Start in production mode
    echo   %0 dev          # Start in development mode
    echo   %0 logs         # View logs
    echo   %0 stop         # Stop all containers
)

pause
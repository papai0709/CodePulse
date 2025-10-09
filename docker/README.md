# CodePulse Docker Documentation 🐳

Complete Docker setup for CodePulse - AI-Enhanced GitHub Repository Analyzer with production-ready containerization.

## 📁 Docker Structure

```
docker/
├── Dockerfile                 # Production Docker image
├── Dockerfile.dev            # Development Docker image  
├── docker-compose.yml        # Production orchestration
├── docker-compose.dev.yml    # Development orchestration
├── docker-manage.sh          # Comprehensive management script (Linux/Mac)
├── docker-run.sh             # Simple run script (Linux/Mac)
├── docker-run.bat            # Simple run script (Windows)
├── .dockerignore             # Docker ignore patterns
├── .env.docker               # Environment template
└── README.md                 # This documentation
```

## 🚀 Quick Start

### Option 1: Using Management Script (Recommended)
```bash
# Linux/Mac - Full featured management
./docker/docker-manage.sh run    # Production mode
./docker/docker-manage.sh dev    # Development mode
./docker/docker-manage.sh status # Check status
./docker/docker-manage.sh stop   # Stop all containers
```

### Option 2: Using Simple Scripts
```bash
# Linux/Mac
./docker/docker-run.sh run

# Windows
docker\docker-run.bat run
```

### Option 3: Direct Docker Commands
```bash
# Build and run with docker-compose
cd docker/
docker-compose up -d

# Or build and run standalone
docker build -f docker/Dockerfile -t codepulse .
docker run -p 5050:5050 --env-file .env codepulse
```

## 🔧 Configuration

### Environment Setup
1. **Copy environment template**:
   ```bash
   cp docker/.env.docker .env
   ```

2. **Edit `.env` with your values**:
   ```bash
   GITHUB_TOKEN=your_github_token_here
   SECRET_KEY=your-secure-secret-key
   LOG_LEVEL=INFO
   ```

### Required Environment Variables
- `GITHUB_TOKEN` - GitHub API token (required for AI features and private repos)
- `SECRET_KEY` - Flask secret key for session security
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## 🏗️ Build Options

### Production Build
```bash
# Using management script
./docker/docker-manage.sh build

# Using docker directly
docker build -f docker/Dockerfile -t codepulse:latest .
```

### Development Build
```bash
# Using management script
./docker/docker-manage.sh build-dev

# Using docker directly
docker build -f docker/Dockerfile.dev -t codepulse:dev .
```

## 🚦 Running Modes

### 1. Production Mode
- **Optimized**: Minimal image size, security hardened
- **Features**: Health checks, logging, restart policies
- **Usage**: `./docker/docker-manage.sh run`
- **Access**: http://localhost:5050

**Characteristics:**
- Non-root user execution
- Production-ready logging
- Health monitoring
- Automatic restarts
- Volume persistence

### 2. Development Mode
- **Features**: Live code reloading, debugging support
- **Usage**: `./docker/docker-manage.sh dev`
- **Access**: http://localhost:5050

**Characteristics:**
- Source code mounted as volume
- Debug mode enabled
- Extended timeouts
- Development tools included

### 3. Standalone Mode
- **Simple**: Single container without orchestration
- **Usage**: `./docker/docker-manage.sh standalone`
- **Best for**: Testing, demos, simple deployments

## 📊 Management Commands

### Container Operations
```bash
# Start services
./docker/docker-manage.sh run        # Production
./docker/docker-manage.sh dev        # Development
./docker/docker-manage.sh standalone # Standalone

# Monitor and control
./docker/docker-manage.sh status     # Show status
./docker/docker-manage.sh logs       # View logs
./docker/docker-manage.sh stop       # Stop all
./docker/docker-manage.sh restart    # Restart production

# Maintenance
./docker/docker-manage.sh update     # Update and rebuild
./docker/docker-manage.sh clean      # Clean up resources
./docker/docker-manage.sh info       # System information
```

### Manual Docker Commands
```bash
# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Enter container
docker exec -it codepulse-app bash

# Check health
docker inspect codepulse-app | grep Health

# Resource usage
docker stats codepulse-app
```

## 🔍 Monitoring & Debugging

### Health Checks
All containers include health checks:
- **Endpoint**: `http://localhost:5050/`
- **Interval**: 30s (production), 60s (development)
- **Timeout**: 10s (production), 30s (development)
- **Retries**: 3 attempts

### Logging
- **Production**: JSON format, rotated logs (10MB, 3 files)
- **Development**: Verbose logging with debug info
- **Access**: `./docker/docker-manage.sh logs`

### Debug Container Access
```bash
# Production container
docker exec -it codepulse-app bash

# Development container
docker exec -it codepulse-dev bash

# Check processes
docker exec -it codepulse-app ps aux

# View environment
docker exec -it codepulse-app env
```

## 🌐 Network & Ports

### Port Mapping
- **5050**: Main application (HTTP)
- **5555**: Debug port (development only)

### Networks
- **Production**: `codepulse-network` (172.20.0.0/16)
- **Development**: `codepulse-dev-network` (172.21.0.0/16)

### External Access
- **Local**: http://localhost:5050
- **Network**: http://[host-ip]:5050

## 💾 Volumes & Persistence

### Production Volumes
- `codepulse-logs`: Application logs
- `codepulse-static`: Static assets (if nginx enabled)

### Development Volumes
- Source code: Live mounted for hot reloading
- `codepulse-dev-cache`: Python cache isolation
- `codepulse-dev-logs`: Development logs

### Data Backup
```bash
# Backup logs
docker run --rm -v codepulse-logs:/data -v $(pwd):/backup alpine tar czf /backup/logs-backup.tar.gz /data

# Restore logs
docker run --rm -v codepulse-logs:/data -v $(pwd):/backup alpine tar xzf /backup/logs-backup.tar.gz -C /
```

## 🔒 Security Features

### Production Security
- **Non-root execution**: User `codepulse` (UID 1001)
- **Minimal base image**: Python 3.12-slim
- **Security scanning**: Built-in health checks
- **Resource limits**: Memory and CPU constraints
- **Network isolation**: Dedicated Docker networks

### Environment Security
- **Secret management**: Environment variables only
- **File permissions**: Restricted access patterns
- **Container isolation**: No privileged mode

## ⚡ Performance Optimization

### Image Optimization
- **Multi-stage builds**: Minimal final image
- **Layer caching**: Optimized Dockerfile order
- **Dependencies**: Cached pip installations
- **Size**: ~200MB production image

### Runtime Optimization
- **Health checks**: Early problem detection
- **Resource limits**: Prevent resource exhaustion
- **Logging**: Structured JSON logs
- **Networking**: Optimized for container communication

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 5050
lsof -i :5050
# Or kill the process
./docker/docker-manage.sh stop
```

#### Permission Issues
```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
# Logout and login again
```

#### Container Won't Start
```bash
# Check logs
./docker/docker-manage.sh logs

# Check container status
docker ps -a

# Inspect container
docker inspect codepulse-app
```

#### Environment Variables Not Loading
```bash
# Verify .env file exists
ls -la .env

# Check environment inside container
docker exec -it codepulse-app env | grep GITHUB
```

### Debug Mode
Enable debug mode for detailed troubleshooting:
```bash
# Development mode with verbose logging
./docker/docker-manage.sh dev

# Check debug logs
docker logs -f codepulse-dev
```

## 🚀 Production Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 5GB disk space

### Deployment Steps
1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd CodePulse
   ```

2. **Configure environment**:
   ```bash
   cp docker/.env.docker .env
   # Edit .env with production values
   ```

3. **Deploy**:
   ```bash
   ./docker/docker-manage.sh run
   ```

4. **Verify deployment**:
   ```bash
   ./docker/docker-manage.sh status
   curl http://localhost:5050
   ```

### Production Checklist
- [ ] Environment variables configured
- [ ] GitHub token provided
- [ ] Secret key set
- [ ] Health checks passing
- [ ] Logs rotating properly
- [ ] Backup strategy in place
- [ ] Monitoring configured

## 📈 Scaling & Extensions

### Horizontal Scaling
```yaml
# Add to docker-compose.yml
services:
  codepulse:
    scale: 3
    deploy:
      replicas: 3
```

### Load Balancing
Uncomment nginx section in `docker-compose.yml` for load balancing.

### Additional Services
The compose files include commented sections for:
- Redis caching
- PostgreSQL database  
- Nginx reverse proxy

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [CodePulse Application Documentation](../README.md)

---

**Happy Containerizing! 🐳🚀**
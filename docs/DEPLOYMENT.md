# Multi-Platform Deployment Guide

## Supported Platforms

The Docker images support the following platforms:
- **Linux/AMD64** - Intel/AMD processors (most servers, PCs)
- **Linux/ARM64** - Apple Silicon (M1/M2/M3), ARM servers
- **Linux/ARM/v7** - Raspberry Pi

## Local Development

```bash
# Clone repository
git clone https://github.com/jojospausch-web/openredact-app.git
cd openredact-app

# Build and run (automatically uses your platform)
docker-compose build
docker-compose up
```

The application will be available at:
- Frontend: http://localhost/
- Backend API: http://localhost/api
- API Documentation: http://localhost:8000/docs

## Production Distribution

### Option 1: Docker Hub (Public)

```bash
# Setup buildx
docker buildx create --name multiplatform --use

# Build and push multi-platform images
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag yourusername/openredact-backend:latest \
  --tag yourusername/openredact-backend:v1.0.0 \
  --push \
  backend/

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag yourusername/openredact-frontend:latest \
  --tag yourusername/openredact-frontend:v1.0.0 \
  --push \
  frontend/
```

### Option 2: GitHub Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/jojospausch-web/openredact-backend:latest \
  --push \
  backend/

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/jojospausch-web/openredact-frontend:latest \
  --push \
  frontend/
```

## Using Pre-Built Images

For users who want to use pre-built images instead of building themselves, create a `docker-compose.yml` file:

```yaml
version: '3.7'

services:
  backend:
    image: yourusername/openredact-backend:latest  # Pre-built multi-platform
    ports:
      - "8000:8000"
    volumes:
      - openredact-storage:/app/storage

  frontend:
    image: yourusername/openredact-frontend:latest  # Pre-built multi-platform
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  openredact-storage:
```

Then simply run:

```bash
docker-compose pull
docker-compose up
```

## Platform Compatibility Matrix

| Platform | CPU Architecture | Status | Notes |
|----------|-----------------|--------|-------|
| Windows 10/11 (Docker Desktop) | Intel/AMD | ✅ Supported | Requires WSL2 |
| macOS Intel | x86_64 | ✅ Supported | |
| macOS Apple Silicon | ARM64 | ✅ Supported | M1/M2/M3 |
| Linux Server | Intel/AMD | ✅ Supported | |
| Linux ARM Server | ARM64 | ✅ Supported | |
| Raspberry Pi 4 | ARMv7 | ✅ Supported | Requires 4GB+ RAM |

## Technical Details

### Base Images
- **Backend**: `python:3.9-bullseye` - Debian Bullseye with Python 3.9
- **Frontend**: `node:14-alpine` (build) + `nginx:alpine` (runtime)

### Why Debian Bullseye?
- ✅ Stable and well-tested
- ✅ wkhtmltopdf available in standard repositories
- ✅ Multi-architecture support (amd64, arm64, armhf)
- ✅ Python 3.9 compatibility
- ✅ Modern numpy 2.x and spacy 3.8.x support

### Dependencies
The backend image includes:
- **wkhtmltopdf** - PDF generation
- **poppler-utils** - PDF text extraction
- **PyTorch** - Deep learning framework
- **spaCy** - NLP library with German language model
- **Stanza** - Stanford NLP toolkit with German model

## Troubleshooting

### Docker Build Issues

**Issue**: `Package 'wkhtmltopdf' has no installation candidate`

**Solution**: Ensure you're using `python:3.9-bullseye` and not `python:3.9` (which uses Debian Trixie where wkhtmltopdf is unavailable).

### Memory Issues

**Issue**: Container crashes or runs out of memory

**Solution**: Increase Docker memory allocation:
- **Docker Desktop**: Settings → Resources → Memory (recommend 4GB+)
- **Linux**: No limit by default, but ensure sufficient system RAM

### Platform-Specific Issues

**macOS Apple Silicon (M1/M2/M3)**:
- Use Docker Desktop 4.0+ for native ARM64 support
- Some packages may take longer to build on first run

**Windows**:
- Ensure WSL2 is enabled
- Use Docker Desktop with WSL2 backend
- File sharing must be configured for mounted volumes

## Performance Optimization

### Multi-Stage Builds
The Dockerfiles use multi-stage builds to minimize image size:
- Frontend: Build with Node.js, serve with nginx
- Backend: Separate dependency installation stages

### Caching
To speed up builds:
```bash
# Build with cache
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache
```

### Layer Caching
Dependencies are installed before copying application code to maximize Docker layer caching.

## Security Considerations

- 🔒 Images run as non-root where possible
- 🔒 Minimal attack surface (only necessary packages)
- 🔒 Regular base image updates recommended
- 🔒 Secrets should never be baked into images

## Monitoring & Logging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks
The backend includes health check endpoints:
- `/health` - Basic health check
- `/docs` - API documentation (Swagger)

## Backup & Data Persistence

Application data is stored in Docker volumes:
```bash
# List volumes
docker volume ls

# Backup volume
docker run --rm -v openredact-storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/openredact-backup.tar.gz /data

# Restore volume
docker run --rm -v openredact-storage:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/openredact-backup.tar.gz --strip 1"
```

## Contributing

For development setup and contribution guidelines, see the main [README.md](../README.md).

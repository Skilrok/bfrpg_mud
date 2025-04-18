# 🚀 BFRPG MUD Deployment Guide

This document provides instructions for deploying the BFRPG MUD application using Docker and setting up CI/CD with GitHub Actions.

## 📋 Requirements

- Docker and Docker Compose
- Git
- A server with SSH access (for production deployment)
- GitHub account (for CI/CD)

## 🐳 Local Development with Docker

### Starting the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bfrpg_mud.git
   cd bfrpg_mud
   ```

2. Run the development script:
   ```bash
   ./scripts/start-dev.sh
   ```

   This script will:
   - Create a virtual environment if it doesn't exist
   - Install dependencies
   - Run database migrations
   - Start the FastAPI server with hot reloading

3. The API will be available at http://localhost:8000

### Testing Docker Setup

To test the Docker setup locally:

```bash
./scripts/docker-test.sh
```

This script will:
- Build the Docker images
- Start the containers
- Run health checks against the API
- Stop the containers when done

## 🏭 Production Deployment

### Manual Deployment

1. SSH into your server:
   ```bash
   ssh user@your-server
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bfrpg_mud.git
   cd bfrpg_mud
   ```

3. Create a `.env` file with your production settings:
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   nano .env
   ```

4. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. The API will be available at http://your-server:8000

### Environment Variables

Configure these environment variables for production:

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://user:password@host:port/dbname |
| SECRET_KEY | Secret key for JWT tokens | your-secret-key |
| ENVIRONMENT | Current environment | production |

## 🔄 CI/CD Pipeline

The project includes a GitHub Actions workflow for Continuous Integration and Deployment.

### How It Works

1. **Testing**: When you push code to any branch, GitHub Actions will:
   - Set up a Python environment
   - Install dependencies
   - Run the test suite

2. **Building and Pushing**: When you push to the `main` branch, GitHub Actions will:
   - Build a Docker image
   - Push it to GitHub Container Registry (ghcr.io)
   - Tag it with the latest commit hash

3. **Deployment**: After a successful build, GitHub Actions can:
   - Deploy to your production server
   - Run health checks to verify the deployment

### Setting Up CI/CD

1. In your GitHub repository, go to Settings > Secrets and add:
   - `SSH_PRIVATE_KEY`: Your SSH private key for deployment
   - `SSH_HOST`: Your server hostname
   - `SSH_USERNAME`: Your server username

2. Uncomment the deployment steps in `.github/workflows/ci-cd.yml` and adjust them to your server setup.

### Manual Deployment with Docker Registry

To manually deploy the latest image from GitHub Container Registry:

1. Login to GitHub Container Registry:
   ```bash
   docker login ghcr.io -u yourusername
   ```

2. Pull the latest image:
   ```bash
   docker pull ghcr.io/yourusername/bfrpg_mud:latest
   ```

3. Update your docker-compose.yml to use the pulled image and run:
   ```bash
   docker-compose up -d
   ```

## 🔍 Deployment Verification

After deployment, verify that the application is running correctly:

1. Check the health endpoint:
   ```bash
   curl http://your-server:8000/health
   ```

2. Test the authentication endpoint:
   ```bash
   curl -X POST http://your-server:8000/api/auth/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=yourusername&password=yourpassword"
   ```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check that PostgreSQL is running and accessible
   - Verify the DATABASE_URL environment variable

2. **Container Fails to Start**:
   - Check the logs: `docker-compose logs`
   - Verify environment variables are set correctly

3. **Authentication Issues**:
   - Check the SECRET_KEY environment variable
   - Verify that users exist in the database

### Getting Logs

```bash
# View all logs
docker-compose logs

# View logs for a specific service
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f
``` 
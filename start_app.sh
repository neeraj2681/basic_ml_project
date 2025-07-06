#!/bin/bash

# Application Start Script for EC2
# This script clones the repo and starts the ML application

set -e  # Exit on any error

echo "🚀 Starting ML Application deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please ensure Docker is installed and started."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not available. Please install it first."
    exit 1
fi

# Clone repository (update with your actual repo URL)
echo "📁 Cloning repository..."
if [ -d "basic_ml_project" ]; then
    echo "📁 Repository already exists, pulling latest changes..."
    cd basic_ml_project
    git pull origin main
else
    # Replace with your actual GitHub repository URL
    echo "⚠️  Please update the repository URL in start_app.sh"
    echo "    git clone https://github.com/yourusername/basic_ml_project.git"
    echo ""
    echo "For now, creating project directory manually..."
    mkdir -p basic_ml_project
    cd basic_ml_project
    
    echo "📋 You'll need to upload your project files manually or clone from your repo"
    echo "    Required files: docker-compose.yml, Dockerfile, Dockerfile.streamlit, etc."
    echo ""
    echo "Exiting - please set up your repository first."
    exit 1
fi

# Build and start the application
echo "🏗️  Building Docker images..."
docker-compose build

echo "🚀 Starting application services..."
docker-compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Get EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your applications:"
echo "   📊 Streamlit Frontend: http://${EC2_IP}:8501"
echo "   🔌 FastAPI Backend:    http://${EC2_IP}:8000"
echo "   📚 API Documentation:  http://${EC2_IP}:8000/docs"
echo "   💊 Health Check:       http://${EC2_IP}:8000/health"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f           # View logs"
echo "   docker-compose ps                # Check status"
echo "   docker-compose restart           # Restart services"
echo "   docker-compose down              # Stop services"
echo "   docker-compose up -d --build     # Rebuild and restart"
echo ""
echo "�� Happy predicting!" 
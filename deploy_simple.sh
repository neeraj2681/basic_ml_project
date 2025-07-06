#!/bin/bash

# Simple AWS EC2 Deployment Script
# This uses host networking to avoid port binding issues

set -e

IMAGE_NAME=${1:-ml-churn-prediction:latest}
CONTAINER_NAME=${2:-ml-app}

echo "🚀 Deploying ML App on AWS EC2"
echo "Image: $IMAGE_NAME"
echo "Container: $CONTAINER_NAME"

# Stop and remove existing container if it exists
if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping existing container..."
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

# Method 1: Host networking (recommended for AWS EC2)
echo "🌐 Starting container with host networking..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --network host \
    --restart unless-stopped \
    "$IMAGE_NAME"

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")

# Check status
echo "📊 Checking container status..."
docker ps --filter "name=$CONTAINER_NAME"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Access your application:"
echo "   📊 Streamlit Frontend: http://$PUBLIC_IP:8501"
echo "   🔌 FastAPI Backend:    http://$PUBLIC_IP:8000"
echo "   📚 API Documentation:  http://$PUBLIC_IP:8000/docs"
echo "   💊 Health Check:       http://$PUBLIC_IP:8000/health"
echo ""
echo "📋 Useful commands:"
echo "   docker logs $CONTAINER_NAME           # View logs"
echo "   docker restart $CONTAINER_NAME        # Restart app"
echo "   docker stop $CONTAINER_NAME           # Stop app"
echo "   bash troubleshoot_aws.sh              # Run diagnostics"
echo ""
echo "⚠️  If you can't access the app:"
echo "   1. Check Security Group (ports 8000, 8501)"
echo "   2. Run: bash troubleshoot_aws.sh"
echo "   3. Check container logs: docker logs $CONTAINER_NAME" 
#!/bin/bash

# EC2 Deployment Script for ML App
# This script sets up Docker, clones the repo, and starts the services

set -e  # Exit on any error

echo "🚀 Starting ML App deployment on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📁 Installing Git..."
sudo yum install -y git

# Install additional tools
sudo yum install -y htop curl wget

echo "✅ Basic setup complete!"
echo ""
echo "🔄 Please logout and login again for Docker group changes to take effect:"
echo "   exit"
echo "   ssh -i your-key.pem ec2-user@your-ec2-ip"
echo ""
echo "🚀 Then run the application deployment:"
echo "   curl -sSL https://raw.githubusercontent.com/yourusername/yourrepo/main/start_app.sh | bash"
echo ""
echo "Or manually:"
echo "   git clone https://github.com/yourusername/yourrepo.git"
echo "   cd basic_ml_project"
echo "   docker-compose up -d" 
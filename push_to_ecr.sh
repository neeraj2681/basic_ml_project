#!/bin/bash

# Script to build and push the ML app to AWS ECR
# Usage: ./push_to_ecr.sh [region] [repository-name]

set -e

# Default values
AWS_REGION=${1:-us-east-1}
REPO_NAME=${2:-ml-churn-prediction}
IMAGE_TAG=${3:-latest}

echo "🚀 Building and pushing ML app to ECR..."
echo "   Region: $AWS_REGION"
echo "   Repository: $REPO_NAME"
echo "   Tag: $IMAGE_TAG"
echo "   Platform: linux/amd64 (x86_64)"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_URI}/${REPO_NAME}:${IMAGE_TAG}"

echo "   Full image name: $FULL_IMAGE_NAME"

# Check if repository exists, create if not
echo "📋 Checking if ECR repository exists..."
if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION > /dev/null 2>&1; then
    echo "📦 Creating ECR repository: $REPO_NAME"
    aws ecr create-repository \
        --repository-name $REPO_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true
else
    echo "✅ Repository $REPO_NAME already exists"
fi

# Get ECR login token
echo "🔐 Getting ECR login token..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Build the Docker image for x86_64 architecture
echo "🏗️  Building Docker image for linux/amd64 (x86_64)..."
docker build --platform linux/amd64 -f Dockerfile.combined -t $REPO_NAME:$IMAGE_TAG .

# Tag the image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag $REPO_NAME:$IMAGE_TAG $FULL_IMAGE_NAME

# Push the image to ECR
echo "📤 Pushing image to ECR..."
docker push $FULL_IMAGE_NAME

# Get the image URI
IMAGE_URI="${ECR_URI}/${REPO_NAME}:${IMAGE_TAG}"

echo ""
echo "✅ Successfully pushed to ECR!"
echo ""
echo "📊 Image Details:"
echo "   Repository: $REPO_NAME"
echo "   Tag: $IMAGE_TAG"
echo "   URI: $IMAGE_URI"
echo "   Architecture: linux/amd64 (x86_64)"
echo ""
echo "🚀 Next steps for deployment:"
echo ""
echo "   1. ECS Fargate Task Definition:"
echo "      - Container Image: $IMAGE_URI"
echo "      - Port Mappings: 8000 (FastAPI), 8501 (Streamlit)"
echo "      - Memory: 2048 MB minimum"
echo "      - CPU: 1024 (1 vCPU) minimum"
echo "      - Platform: LINUX/X86_64"
echo ""
echo "   2. EC2 Instance (x86_64):"
echo "      docker run -d -p 8000:8000 -p 8501:8501 $IMAGE_URI"
echo ""
echo "   3. ECS Service with Load Balancer:"
echo "      - Target Group 1: Port 8000 (FastAPI)"
echo "      - Target Group 2: Port 8501 (Streamlit)"
echo ""
echo "🎉 Happy deploying!" 
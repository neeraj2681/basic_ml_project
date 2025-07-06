#!/bin/bash

# AWS Deployment Script for Customer Churn Prediction API
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="churn-prediction-api"
ECS_CLUSTER_NAME="churn-api-cluster"
ECS_SERVICE_NAME="churn-api-service"
TASK_DEFINITION_FAMILY="churn-prediction-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting deployment of Customer Churn Prediction API${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"
echo "ECR Repository: ${ECR_URI}"
echo "ECS Cluster: ${ECS_CLUSTER_NAME}"
echo "ECS Service: ${ECS_SERVICE_NAME}"

# Step 1: Create ECR repository if it doesn't exist
echo -e "${YELLOW}🏗️  Creating ECR repository...${NC}"
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}

# Step 2: Get ECR login token
echo -e "${YELLOW}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

# Step 3: Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t ${ECR_REPOSITORY_NAME} .

# Step 4: Tag image for ECR
echo -e "${YELLOW}🏷️  Tagging image...${NC}"
docker tag ${ECR_REPOSITORY_NAME}:latest ${ECR_URI}:latest

# Step 5: Push image to ECR
echo -e "${YELLOW}📤 Pushing image to ECR...${NC}"
docker push ${ECR_URI}:latest

# Step 6: Update task definition with correct ECR URI
echo -e "${YELLOW}📝 Updating task definition...${NC}"
sed "s|YOUR_ECR_REPOSITORY_URI|${ECR_URI}|g" aws/ecs-task-definition.json > aws/ecs-task-definition-updated.json
sed -i "s|YOUR_ACCOUNT_ID|${AWS_ACCOUNT_ID}|g" aws/ecs-task-definition-updated.json

# Step 7: Register task definition
echo -e "${YELLOW}📋 Registering task definition...${NC}"
aws ecs register-task-definition --cli-input-json file://aws/ecs-task-definition-updated.json --region ${AWS_REGION}

# Step 8: Create ECS cluster if it doesn't exist
echo -e "${YELLOW}🏗️  Creating ECS cluster...${NC}"
aws ecs describe-clusters --clusters ${ECS_CLUSTER_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecs create-cluster --cluster-name ${ECS_CLUSTER_NAME} --region ${AWS_REGION}

# Step 9: Create or update ECS service
echo -e "${YELLOW}🚀 Deploying to ECS...${NC}"
if aws ecs describe-services --cluster ${ECS_CLUSTER_NAME} --services ${ECS_SERVICE_NAME} --region ${AWS_REGION} 2>/dev/null | grep -q "ACTIVE"; then
    echo "Updating existing service..."
    aws ecs update-service \
        --cluster ${ECS_CLUSTER_NAME} \
        --service ${ECS_SERVICE_NAME} \
        --task-definition ${TASK_DEFINITION_FAMILY} \
        --region ${AWS_REGION}
else
    echo "Creating new service..."
    aws ecs create-service \
        --cluster ${ECS_CLUSTER_NAME} \
        --service-name ${ECS_SERVICE_NAME} \
        --task-definition ${TASK_DEFINITION_FAMILY} \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx],securityGroups=[sg-xxxxxxxxx],assignPublicIp=ENABLED}" \
        --region ${AWS_REGION}
fi

# Cleanup
rm -f aws/ecs-task-definition-updated.json

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your API will be available once the ECS service is running.${NC}"
echo -e "${YELLOW}💡 To check the status: aws ecs describe-services --cluster ${ECS_CLUSTER_NAME} --services ${ECS_SERVICE_NAME} --region ${AWS_REGION}${NC}" 
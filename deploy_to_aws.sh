#!/bin/bash

# 🚀 Automated AWS Deployment Script for Churn Prediction API
# This script deploys your Docker container to AWS Fargate

set -e  # Exit on any error

echo "🚀 Starting AWS Deployment for Churn Prediction API..."
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="churn-prediction"
CLUSTER_NAME="${APP_NAME}-cluster"
SERVICE_NAME="${APP_NAME}-service"
TASK_NAME="${APP_NAME}-task"
REGION="us-east-1"
PORT=8000

# Check if AWS CLI is configured
echo -e "${BLUE}Checking AWS CLI configuration...${NC}"
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}❌ AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    echo "You need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region (recommend: us-east-1)"
    echo "  - Default output format (recommend: json)"
    exit 1
fi

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ AWS Account ID: ${ACCOUNT_ID}${NC}"

# Step 1: Create ECR Repository
echo -e "${BLUE}Step 1: Creating ECR Repository...${NC}"
REPO_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${APP_NAME}-api"

if aws ecr describe-repositories --repository-names "${APP_NAME}-api" --region $REGION &>/dev/null; then
    echo -e "${YELLOW}⚠️  ECR repository already exists${NC}"
else
    aws ecr create-repository --repository-name "${APP_NAME}-api" --region $REGION
    echo -e "${GREEN}✅ ECR repository created${NC}"
fi

# Step 2: Login to ECR and push Docker image
echo -e "${BLUE}Step 2: Logging into ECR and pushing Docker image...${NC}"
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REPO_URI

# Tag and push the image
docker tag basic-ml-app:latest $REPO_URI:latest
docker push $REPO_URI:latest
echo -e "${GREEN}✅ Docker image pushed to ECR${NC}"

# Step 3: Create ECS Cluster
echo -e "${BLUE}Step 3: Creating ECS Cluster...${NC}"
if aws ecs describe-clusters --clusters $CLUSTER_NAME --region $REGION &>/dev/null; then
    echo -e "${YELLOW}⚠️  ECS cluster already exists${NC}"
else
    aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION
    echo -e "${GREEN}✅ ECS cluster created${NC}"
fi

# Step 4: Create IAM role for ECS tasks
echo -e "${BLUE}Step 4: Setting up IAM roles...${NC}"
EXECUTION_ROLE_NAME="ecsTaskExecutionRole"
TASK_ROLE_NAME="${APP_NAME}TaskRole"

# Check if execution role exists
if ! aws iam get-role --role-name $EXECUTION_ROLE_NAME &>/dev/null; then
    # Create trust policy
    cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    # Create execution role
    aws iam create-role --role-name $EXECUTION_ROLE_NAME --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name $EXECUTION_ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    
    rm trust-policy.json
    echo -e "${GREEN}✅ IAM execution role created${NC}"
else
    echo -e "${YELLOW}⚠️  IAM execution role already exists${NC}"
fi

# Get execution role ARN
EXECUTION_ROLE_ARN=$(aws iam get-role --role-name $EXECUTION_ROLE_NAME --query 'Role.Arn' --output text)

# Step 5: Create Task Definition
echo -e "${BLUE}Step 5: Creating ECS Task Definition...${NC}"
cat > task-definition.json << EOF
{
  "family": "$TASK_NAME",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "$APP_NAME",
      "image": "$REPO_URI:latest",
      "portMappings": [
        {
          "containerPort": $PORT,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_NAME",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": []
    }
  ]
}
EOF

# Create CloudWatch log group
aws logs create-log-group --log-group-name "/ecs/$TASK_NAME" --region $REGION 2>/dev/null || true

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $REGION
rm task-definition.json
echo -e "${GREEN}✅ Task definition created${NC}"

# Step 6: Get default VPC and subnets
echo -e "${BLUE}Step 6: Getting VPC and subnet information...${NC}"
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text --region $REGION)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region $REGION)

echo -e "${GREEN}✅ Using VPC: $VPC_ID${NC}"

# Step 7: Create Security Group
echo -e "${BLUE}Step 7: Creating Security Group...${NC}"
SG_NAME="${APP_NAME}-sg"

# Check if security group exists
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" --query 'SecurityGroups[0].GroupId' --output text --region $REGION 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    # Create security group
    SG_ID=$(aws ec2 create-security-group --group-name $SG_NAME --description "Security group for $APP_NAME" --vpc-id $VPC_ID --query 'GroupId' --output text --region $REGION)
    
    # Add inbound rule for port 8000
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port $PORT --cidr 0.0.0.0/0 --region $REGION
    
    echo -e "${GREEN}✅ Security group created: $SG_ID${NC}"
else
    echo -e "${YELLOW}⚠️  Security group already exists: $SG_ID${NC}"
fi

# Step 8: Create ECS Service
echo -e "${BLUE}Step 8: Creating ECS Service...${NC}"

# Prepare subnet IDs for JSON
SUBNET_ARRAY=$(echo $SUBNET_IDS | tr ' ' '\n' | sed 's/^/"/' | sed 's/$/"/' | tr '\n' ',' | sed 's/,$//')

cat > service-definition.json << EOF
{
  "serviceName": "$SERVICE_NAME",
  "cluster": "$CLUSTER_NAME",
  "taskDefinition": "$TASK_NAME",
  "desiredCount": 1,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": [$SUBNET_ARRAY],
      "securityGroups": ["$SG_ID"],
      "assignPublicIp": "ENABLED"
    }
  }
}
EOF

# Check if service exists
if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION &>/dev/null; then
    echo -e "${YELLOW}⚠️  Service already exists, updating...${NC}"
    aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --task-definition $TASK_NAME --region $REGION
else
    aws ecs create-service --cli-input-json file://service-definition.json --region $REGION
    echo -e "${GREEN}✅ ECS service created${NC}"
fi

rm service-definition.json

# Step 9: Wait for service to be running
echo -e "${BLUE}Step 9: Waiting for service to become stable...${NC}"
echo "This may take a few minutes..."

aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION

# Step 10: Get public IP
echo -e "${BLUE}Step 10: Getting public endpoint...${NC}"
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --query 'taskArns[0]' --output text --region $REGION)
ENI_ID=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' --output text --region $REGION)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --query 'NetworkInterfaces[0].Association.PublicIp' --output text --region $REGION)

echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "========================================"
echo -e "${GREEN}✅ Your API is now running on AWS!${NC}"
echo ""
echo -e "${BLUE}🌐 Public URL: http://${PUBLIC_IP}:${PORT}${NC}"
echo -e "${BLUE}📊 Health Check: http://${PUBLIC_IP}:${PORT}/health${NC}"
echo -e "${BLUE}📖 API Docs: http://${PUBLIC_IP}:${PORT}/docs${NC}"
echo ""
echo -e "${YELLOW}📋 AWS Resources Created:${NC}"
echo "  - ECR Repository: ${APP_NAME}-api"
echo "  - ECS Cluster: $CLUSTER_NAME"
echo "  - ECS Service: $SERVICE_NAME"
echo "  - Task Definition: $TASK_NAME"
echo "  - Security Group: $SG_ID"
echo ""
echo -e "${BLUE}💰 Estimated monthly cost: $15-30 (after free tier)${NC}"
echo -e "${BLUE}🔍 Monitor in AWS Console: ECS → Clusters → $CLUSTER_NAME${NC}"
echo ""
echo -e "${GREEN}Test your API:${NC}"
echo "curl -X POST \"http://${PUBLIC_IP}:${PORT}/predict\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"tenure\": 12, \"monthly_charges\": 50, \"total_charges\": 600, \"contract_type\": \"Month-to-month\", \"payment_method\": \"Electronic check\", \"paperless_billing\": \"Yes\", \"internet_service\": \"DSL\", \"online_security\": \"No\", \"online_backup\": \"No\", \"device_protection\": \"No\", \"tech_support\": \"No\", \"streaming_tv\": \"No\", \"streaming_movies\": \"No\"}'"
echo ""
echo -e "${RED}⚠️  Important: The IP address may change if the service restarts.${NC}"
echo -e "${BLUE}For a permanent URL, consider setting up:${NC}"
echo "  - Application Load Balancer"
echo "  - Route 53 domain name"
echo "  - SSL certificate"

# Cleanup temporary files
rm -f trust-policy.json task-definition.json service-definition.json

echo ""
echo -e "${GREEN}🎉 Deployment script completed successfully!${NC}" 
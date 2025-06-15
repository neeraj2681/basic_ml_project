# Customer Churn Prediction API - AWS Deployment Guide

This guide explains how to deploy the Customer Churn Prediction ML model as a REST API on AWS using FastAPI and Docker.

## 🏗️ Architecture Overview

- **FastAPI**: Web framework for building the REST API
- **Docker**: Containerization for consistent deployment
- **AWS ECS**: Container orchestration service
- **AWS ECR**: Container registry for storing Docker images
- **MLflow**: Model versioning and artifact management

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Docker** installed and running
4. **Python 3.10+** for local development
5. **MLflow** model artifacts (generated from training pipeline)

## 🚀 Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API locally
python app.py

# Test the API
python test_api.py
```

The API will be available at `http://localhost:8000`

### 2. Docker Development

```bash
# Build the Docker image
docker build -t churn-prediction-api .

# Run with Docker
docker run -p 8000:8000 churn-prediction-api

# Or use Docker Compose
docker-compose up --build
```

### 3. AWS Deployment

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy to AWS (requires AWS CLI configuration)
./deploy.sh
```

## 📚 API Endpoints

### Health Check
```http
GET /health
```
Returns the health status of the API and model loading status.

### Single Prediction
```http
POST /predict
Content-Type: application/json

{
  "tenure": 12.0,
  "monthly_charges": 65.5,
  "total_charges": 786.0,
  "contract_type": "Month-to-month",
  "payment_method": "Electronic check",
  "paperless_billing": "Yes",
  "internet_service": "Fiber optic",
  "online_security": "No",
  "online_backup": "No",
  "device_protection": "No",
  "tech_support": "No",
  "streaming_tv": "Yes",
  "streaming_movies": "Yes"
}
```

### Batch Prediction
```http
POST /predict_batch
Content-Type: application/json

[
  {
    "tenure": 12.0,
    "monthly_charges": 65.5,
    // ... other fields
  },
  {
    "tenure": 36.0,
    "monthly_charges": 45.2,
    // ... other fields
  }
]
```

### Model Information
```http
GET /model_info
```

## 🔧 Configuration

### Environment Variables

- `MLFLOW_TRACKING_URI`: MLflow tracking server URI
- `AWS_REGION`: AWS region for deployment
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

### AWS Configuration

Before deployment, update the following in `deploy.sh`:

```bash
AWS_REGION="us-east-1"  # Your preferred region
ECR_REPOSITORY_NAME="churn-prediction-api"
ECS_CLUSTER_NAME="churn-api-cluster"
ECS_SERVICE_NAME="churn-api-service"
```

And in `aws/ecs-task-definition.json`:

- Replace `YOUR_ACCOUNT_ID` with your AWS account ID
- Update subnet and security group IDs
- Adjust CPU/memory requirements as needed

## 🛠️ AWS Setup Steps

### 1. IAM Roles

Create the following IAM roles:

**ECS Task Execution Role** (`ecsTaskExecutionRole`):
```json
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
```

Attach policies:
- `AmazonECSTaskExecutionRolePolicy`
- `CloudWatchLogsFullAccess`

**ECS Task Role** (`ecsTaskRole`):
```json
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
```

### 2. VPC and Security Groups

Create a security group that allows:
- Inbound HTTP traffic on port 8000
- Outbound internet access for downloading dependencies

### 3. CloudWatch Logs

Create a log group: `/ecs/churn-prediction-api`

## 🧪 Testing

### Local Testing
```bash
# Start the API
python app.py

# Run tests
python test_api.py
```

### Production Testing
```bash
# Update BASE_URL in test_api.py to your deployed URL
# Then run the tests
python test_api.py
```

## 📊 Monitoring

### CloudWatch Metrics
- Container CPU/Memory utilization
- Request count and latency
- Error rates

### Health Checks
The API includes built-in health checks:
- Container health check via Docker
- ECS health check via task definition
- Application health check via `/health` endpoint

## 🔒 Security Best Practices

1. **Non-root user**: Container runs as non-root user
2. **Minimal base image**: Uses Python slim image
3. **Environment variables**: Sensitive data via environment variables
4. **IAM roles**: Least privilege access
5. **VPC**: Deploy in private subnets with NAT gateway
6. **HTTPS**: Use Application Load Balancer with SSL certificate

## 🚨 Troubleshooting

### Common Issues

1. **Model loading fails**:
   - Check MLflow artifacts are accessible
   - Verify model and preprocessor paths
   - Check CloudWatch logs

2. **Container fails to start**:
   - Verify Docker image builds locally
   - Check ECS task definition
   - Review CloudWatch logs

3. **API returns 503**:
   - Model or preprocessor not loaded
   - Check health endpoint for details

### Debugging Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster churn-api-cluster --services churn-api-service

# View CloudWatch logs
aws logs tail /ecs/churn-prediction-api --follow

# Check task definition
aws ecs describe-task-definition --task-definition churn-prediction-api
```

## 📈 Scaling

### Auto Scaling
Configure ECS service auto scaling based on:
- CPU utilization
- Memory utilization
- Request count

### Load Balancing
Use Application Load Balancer for:
- High availability
- SSL termination
- Health checks
- Multiple availability zones

## 💰 Cost Optimization

1. **Right-sizing**: Start with minimal resources and scale up
2. **Spot instances**: Use Fargate Spot for cost savings
3. **Auto scaling**: Scale down during low usage periods
4. **Reserved capacity**: For predictable workloads

## 🔄 CI/CD Pipeline

Consider setting up automated deployment with:
- GitHub Actions / GitLab CI
- AWS CodePipeline
- Automated testing
- Blue-green deployments

## 📞 Support

For issues and questions:
1. Check CloudWatch logs
2. Review this documentation
3. Test locally first
4. Check AWS service status

---

## 📝 Example Usage

```python
import requests

# Single prediction
response = requests.post(
    "https://your-api-url/predict",
    json={
        "tenure": 12.0,
        "monthly_charges": 65.5,
        "total_charges": 786.0,
        "contract_type": "Month-to-month",
        "payment_method": "Electronic check",
        "paperless_billing": "Yes",
        "internet_service": "Fiber optic",
        "online_security": "No",
        "online_backup": "No",
        "device_protection": "No",
        "tech_support": "No",
        "streaming_tv": "Yes",
        "streaming_movies": "Yes"
    }
)

result = response.json()
print(f"Churn Probability: {result['churn_probability']}")
print(f"Prediction: {result['churn_prediction']}")
```

Happy deploying! 🚀 
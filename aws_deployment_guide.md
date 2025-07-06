# 🚀 AWS Deployment Guide for ML Model

This guide will help you deploy your Customer Churn Prediction model to AWS using Docker and AWS Fargate.

## 📋 Prerequisites

### Step 1: AWS Account Setup
1. **Create AWS Account**: Go to [aws.amazon.com](https://aws.amazon.com)
2. **Get Access Keys**:
   - AWS Console → IAM → Users → Your user → Security credentials
   - Create Access Key & Secret Access Key
   - **Save these securely!**

### Step 2: Configure AWS CLI
```bash
aws configure
```
Enter when prompted:
- AWS Access Key ID: `[your-access-key]`
- AWS Secret Access Key: `[your-secret-key]`
- Default region: `us-east-1` (recommended)
- Default output format: `json`

## 🐳 Docker Image Deployment

### Step 3: Create Amazon ECR Repository
```bash
# Create ECR repository
aws ecr create-repository --repository-name churn-prediction-api

# Get login token and authenticate Docker
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com
```

### Step 4: Tag and Push Docker Image
```bash
# Tag your local image
docker tag basic-ml-app:latest [ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/churn-prediction-api:latest

# Push to ECR
docker push [ACCOUNT-ID].dkr.ecr.us-east-1.amazonaws.com/churn-prediction-api:latest
```

## ⚡ AWS Fargate Deployment

### Step 5: Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name churn-prediction-cluster
```

### Step 6: Create Task Definition
This defines how your container should run (CPU, memory, networking).

### Step 7: Create ECS Service
This ensures your application stays running and handles load balancing.

### Step 8: Configure Security Groups
- Allow HTTP traffic on port 8000
- Configure proper networking

## 🌐 Access Your Application

Once deployed, you'll get:
- **Public URL**: Your API will be accessible via AWS-provided URL
- **Load Balancer**: Automatic scaling and high availability
- **HTTPS**: Can be configured with AWS Certificate Manager

## 💰 Estimated Costs

**AWS Free Tier includes:**
- 750 hours of t2.micro instances (first year)
- 1GB of container registry storage

**Expected monthly cost after free tier:**
- **Fargate**: ~$15-30/month for small workload
- **ECR storage**: ~$0.10/GB/month
- **Data transfer**: First 1GB free, then $0.09/GB

## 🔒 Security Best Practices

1. **Use IAM roles** instead of access keys where possible
2. **Enable CloudTrail** for audit logging
3. **Configure VPC** for network isolation
4. **Use secrets manager** for sensitive data
5. **Enable WAF** for web application firewall

## 🚨 Important Notes

- **Region Selection**: Choose region closest to your users
- **Monitoring**: Use CloudWatch for logs and metrics
- **Backup Strategy**: Consider regular ECR image backups
- **Cost Control**: Set up billing alerts to avoid surprises

## 🎯 Next Steps After Deployment

1. **Custom Domain**: Use Route 53 for custom domain
2. **SSL Certificate**: Use AWS Certificate Manager
3. **CI/CD Pipeline**: Set up CodePipeline for automatic deployments
4. **Monitoring**: Configure CloudWatch dashboards
5. **Scaling**: Configure auto-scaling based on usage

---

**Ready to deploy? Follow the automated script below!** 
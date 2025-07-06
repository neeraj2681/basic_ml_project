# Deploying ML App on EC2 Instance

## Overview
This guide covers deploying your Streamlit + FastAPI application on a single EC2 instance using Docker Compose.

## Architecture
```
Internet → EC2 Instance → Docker Compose
                      ├── FastAPI (port 8000)
                      └── Streamlit (port 8501)
```

## Step 1: Launch EC2 Instance

### Instance Requirements
- **Instance Type**: t3.medium or larger (2 vCPU, 4GB RAM minimum)
- **AMI**: Amazon Linux 2023 or Ubuntu 22.04
- **Storage**: 20GB+ EBS volume
- **Security Group**: Configure ports as shown below

### Security Group Configuration
```bash
# Allow SSH access
Port 22    | Source: Your IP | Protocol: TCP

# Allow FastAPI access
Port 8000  | Source: 0.0.0.0/0 | Protocol: TCP

# Allow Streamlit access  
Port 8501  | Source: 0.0.0.0/0 | Protocol: TCP

# Optional: HTTPS
Port 443   | Source: 0.0.0.0/0 | Protocol: TCP
```

## Step 2: Setup EC2 Instance

### Connect to EC2
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

### Install Docker & Docker Compose
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
```

### Install Git
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
sudo yum install -y git
```

## Step 3: Deploy Application

### Clone Your Repository
```bash
git clone <your-repo-url>
cd basic_ml_project
```

### Build and Run
```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Step 4: Access Your Applications

### Access URLs
- **FastAPI Backend**: `http://your-ec2-public-ip:8000`
- **Streamlit Frontend**: `http://your-ec2-public-ip:8501`
- **API Health Check**: `http://your-ec2-public-ip:8000/health`
- **API Documentation**: `http://your-ec2-public-ip:8000/docs`

### Test the Setup
```bash
# Test FastAPI health
curl http://your-ec2-public-ip:8000/health

# Test Streamlit
curl http://your-ec2-public-ip:8501
```

## Step 5: Production Optimizations

### 1. Use a Domain Name
```bash
# Example with your domain
# FastAPI: api.yourdomain.com
# Streamlit: app.yourdomain.com
```

### 2. Add SSL/HTTPS with Nginx
Create `nginx.conf`:
```nginx
server {
    listen 80;
    server_name app.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Add Nginx to Docker Compose
```yaml
# Add this to your docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - fastapi
      - streamlit
    networks:
      - ml-network
```

### 4. Enable Auto-restart
```bash
# Make services restart automatically
docker-compose up -d --restart unless-stopped
```

## Step 6: Monitoring & Maintenance

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f streamlit
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### System Monitoring
```bash
# Check system resources
htop
df -h
docker stats
```

## Cost Estimation (Monthly)

| Component | Cost |
|-----------|------|
| t3.medium EC2 | ~$30/month |
| 20GB EBS Volume | ~$2/month |
| Data Transfer | ~$1-5/month |
| **Total** | **~$33-37/month** |

## Advantages
✅ Simple deployment
✅ Full control over environment
✅ Cost-effective for low traffic
✅ Easy debugging and monitoring

## Disadvantages
❌ Manual scaling required
❌ Single point of failure
❌ Need to manage EC2 instance
❌ No automatic load balancing

## Alternative: ECS Fargate
For production workloads, consider using our existing ECS Fargate deployment script (`deploy_to_aws.sh`) which provides:
- Automatic scaling
- No server management
- High availability
- Load balancing
- Better for production environments 
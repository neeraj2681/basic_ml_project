#!/bin/bash

# AWS EC2 Troubleshooting Script for ML App
echo "🔍 AWS EC2 ML App Troubleshooting Script"
echo "========================================"

# Get instance information
echo ""
echo "📊 EC2 Instance Information:"
echo "Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'Not available')"
echo "Private IP: $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || echo 'Not available')"
echo "Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo 'Not available')"

# Check Docker status
echo ""
echo "🐳 Docker Status:"
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker is installed"
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker is running"
        
        # List containers
        echo ""
        echo "📦 Running Containers:"
        docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
        
        # Check if ML app container is running
        ML_CONTAINER=$(docker ps --filter "expose=8000" --filter "expose=8501" --format "{{.Names}}" | head -1)
        if [ -n "$ML_CONTAINER" ]; then
            echo ""
            echo "🎯 Found ML App Container: $ML_CONTAINER"
            
            # Check container logs
            echo ""
            echo "📋 Container Logs (last 20 lines):"
            docker logs --tail 20 "$ML_CONTAINER"
            
            # Check port bindings
            echo ""
            echo "🔌 Port Bindings:"
            docker port "$ML_CONTAINER"
            
            # Test internal connectivity
            echo ""
            echo "🔍 Internal Connectivity Test:"
            if docker exec "$ML_CONTAINER" curl -s http://localhost:8000/health >/dev/null 2>&1; then
                echo "✅ FastAPI responds internally"
            else
                echo "❌ FastAPI not responding internally"
            fi
            
            if docker exec "$ML_CONTAINER" curl -s -I http://localhost:8501 >/dev/null 2>&1; then
                echo "✅ Streamlit responds internally"
            else
                echo "❌ Streamlit not responding internally"
            fi
        else
            echo "❌ No ML app container found"
        fi
    else
        echo "❌ Docker is not running"
    fi
else
    echo "❌ Docker is not installed"
fi

# Check system ports
echo ""
echo "🌐 System Port Status:"
echo "Listening ports (8000, 8501):"
if command -v netstat >/dev/null 2>&1; then
    netstat -tlnp | grep -E ":(8000|8501) " || echo "No services listening on ports 8000 or 8501"
elif command -v ss >/dev/null 2>&1; then
    ss -tlnp | grep -E ":(8000|8501) " || echo "No services listening on ports 8000 or 8501"
else
    echo "netstat/ss not available"
fi

# Check firewall status
echo ""
echo "🔥 Firewall Status:"
if command -v ufw >/dev/null 2>&1; then
    echo "UFW Status:"
    sudo ufw status
elif command -v iptables >/dev/null 2>&1; then
    echo "IPTables rules (first 10):"
    sudo iptables -L | head -10
else
    echo "No firewall tools found"
fi

# Test external connectivity
echo ""
echo "🌍 External Connectivity Test:"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
if [ -n "$PUBLIC_IP" ]; then
    echo "Testing from localhost to public IP..."
    
    # Test FastAPI
    if curl -s --connect-timeout 5 "http://$PUBLIC_IP:8000/health" >/dev/null 2>&1; then
        echo "✅ FastAPI accessible externally"
    else
        echo "❌ FastAPI not accessible externally"
    fi
    
    # Test Streamlit
    if curl -s --connect-timeout 5 -I "http://$PUBLIC_IP:8501" >/dev/null 2>&1; then
        echo "✅ Streamlit accessible externally"
    else
        echo "❌ Streamlit not accessible externally"
    fi
else
    echo "Could not determine public IP"
fi

echo ""
echo "📋 Quick Fixes to Try:"
echo "1. Check Security Group: Allow inbound 8000, 8501 from 0.0.0.0/0"
echo "2. Disable UFW firewall: sudo ufw disable"
echo "3. Restart container: docker restart <container-name>"
echo "4. Check container logs: docker logs <container-name>"
echo "5. Run with host network: docker run --network host ..."
echo ""
echo "🔗 Access URLs (replace with your public IP):"
echo "   FastAPI: http://$PUBLIC_IP:8000"
echo "   Streamlit: http://$PUBLIC_IP:8501"
echo "   API Docs: http://$PUBLIC_IP:8000/docs" 
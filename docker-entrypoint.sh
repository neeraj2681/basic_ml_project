#!/bin/bash
set -e

echo "🚀 Starting ML Application Container..."
echo "📅 $(date)"
echo "🏗️  Container Architecture: $(uname -m)"
echo "🌐 Container IP: $(hostname -I)"

# Function to check if a port is available
check_port() {
    local port=$1
    local service=$2
    echo "🔍 Checking if port $port is available for $service..."
    
    if netstat -tlnp 2>/dev/null | grep ":$port " >/dev/null; then
        echo "⚠️  Port $port is already in use:"
        netstat -tlnp 2>/dev/null | grep ":$port " || true
    else
        echo "✅ Port $port is available for $service"
    fi
}

# Check ports
check_port 8000 "FastAPI"
check_port 8501 "Streamlit"

# Show network interfaces
echo "🌐 Network interfaces:"
ip addr show 2>/dev/null | grep -E "(inet |UP,)" | head -10 || echo "Could not show network interfaces"

# Show environment variables
echo "🔧 Environment:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   API_BASE_URL: $API_BASE_URL"
echo "   STREAMLIT_SERVER_ADDRESS: $STREAMLIT_SERVER_ADDRESS"

# Ensure log directory exists and has correct permissions
mkdir -p /var/log/supervisor
chown -R app:app /var/log/supervisor /app

echo "🎯 Starting services with supervisor..."

# Wait a moment for any system processes to settle
sleep 2

# Start supervisor as root (it will switch to app user for individual processes)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 
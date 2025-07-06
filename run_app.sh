#!/bin/bash

# Run Customer Churn Prediction App
# This script starts both the FastAPI backend and Streamlit frontend

echo "🚀 Starting Customer Churn Prediction Application..."
echo "======================================================"

# Check if Docker is running
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker is not installed or not running. Please install Docker first."
    exit 1
fi

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null
    fi
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Option 1: Run with Docker (recommended for production)
run_with_docker() {
    echo "🐳 Starting with Docker..."
    
    # Build the Docker image if it doesn't exist
    if [[ "$(docker images -q basic-ml-app 2> /dev/null)" == "" ]]; then
        echo "📦 Building Docker image..."
        docker build -t basic-ml-app .
    fi
    
    # Stop and remove existing container if running
    docker stop basic-ml-app-container 2>/dev/null || true
    docker rm basic-ml-app-container 2>/dev/null || true
    
    # Run FastAPI in Docker
    echo "⚡ Starting FastAPI backend in Docker..."
    docker run -d --name basic-ml-app-container -p 8000:8000 basic-ml-app
    
    # Wait for FastAPI to start
    sleep 5
    
    # Check if FastAPI is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ FastAPI backend is running on http://localhost:8000"
    else
        echo "❌ Failed to start FastAPI backend"
        exit 1
    fi
    
    # Run Streamlit locally
    echo "🎨 Starting Streamlit frontend..."
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
    STREAMLIT_PID=$!
    
    echo ""
    echo "🎉 Application is ready!"
    echo "📊 Streamlit Frontend: http://localhost:8501"
    echo "🔧 FastAPI Backend: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Keep script running
    wait $STREAMLIT_PID
}

# Option 2: Run locally (for development)
run_locally() {
    echo "💻 Starting locally..."
    
    # Start FastAPI in background
    echo "⚡ Starting FastAPI backend..."
    python app.py &
    FASTAPI_PID=$!
    
    # Wait for FastAPI to start
    sleep 3
    
    # Check if FastAPI is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ FastAPI backend is running on http://localhost:8000"
    else
        echo "❌ Failed to start FastAPI backend"
        kill $FASTAPI_PID 2>/dev/null
        exit 1
    fi
    
    # Start Streamlit in background
    echo "🎨 Starting Streamlit frontend..."
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
    STREAMLIT_PID=$!
    
    echo ""
    echo "🎉 Application is ready!"
    echo "📊 Streamlit Frontend: http://localhost:8501"
    echo "🔧 FastAPI Backend: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Keep script running
    wait $STREAMLIT_PID
}

# Check command line arguments
if [ "$1" = "--local" ]; then
    run_locally
else
    run_with_docker
fi 
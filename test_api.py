#!/usr/bin/env python3
"""
Test script for Customer Churn Prediction API
"""

import requests
import json
import time

# API base URL (change this to your deployed URL)
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_model_info():
    """Test the model info endpoint"""
    print("\n📊 Testing model info...")
    try:
        response = requests.get(f"{BASE_URL}/model_info")
        if response.status_code == 200:
            print("✅ Model info retrieved")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")

def test_single_prediction():
    """Test single customer prediction"""
    print("\n🔮 Testing single prediction...")
    
    # Sample customer data
    customer_data = {
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
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=customer_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single prediction successful")
            print(f"Churn Probability: {result['churn_probability']:.4f}")
            print(f"Churn Prediction: {result['churn_prediction']}")
            print(f"Confidence: {result['confidence']}")
        else:
            print(f"❌ Single prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Single prediction error: {e}")

def test_batch_prediction():
    """Test batch prediction"""
    print("\n📦 Testing batch prediction...")
    
    # Sample batch data
    batch_data = [
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
        },
        {
            "tenure": 36.0,
            "monthly_charges": 45.2,
            "total_charges": 1627.2,
            "contract_type": "Two year",
            "payment_method": "Bank transfer (automatic)",
            "paperless_billing": "No",
            "internet_service": "DSL",
            "online_security": "Yes",
            "online_backup": "Yes",
            "device_protection": "Yes",
            "tech_support": "Yes",
            "streaming_tv": "No",
            "streaming_movies": "No"
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict_batch",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Batch prediction successful")
            for i, prediction in enumerate(result['predictions']):
                print(f"Customer {i+1}:")
                print(f"  Churn Probability: {prediction['churn_probability']:.4f}")
                print(f"  Churn Prediction: {prediction['churn_prediction']}")
                print(f"  Confidence: {prediction['confidence']}")
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Batch prediction error: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting API Tests for Customer Churn Prediction")
    print("=" * 50)
    
    # Wait a moment for the API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Run tests
    test_health_check()
    test_root_endpoint()
    test_model_info()
    test_single_prediction()
    test_batch_prediction()
    
    print("\n" + "=" * 50)
    print("🏁 API testing completed!")

if __name__ == "__main__":
    main() 
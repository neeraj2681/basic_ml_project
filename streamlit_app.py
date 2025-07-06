import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration - use environment variable for Docker deployment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def check_api_health():
    """Check if the FastAPI backend is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def get_prediction(customer_data: Dict[str, Any]):
    """Get prediction from the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict", 
            json=customer_data,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_batch_predictions(customers_data: list):
    """Get batch predictions from the FastAPI backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict_batch", 
            json=customers_data,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def create_gauge_chart(probability: float, title: str = "Churn Probability"):
    """Create a gauge chart for churn probability"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def main():
    st.title("🔮 Customer Churn Prediction Dashboard")
    st.markdown("---")
    
    # Sidebar - API Status
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Check API health
        health_status = check_api_health()
        if health_status:
            if health_status.get("status") == "healthy":
                st.success("✅ API is healthy")
                if health_status.get("model_loaded"):
                    st.success("✅ Model loaded")
                else:
                    st.warning("⚠️ Model not loaded")
            else:
                st.error("❌ API is degraded")
        else:
            st.error("❌ Cannot connect to API")
            st.error(f"Trying to connect to: {API_BASE_URL}")
            
        st.markdown("---")
        st.markdown("### 📊 Model Info")
        st.info("🎯 **Purpose**: Predict customer churn likelihood")
        st.info("🧠 **Algorithm**: Logistic Regression")
        st.info("📈 **Accuracy**: ~73%")
        
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Single Prediction", "📊 Batch Prediction", "📈 Analytics"])
    
    with tab1:
        st.header("Individual Customer Churn Prediction")
        
        # Create two columns for input
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Customer Information")
            
            tenure = st.number_input(
                "Tenure (months)", 
                min_value=0, 
                max_value=100, 
                value=12,
                help="How long has the customer been with the company?"
            )
            
            monthly_charges = st.number_input(
                "Monthly Charges ($)", 
                min_value=0.0, 
                max_value=200.0, 
                value=50.0,
                step=0.01,
                help="Monthly fee charged to the customer"
            )
            
            total_charges = st.number_input(
                "Total Charges ($)", 
                min_value=0.0, 
                max_value=10000.0, 
                value=600.0,
                step=0.01,
                help="Total amount charged to the customer"
            )
            
            contract_type = st.selectbox(
                "Contract Type",
                ["Month-to-month", "One year", "Two year"],
                help="Type of contract the customer has"
            )
            
            payment_method = st.selectbox(
                "Payment Method",
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
                help="How the customer pays their bill"
            )
            
            paperless_billing = st.selectbox(
                "Paperless Billing",
                ["Yes", "No"],
                help="Whether the customer has paperless billing"
            )
            
        with col2:
            st.subheader("📡 Service Information")
            
            internet_service = st.selectbox(
                "Internet Service",
                ["DSL", "Fiber optic", "No"],
                help="Type of internet service"
            )
            
            online_security = st.selectbox(
                "Online Security",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has online security add-on"
            )
            
            online_backup = st.selectbox(
                "Online Backup",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has online backup add-on"
            )
            
            device_protection = st.selectbox(
                "Device Protection",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has device protection add-on"
            )
            
            tech_support = st.selectbox(
                "Tech Support",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has tech support add-on"
            )
            
            streaming_tv = st.selectbox(
                "Streaming TV",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has streaming TV add-on"
            )
            
            streaming_movies = st.selectbox(
                "Streaming Movies",
                ["Yes", "No", "No internet service"],
                help="Whether the customer has streaming movies add-on"
            )
        
        # Prediction button
        if st.button("🔮 Predict Churn", type="primary"):
            # Prepare customer data
            customer_data = {
                "tenure": tenure,
                "monthly_charges": monthly_charges,
                "total_charges": total_charges,
                "contract_type": contract_type,
                "payment_method": payment_method,
                "paperless_billing": paperless_billing,
                "internet_service": internet_service,
                "online_security": online_security,
                "online_backup": online_backup,
                "device_protection": device_protection,
                "tech_support": tech_support,
                "streaming_tv": streaming_tv,
                "streaming_movies": streaming_movies
            }
            
            # Get prediction
            with st.spinner("🔄 Making prediction..."):
                prediction = get_prediction(customer_data)
                
            if prediction:
                # Display results
                st.markdown("---")
                st.header("📊 Prediction Results")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Gauge chart
                    fig = create_gauge_chart(prediction["churn_probability"])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.metric(
                        "Churn Prediction",
                        prediction["churn_prediction"],
                        delta=f"{prediction['churn_probability']:.1%} probability"
                    )
                
                with col3:
                    confidence_color = {
                        "High": "🟢",
                        "Medium": "🟡", 
                        "Low": "🔴"
                    }
                    st.metric(
                        "Confidence",
                        f"{confidence_color.get(prediction['confidence'], '🔵')} {prediction['confidence']}",
                    )
                
                # Risk assessment
                risk_level = "🔴 High Risk" if prediction["churn_probability"] > 0.7 else \
                           "🟡 Medium Risk" if prediction["churn_probability"] > 0.3 else \
                           "🟢 Low Risk"
                           
                st.markdown(f"### Risk Assessment: {risk_level}")
                
                # Recommendations
                if prediction["churn_probability"] > 0.5:
                    st.warning("⚠️ **High Churn Risk Detected!**")
                    st.markdown("**Recommended Actions:**")
                    st.markdown("- 📞 Proactive customer outreach")
                    st.markdown("- 💰 Consider retention offers")
                    st.markdown("- 🎯 Personalized service improvements")
                    st.markdown("- 📋 Collect feedback on pain points")
                else:
                    st.success("✅ **Low Churn Risk**")
                    st.markdown("**Recommended Actions:**")
                    st.markdown("- 😊 Continue excellent service")
                    st.markdown("- 🔄 Regular satisfaction surveys")
                    st.markdown("- 📈 Upselling opportunities")
    
    with tab2:
        st.header("Batch Customer Prediction")
        st.markdown("Upload a CSV file with customer data for bulk prediction")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="CSV should contain columns matching the input fields"
        )
        
        if uploaded_file is not None:
            try:
                # Read the CSV
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(df)} customers")
                
                # Show preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head())
                
                # Predict button
                if st.button("🔮 Predict All", type="primary"):
                    with st.spinner("🔄 Processing batch predictions..."):
                        # Convert dataframe to list of dictionaries
                        customers_list = df.to_dict('records')
                        
                        # Get batch predictions
                        batch_results = get_batch_predictions(customers_list)
                        
                    if batch_results:
                        predictions_df = pd.DataFrame(batch_results["predictions"])
                        
                        # Merge with original data
                        results_df = pd.concat([df, predictions_df], axis=1)
                        
                        st.subheader("📊 Prediction Results")
                        st.dataframe(results_df)
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            avg_churn_prob = predictions_df["churn_probability"].mean()
                            st.metric("Average Churn Probability", f"{avg_churn_prob:.1%}")
                        
                        with col2:
                            high_risk_count = (predictions_df["churn_probability"] > 0.7).sum()
                            st.metric("High Risk Customers", high_risk_count)
                        
                        with col3:
                            churn_yes_count = (predictions_df["churn_prediction"] == "Yes").sum()
                            st.metric("Predicted Churners", churn_yes_count)
                        
                        # Download button
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results CSV",
                            data=csv,
                            file_name="churn_predictions.csv",
                            mime="text/csv"
                        )
                        
                        # Visualization
                        st.subheader("📈 Risk Distribution")
                        fig = px.histogram(
                            predictions_df, 
                            x="churn_probability", 
                            nbins=20,
                            title="Distribution of Churn Probabilities"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        # Sample CSV download
        st.markdown("---")
        st.subheader("📥 Need a sample file?")
        
        sample_data = {
            "tenure": [12, 34, 2, 45],
            "monthly_charges": [50.0, 75.0, 85.0, 45.0],
            "total_charges": [600.0, 2550.0, 170.0, 2025.0],
            "contract_type": ["Month-to-month", "Two year", "Month-to-month", "One year"],
            "payment_method": ["Electronic check", "Credit card (automatic)", "Electronic check", "Bank transfer (automatic)"],
            "paperless_billing": ["Yes", "No", "Yes", "No"],
            "internet_service": ["DSL", "Fiber optic", "Fiber optic", "DSL"],
            "online_security": ["No", "Yes", "No", "Yes"],
            "online_backup": ["No", "Yes", "No", "Yes"],
            "device_protection": ["No", "Yes", "No", "Yes"],
            "tech_support": ["No", "Yes", "No", "Yes"],
            "streaming_tv": ["No", "Yes", "No", "Yes"],
            "streaming_movies": ["No", "Yes", "No", "Yes"]
        }
        
        sample_df = pd.DataFrame(sample_data)
        sample_csv = sample_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download Sample CSV",
            data=sample_csv,
            file_name="sample_customers.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.header("Model Analytics & Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Model Performance")
            
            # Mock performance data (in real scenario, this would come from your model training)
            performance_data = {
                "Metric": ["Accuracy", "Precision", "Recall", "F1-Score"],
                "Value": [0.73, 0.71, 0.73, 0.71]
            }
            
            perf_df = pd.DataFrame(performance_data)
            
            fig = px.bar(
                perf_df, 
                x="Metric", 
                y="Value",
                title="Model Performance Metrics",
                color="Value",
                color_continuous_scale="viridis"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Feature Importance")
            
            # Mock feature importance (in real scenario, this would come from your model)
            feature_data = {
                "Feature": ["Monthly Charges", "Total Charges", "Tenure", "Contract Type", "Payment Method", "Internet Service"],
                "Importance": [0.25, 0.20, 0.18, 0.15, 0.12, 0.10]
            }
            
            feat_df = pd.DataFrame(feature_data)
            
            fig = px.bar(
                feat_df, 
                x="Importance", 
                y="Feature",
                orientation="h",
                title="Top Feature Importance",
                color="Importance",
                color_continuous_scale="plasma"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("💡 Business Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.info("""
            **🔍 Key Risk Factors:**
            - High monthly charges
            - Month-to-month contracts
            - Electronic check payments
            - Short tenure (< 12 months)
            """)
        
        with insights_col2:
            st.success("""
            **✅ Retention Strategies:**
            - Offer long-term contract discounts
            - Promote automatic payment methods
            - Provide loyalty rewards for long tenure
            - Bundle services for better value
            """)

if __name__ == "__main__":
    main() 
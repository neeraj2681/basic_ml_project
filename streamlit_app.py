import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

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
        response = requests.post(f"{API_BASE_URL}/predict", json=customer_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def create_gauge_chart(probability: float):
    """Create a gauge chart for churn probability"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Churn Probability (%)"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def main():
    st.title("🎯 Customer Churn Prediction Dashboard")
    st.markdown("---")
    
    # Check API health
    health_status = check_api_health()
    
    # Sidebar for API status
    with st.sidebar:
        st.header("🔌 API Status")
        if health_status:
            if health_status.get('status') == 'healthy':
                st.success("✅ API is healthy")
                st.success("✅ Model loaded")
            else:
                st.warning("⚠️ API is degraded")
                st.error("❌ Model not loaded")
        else:
            st.error("❌ API is not responding")
            st.error("Make sure your FastAPI server is running on http://localhost:8000")
            st.stop()
        
        st.markdown("---")
        st.header("📋 Instructions")
        st.markdown("""
        1. Fill in the customer information in the form
        2. Click 'Predict Churn' to get the prediction
        3. View the results and probability gauge
        4. Use the batch prediction for multiple customers
        """)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Single Prediction", "📊 Batch Prediction", "📈 Analytics"])
    
    with tab1:
        st.header("Customer Information")
        
        # Create input form
        with st.form("customer_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📋 Basic Info")
                tenure = st.number_input(
                    "Tenure (months)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=12.0,
                    help="Number of months the customer has been with the company"
                )
                monthly_charges = st.number_input(
                    "Monthly Charges ($)", 
                    min_value=0.0, 
                    max_value=200.0, 
                    value=65.0,
                    help="Monthly charges in dollars"
                )
                total_charges = st.number_input(
                    "Total Charges ($)", 
                    min_value=0.0, 
                    max_value=10000.0, 
                    value=1000.0,
                    help="Total charges accumulated"
                )
                
            with col2:
                st.subheader("📞 Service Details")
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
                    help="Whether the customer uses paperless billing"
                )
                internet_service = st.selectbox(
                    "Internet Service", 
                    ["DSL", "Fiber optic", "No"],
                    help="Type of internet service"
                )
                
            with col3:
                st.subheader("🌐 Add-on Services")
                online_security = st.selectbox(
                    "Online Security", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has online security service"
                )
                online_backup = st.selectbox(
                    "Online Backup", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has online backup service"
                )
                device_protection = st.selectbox(
                    "Device Protection", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has device protection"
                )
                tech_support = st.selectbox(
                    "Tech Support", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has tech support"
                )
                streaming_tv = st.selectbox(
                    "Streaming TV", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has streaming TV service"
                )
                streaming_movies = st.selectbox(
                    "Streaming Movies", 
                    ["Yes", "No", "No internet service"],
                    help="Whether customer has streaming movies service"
                )
            
            # Submit button
            submitted = st.form_submit_button("🔮 Predict Churn", use_container_width=True)
            
        if submitted:
            # Prepare data for API
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
            with st.spinner("🔄 Getting prediction..."):
                prediction = get_prediction(customer_data)
            
            if prediction:
                st.success("✅ Prediction completed!")
                
                # Display results
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.plotly_chart(create_gauge_chart(prediction['churn_probability']), use_container_width=True)
                
                with col2:
                    st.metric(
                        "Churn Prediction", 
                        prediction['churn_prediction'],
                        help="Whether the customer is likely to churn"
                    )
                    st.metric(
                        "Confidence Level", 
                        prediction['confidence'],
                        help="How confident the model is in this prediction"
                    )
                
                with col3:
                    probability_pct = prediction['churn_probability'] * 100
                    st.metric(
                        "Churn Probability", 
                        f"{probability_pct:.1f}%",
                        help="Exact probability of customer churning"
                    )
                    
                    # Risk level
                    if probability_pct >= 70:
                        risk_level = "🔴 High Risk"
                        risk_color = "red"
                    elif probability_pct >= 30:
                        risk_level = "🟡 Medium Risk"
                        risk_color = "orange"
                    else:
                        risk_level = "🟢 Low Risk"
                        risk_color = "green"
                    
                    st.markdown(f"**Risk Level:** <span style='color:{risk_color}'>{risk_level}</span>", unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("---")
                st.subheader("💡 Recommendations")
                
                if prediction['churn_prediction'] == "Yes":
                    st.warning("""
                    **High Churn Risk Detected!** Consider these retention strategies:
                    - Offer personalized discounts or promotions
                    - Improve customer service engagement
                    - Provide additional value-added services
                    - Consider contract extension incentives
                    """)
                else:
                    st.info("""
                    **Low Churn Risk** - This customer appears satisfied. Consider:
                    - Upselling additional services
                    - Loyalty program enrollment
                    - Referral incentives
                    """)
    
    with tab2:
        st.header("📊 Batch Prediction")
        st.markdown("Upload a CSV file with customer data for batch prediction")
        
        # Sample data template
        with st.expander("📋 View Required CSV Format"):
            sample_data = pd.DataFrame({
                'tenure': [12, 24, 6],
                'monthly_charges': [65.0, 89.5, 45.0],
                'total_charges': [780.0, 2148.0, 270.0],
                'contract_type': ['Month-to-month', 'One year', 'Month-to-month'],
                'payment_method': ['Electronic check', 'Credit card (automatic)', 'Mailed check'],
                'paperless_billing': ['Yes', 'No', 'Yes'],
                'internet_service': ['DSL', 'Fiber optic', 'DSL'],
                'online_security': ['No', 'Yes', 'No'],
                'online_backup': ['No', 'Yes', 'No'],
                'device_protection': ['No', 'Yes', 'No'],
                'tech_support': ['No', 'Yes', 'No'],
                'streaming_tv': ['No', 'Yes', 'No'],
                'streaming_movies': ['No', 'Yes', 'No']
            })
            st.dataframe(sample_data)
            
            # Download template
            csv = sample_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Template",
                data=csv,
                file_name='customer_data_template.csv',
                mime='text/csv'
            )
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File uploaded successfully! Found {len(df)} customers.")
                
                # Show preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head())
                
                if st.button("🔮 Predict Batch", use_container_width=True):
                    # Note: For batch prediction, you'd need to implement the batch endpoint call
                    # This is a simplified version that calls single predictions
                    st.info("💡 Batch prediction feature would be implemented here using the /predict_batch endpoint")
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with tab3:
        st.header("📈 Model Analytics")
        st.info("🚧 This section would contain model performance metrics, feature importance, and other analytics.")
        
        # Placeholder for analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Model Performance")
            # Placeholder metrics
            metrics_data = {
                'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                'Value': [0.85, 0.82, 0.78, 0.80]
            }
            metrics_df = pd.DataFrame(metrics_data)
            
            fig = px.bar(metrics_df, x='Metric', y='Value', 
                        title="Model Performance Metrics",
                        color='Value', color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Feature Importance")
            # Placeholder feature importance
            features_data = {
                'Feature': ['Monthly Charges', 'Tenure', 'Contract Type', 'Total Charges', 'Internet Service'],
                'Importance': [0.25, 0.22, 0.18, 0.15, 0.12]
            }
            features_df = pd.DataFrame(features_data)
            
            fig = px.horizontal_bar(features_df, x='Importance', y='Feature',
                                  title="Top 5 Important Features",
                                  orientation='h')
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 
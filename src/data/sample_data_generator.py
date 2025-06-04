import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_customer_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate a sample dataset for customer churn prediction.
    
    Features:
    - customer_id: Unique identifier for each customer
    - tenure: Number of months the customer has stayed with the company
    - monthly_charges: The amount charged to the customer monthly
    - total_charges: The total amount charged to the customer
    - contract_type: Type of contract (Month-to-month, One year, Two year)
    - payment_method: Method of payment (Electronic check, Mailed check, Bank transfer, Credit card)
    - paperless_billing: Whether the customer has paperless billing (Yes/No)
    - internet_service: Type of internet service (DSL, Fiber optic, No)
    - online_security: Whether the customer has online security (Yes/No/No internet service)
    - online_backup: Whether the customer has online backup (Yes/No/No internet service)
    - device_protection: Whether the customer has device protection (Yes/No/No internet service)
    - tech_support: Whether the customer has tech support (Yes/No/No internet service)
    - streaming_tv: Whether the customer has streaming TV (Yes/No/No internet service)
    - streaming_movies: Whether the customer has streaming movies (Yes/No/No internet service)
    - churn: Whether the customer churned (Yes/No)
    """
    np.random.seed(42)
    
    # Generate customer IDs
    customer_ids = [f'CUST{i:06d}' for i in range(n_samples)]
    
    # Generate tenure (months)
    tenure = np.random.randint(1, 73, n_samples)  # 1-72 months
    
    # Generate monthly charges
    monthly_charges = np.random.normal(65, 30, n_samples)
    monthly_charges = np.clip(monthly_charges, 20, 120)  # Clip between 20 and 120
    
    # Calculate total charges (with some noise)
    total_charges = monthly_charges * tenure * (1 + np.random.normal(0, 0.1, n_samples))
    total_charges = np.clip(total_charges, 0, None)  # Ensure non-negative
    
    # Generate categorical features
    contract_types = np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples, p=[0.5, 0.3, 0.2])
    payment_methods = np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], 
                                     n_samples, p=[0.3, 0.2, 0.25, 0.25])
    paperless_billing = np.random.choice(['Yes', 'No'], n_samples, p=[0.6, 0.4])
    internet_services = np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples, p=[0.3, 0.4, 0.3])
    
    # Generate service features
    service_features = ['online_security', 'online_backup', 'device_protection', 
                       'tech_support', 'streaming_tv', 'streaming_movies']
    
    service_data = {}
    for feature in service_features:
        # For customers with no internet service, set to 'No internet service'
        values = np.where(internet_services == 'No', 
                         'No internet service',
                         np.random.choice(['Yes', 'No'], n_samples, p=[0.4, 0.6]))
        service_data[feature] = values
    
    # Generate churn (target variable)
    # Higher probability of churn for:
    # - Month-to-month contracts
    # - Higher monthly charges
    # - No additional services
    churn_prob = (
        (contract_types == 'Month-to-month') * 0.3 +
        (monthly_charges > 70) * 0.2 +
        (np.sum([service_data[feature] == 'Yes' for feature in service_features], axis=0) == 0) * 0.2
    )
    churn_prob = np.clip(churn_prob, 0, 1)
    churn = np.random.binomial(1, churn_prob)
    churn = np.where(churn == 1, 'Yes', 'No')
    
    # Create DataFrame
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'tenure': tenure,
        'monthly_charges': monthly_charges,
        'total_charges': total_charges,
        'contract_type': contract_types,
        'payment_method': payment_methods,
        'paperless_billing': paperless_billing,
        'internet_service': internet_services,
        **service_data,
        'churn': churn
    })
    
    # Add some missing values
    df.loc[np.random.choice(df.index, 50), 'total_charges'] = np.nan
    df.loc[np.random.choice(df.index, 30), 'payment_method'] = np.nan
    
    return df

if __name__ == "__main__":
    # Generate and save sample data
    df = generate_customer_data()
    df.to_csv('data/customer_churn_data.csv', index=False)
    print("Sample customer churn dataset generated and saved to 'data/customer_churn_data.csv'") 
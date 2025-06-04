# Machine Learning Project

This project demonstrates a production-ready machine learning pipeline with the following components:

- Data Ingestion
- Data Preprocessing
- Model Training and Selection
- Model Validation
- Feature Pipeline Testing

## Project Structure

```
.
├── data/               # Dataset directory
├── src/               # Source code
│   ├── data/         # Data ingestion and preprocessing
│   ├── features/     # Feature engineering
│   ├── models/       # Model training and selection
│   └── utils/        # Utility functions
├── tests/            # Unit tests
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## Dataset Description

The project uses a synthetic customer churn dataset with the following features:

### Customer Information
- `customer_id`: Unique identifier for each customer
- `tenure`: Number of months the customer has stayed with the company (1-72 months)
- `monthly_charges`: The amount charged to the customer monthly ($20-$120)
- `total_charges`: The total amount charged to the customer (with some random noise)

### Contract Details
- `contract_type`: Type of contract
  - Month-to-month (50% of customers)
  - One year (30% of customers)
  - Two year (20% of customers)
- `payment_method`: Method of payment
  - Electronic check (30%)
  - Mailed check (20%)
  - Bank transfer (25%)
  - Credit card (25%)
- `paperless_billing`: Whether the customer has paperless billing (60% Yes, 40% No)

### Service Information
- `internet_service`: Type of internet service
  - DSL (30%)
  - Fiber optic (40%)
  - No service (30%)
- Additional services (Yes/No/No internet service):
  - `online_security`
  - `online_backup`
  - `device_protection`
  - `tech_support`
  - `streaming_tv`
  - `streaming_movies`

### Target Variable
- `churn`: Whether the customer left the company (Yes/No)

### Data Generation Process

The dataset is generated with realistic patterns and correlations:

1. **Base Features**:
   - Customer IDs are generated sequentially
   - Tenure is randomly distributed between 1-72 months
   - Monthly charges follow a normal distribution centered at $65 with std of $30
   - Total charges are calculated as monthly_charges × tenure with added noise

2. **Categorical Features**:
   - Contract types and payment methods are generated with specified probabilities
   - Internet service type affects available add-on services
   - Customers with no internet service cannot have add-on services

3. **Churn Probability**:
   The target variable (churn) is generated based on the following factors:
   - Higher probability for month-to-month contracts (+30%)
   - Higher probability for customers with monthly charges > $70 (+20%)
   - Higher probability for customers with no additional services (+20%)
   - Final probability is clipped between 0 and 1

4. **Missing Values**:
   - 50 random missing values in total_charges
   - 30 random missing values in payment_method

This synthetic dataset mimics real-world patterns in customer churn while maintaining controlled conditions for testing and development.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Data Ingestion:
```bash
python src/data/data_ingestion.py
```

2. Model Training:
```bash
python src/models/train.py
```

3. Run Tests:
```bash
pytest tests/
```

## Features

- Object-oriented design following SOLID principles
- Clean and maintainable code structure
- Multiple model comparison and selection
- Comprehensive testing suite
- Production-ready pipeline 
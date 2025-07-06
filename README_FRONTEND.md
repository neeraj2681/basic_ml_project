# Customer Churn Prediction Frontend

A beautiful Streamlit web interface for the Customer Churn Prediction API.

## Features

🎯 **Interactive Dashboard**: User-friendly interface for churn prediction
📊 **Visual Analytics**: Gauge charts and risk assessment visualization  
📈 **Batch Processing**: Upload CSV files for bulk predictions
🔄 **Real-time API Integration**: Seamless communication with FastAPI backend
📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run both FastAPI backend (Docker) + Streamlit frontend
./run_app.sh

# Or run everything locally (for development)
./run_app.sh --local
```

### Option 2: Manual Setup

1. **Start the FastAPI Backend**:
   ```bash
   # Using Docker (recommended)
   docker run -p 8000:8000 basic-ml-app
   
   # Or locally
   python app.py
   ```

2. **Start the Streamlit Frontend**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Access the Application

- **🎨 Streamlit Frontend**: http://localhost:8501
- **🔧 FastAPI Backend**: http://localhost:8000  
- **📚 API Documentation**: http://localhost:8000/docs

## Using the Frontend

### Single Prediction Tab
1. Fill in customer information in the form
2. Click "🔮 Predict Churn" to get the prediction
3. View results with probability gauge and risk assessment
4. Get personalized recommendations based on the prediction

### Batch Prediction Tab
1. Download the CSV template
2. Fill in multiple customer records
3. Upload the CSV file
4. Get predictions for all customers at once

### Analytics Tab
- View model performance metrics
- See feature importance charts
- Analyze prediction patterns

## Input Fields

| Field | Type | Description |
|-------|------|-------------|
| Tenure | Number | Months with the company (0-100) |
| Monthly Charges | Number | Monthly charges in dollars |
| Total Charges | Number | Total charges accumulated |
| Contract Type | Select | Month-to-month, One year, Two year |
| Payment Method | Select | Payment method used |
| Paperless Billing | Select | Yes/No |
| Internet Service | Select | DSL, Fiber optic, No |
| Online Security | Select | Yes, No, No internet service |
| Online Backup | Select | Yes, No, No internet service |
| Device Protection | Select | Yes, No, No internet service |
| Tech Support | Select | Yes, No, No internet service |
| Streaming TV | Select | Yes, No, No internet service |
| Streaming Movies | Select | Yes, No, No internet service |

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `GET /health` - Check API health status
- `POST /predict` - Single customer prediction
- `POST /predict_batch` - Batch predictions (planned)

## Troubleshooting

### Common Issues

1. **API Not Responding**:
   - Make sure FastAPI backend is running on port 8000
   - Check if Docker container is running: `docker ps`
   - Verify health endpoint: `curl http://localhost:8000/health`

2. **Dependencies Missing**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**:
   ```bash
   # Kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

### Development Mode

For development, run locally with auto-reload:

```bash
# FastAPI with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Streamlit with auto-reload (in separate terminal)
streamlit run streamlit_app.py --server.runOnSave true
```

## Architecture

```
┌─────────────────┐    HTTP/API    ┌─────────────────┐
│   Streamlit     │◄──────────────►│   FastAPI       │
│   Frontend      │     Requests   │   Backend       │
│   (Port 8501)   │                │   (Port 8000)   │
└─────────────────┘                └─────────────────┘
                                           │
                                           ▼
                                   ┌─────────────────┐
                                   │   ML Model      │
                                   │   (Joblib)      │
                                   └─────────────────┘
```

## Customization

### Styling
- Modify the Streamlit theme in `.streamlit/config.toml`
- Customize colors and fonts in the Streamlit app

### Features
- Add new visualization charts
- Implement additional API endpoints
- Extend the analytics dashboard

## Security Notes

- The frontend runs on HTTP (development mode)
- For production, use HTTPS and proper authentication
- Validate all user inputs on the backend
- Consider rate limiting for the API

## Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. View FastAPI logs: `docker logs basic-ml-app-container`
3. Check Streamlit console output for errors 
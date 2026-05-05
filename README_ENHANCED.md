# Data Visioneers - Enhanced Financial Forecasting System

## Overview

**Data Visioneers** is a web-based Financial Forecasting and Prescriptive Recommendation System designed for engineering firms to monitor, predict, and manage project finances. This enhanced version aligns with the thesis research (Chapters 1-3) and implements a comprehensive framework for financial decision-support.

## Key Enhancements

### 1. Project-Based Analysis
- **Multi-Project Management**: Users can create and manage multiple projects independently.
- **Per-Project Dashboards**: Each project has its own comprehensive dashboard with KPIs, predictions, and recommendations.
- **Organized Data**: Financial data is organized by project, enabling comparison and historical tracking.

### 2. Model Evaluation Metrics
The system now calculates and displays **Mean Absolute Error (MAE)** and **Root Mean Square Error (RMSE)** for each model:
- **Multiple Linear Regression (MLR)**: Baseline interpretable model for linear relationships.
- **Random Forest (RF)**: Captures nonlinear patterns and complex feature interactions.
- **ARIMA**: Time-series validation to confirm trend direction consistency.

### 3. Enhanced Prescriptive Recommendations
Recommendations are now context-aware and based on:
- **Forecast Outputs**: Predictions from MLR and RF models.
- **Risk Thresholds**: Automatic classification into Stable, Warning, or Critical risk levels.
- **Trend Validation**: ARIMA confirms whether trends are consistent over time.
- **Actionable Advice**: Specific guidance for cost control, budget reallocation, and contingency planning.

### 4. Professional UI/UX
- **Modern Design**: Clean, responsive interface with gradient navigation and card-based layouts.
- **Data Visualization**: Interactive charts using Chart.js for balance trends, financial distribution, and cost comparisons.
- **Accessibility**: Intuitive navigation, clear labeling, and visual hierarchy.
- **Mobile-Responsive**: Works seamlessly on desktop, tablet, and mobile devices.

### 5. Comprehensive System Architecture

The system follows the conceptual framework from the thesis:

```
INPUT → DATA PREPROCESSING → FORECASTING MODELS → PREDICTION INTEGRATION → RECOMMENDATIONS → OUTPUT
```

#### Modules:
1. **Data Input Module**: Accepts project financial data via CSV upload.
2. **Data Preprocessing Module**: Cleans, normalizes, and prepares time-series data.
3. **Forecasting Module**: Implements MLR, RF, and ARIMA models.
4. **Prediction Integration**: Combines model outputs for unified insights.
5. **Recommendation Engine**: Generates prescriptive actions based on forecasts and risk levels.
6. **Reporting & Dashboard**: Displays KPIs, predictions, metrics, and recommendations.

## Features

### User Management
- **Secure Registration & Login**: Password hashing with Werkzeug.
- **Role-Based Access**: Admin and regular user roles.
- **Profile Management**: Users can update their passwords.
- **Audit Logging**: All actions are logged for accountability.

### Project Management
- **Create Projects**: Define project name and description.
- **Upload Financial Data**: CSV files with required columns.
- **View Project Dashboard**: Real-time KPIs and forecasts.
- **Detailed Analysis**: Interactive visualizations and statistical summaries.

### Financial Analysis
- **Key Performance Indicators (KPIs)**:
  - Project Cost
  - VAT (Value Added Tax)
  - Payments Made
  - Percent Accomplished
  - Current Balance

- **Model Predictions**:
  - MLR predicted balance with MAE/RMSE
  - RF predicted balance with MAE/RMSE
  - ARIMA trend validation with MAE/RMSE

- **Risk Assessment**:
  - **Stable**: Balance is healthy and on track.
  - **Warning**: Declining balance trend detected; review spending.
  - **Critical**: Negative balance or severe decline; immediate action required.

### Visualizations
- **Balance Trend Chart**: Line chart showing balance over time.
- **Financial Distribution**: Doughnut chart of cost components.
- **Cost Comparison**: Bar chart comparing project cost, VAT, and payments.
- **Data Tables**: Detailed financial records with risk indicators.

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.8+, Flask |
| Database | MySQL/MariaDB / PostgreSQL (Cloud-ready) |
| Frontend | HTML5, CSS3, JavaScript |
| Charting | Chart.js 3.9.1 |
| ML/Statistics | scikit-learn, pandas, numpy, statsmodels |
| Security | Werkzeug, Flask-Talisman, Flask-SeaSurf, Flask-Limiter |
| Compliance | ISO 25010 Standards |

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL/MariaDB database server
- pip (Python package manager)

### Step 1: Clone/Extract Project
```bash
cd /path/to/Data-Visioneers
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Log into MySQL
mysql -u root -p

# Create database and apply schema
CREATE DATABASE thesis_finance;
USE thesis_finance;
SOURCE schema.sql;
```

### Step 5: Environment Configuration
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### Step 6: Run Application
```bash
python app_enhanced.py
```

The application will run on `http://localhost:5000/`

## CSV Data Format

Your CSV file must contain these columns (exact names required):

| Column | Type | Description |
|--------|------|-------------|
| Project ID | String | Unique identifier for the project |
| Date | String | Date of the record (YYYY-MM-DD) |
| Period Index | Numeric | Sequential index of the period |
| Project Cost (PHP) | Numeric | Total project cost in PHP |
| VAT (12%) | Numeric | Value Added Tax amount (12%) |
| Payments Made | Numeric | Cumulative payments made |
| Percent Accomplished | Numeric | Project progress percentage |
| Financial Balance | Numeric | Current financial balance |
| Labor Cost | Numeric | Cost associated with labor |
| Material Cost | Numeric | Cost associated with materials |
| Equipment Cost | Numeric | Cost associated with equipment |
| Overhead | Numeric | Overhead costs |
| Lag Project Cost | Numeric | Project cost from the previous period |
| Lag Payments | Numeric | Payments from the previous period |
| Rolling Avg Cost (7) | Numeric | 7-period rolling average cost |
| Rolling Sum Payments (7) | Numeric | 7-period rolling sum of payments |
| Cost-to-Progress Ratio | Numeric | Ratio of cost to progress |
| Cumulative Payments | Numeric | Total cumulative payments |
| Variance | Numeric | Financial variance |

### Example CSV:
```csv
Project ID,Date,Period Index,Project Cost (PHP),VAT (12%),Payments Made,Percent Accomplished,Financial Balance,Labor Cost,Material Cost,Equipment Cost,Overhead,Lag Project Cost,Lag Payments,Rolling Avg Cost (7),Rolling Sum Payments (7),Cost-to-Progress Ratio,Cumulative Payments,Variance
PRJ-001,2019-01-01 0:00:00,1,21631929.32,2595831.519,16852.72242,0.076137625,24210908.12,8440070.415,10634570.46,2207721.165,349567.2892,,,284112422.4,16852.72242,21615076.6
```

## Usage Workflow

1. **Register**: Create a user account.
2. **Login**: Access the system.
3. **Create Project**: Define a new engineering project.
4. **Upload Data**: Upload CSV with financial records.
5. **View Dashboard**: See KPIs and model predictions.
6. **Review Recommendations**: Read prescriptive guidance.
7. **Analyze Trends**: Explore detailed visualizations.
8. **Make Decisions**: Use insights for financial planning.

## Model Evaluation

### Mean Absolute Error (MAE)
Measures average prediction error in absolute terms. Lower values indicate better accuracy.

### Root Mean Square Error (RMSE)
Penalizes larger errors more heavily. Useful for detecting outliers and model stability.

### Model Selection
- **MLR**: Best for interpretability and linear relationships.
- **RF**: Best for capturing complex, nonlinear patterns.
- **ARIMA**: Best for validating temporal trends and seasonality.

## Prescriptive Recommendations Framework

Recommendations are generated based on:

1. **Forecast Comparison**: If MLR and RF predictions are lower than current balance, a warning is issued.
2. **Risk Thresholds**:
   - Decline > 10%: Critical risk
   - Decline 5-10%: Warning risk
   - Negative balance: Critical risk
3. **ARIMA Validation**: Confirms trend direction consistency.
4. **Actionable Advice**: Specific actions (cost control, budget review, contingency planning).

## Admin Features

- **User Management**: View all registered users and their roles.
- **Audit Logs**: Monitor system activities and user actions.
- **System Monitoring**: Track uploads, predictions, and recommendations.

## Security Features

- **Password Hashing**: Werkzeug secure password hashing.
- **Session Management**: Secure session handling.
- **Input Validation**: CSV format and required field validation.
- **Database Constraints**: Foreign keys and data integrity.
- **Audit Trail**: Complete action logging for accountability.

## Troubleshooting

### CSV Upload Fails
- Ensure all required columns are present with exact names.
- Check that numeric columns contain valid numbers.
- Verify file is in UTF-8 encoding.

### Models Not Training
- Ensure at least 3 rows of data for MLR/RF.
- Ensure at least 6 rows for ARIMA.
- Check for missing or invalid numeric values.

### Database Connection Error
- Verify MySQL/MariaDB is running.
- Check .env credentials match database setup.
- Ensure database and tables are created.

## Future Enhancements

- **Export Reports**: PDF/Excel export of dashboards and recommendations.
- **Predictive Intervals**: Confidence intervals for forecasts.
- **Advanced Visualizations**: 3D charts, heatmaps, and interactive dashboards.
- **API Integration**: RESTful API for external integrations.
- **Mobile App**: Native mobile application.
- **Real-Time Alerts**: Email/SMS notifications for critical risks.
- **Collaborative Features**: Team-based project management.

## References

This system is based on research from:
- Wasserbacher & Spindler (2022): Decision-support frameworks for forecasting.
- Rehman (2026): Project performance prediction using ML.
- Zheng et al. (2023): Random Forest for construction cost prediction.
- Gonzales et al. (2017): ARIMA for time-series forecasting.

## Contact & Support

For questions or issues, please refer to the project documentation or contact the development team.

## License

This project is developed as part of academic research. All rights reserved.

---

**Data Visioneers** - Empowering Engineering Firms with AI-Driven Financial Forecasting

# Thesis Requirements - Data Visioneers

## Core Objectives
- Develop a web-based financial forecasting system for engineering firms.
- Use **Multiple Linear Regression (MLR)** and **Random Forest (RF)** as primary forecasting models.
- Use **ARIMA** as a supporting model for trend validation.
- Translate forecasts into **prescriptive recommendations**.
- Evaluate model performance using **MAE** and **RMSE**.

## Data Inputs
- Project Cost
- VAT (Value Added Tax)
- Payments Made
- Percent Accomplished
- Balance
- Time Variable (Date/Period)

## System Architecture / Modules
1. **Data Input Module**: Collects project financial and progress variables.
2. **Data Preprocessing Module**: Cleaning, handling missing values, normalization, and time-series preparation.
3. **Forecasting Module**: Implements MLR, RF, and ARIMA.
4. **Recommendation Module**: Translates outputs into actionable advice (e.g., cost control alerts, budget reallocation).
5. **Reporting & Dashboard Module**: Displays forecasts, trends, and recommendations.
6. **Evaluation Module**: Supports software quality testing and model evaluation (MAE, RMSE).

## Key Enhancements Needed
- **Project-based Analysis**: The system should display analysis *per project*.
- **Model Evaluation**: Include MAE and RMSE for the models.
- **Improved UI/UX**: Professional and "good looking" as requested by the user.
- **Trend Validation**: Explicitly use ARIMA for trend validation alongside MLR and RF.
- **Prescriptive Recommendations**: More detailed and context-aware advice based on model outputs.

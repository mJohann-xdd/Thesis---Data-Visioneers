# Data Visioneers - Complete Setup Instructions

## 🚀 Quick Start Guide

Follow these steps to get the **Data Visioneers** application running on your computer.

---

## Prerequisites

Before you start, make sure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL Server** (or MariaDB) - [Download MySQL](https://dev.mysql.com/downloads/mysql/) or [Download MariaDB](https://mariadb.org/download/)
- **Git** (optional, for cloning) - [Download Git](https://git-scm.com/)

### Verify Installation

Open your terminal/command prompt and run:

```bash
python --version
mysql --version
```

Both should show version numbers. If not, install them first.

---

## Step 1: Extract the Project

Extract the **Enhanced-Data-Visioneers-Complete.zip** file to your desired location.

```bash
# Example on Windows
# Right-click the ZIP file → Extract All → Choose folder

# Example on Mac/Linux
unzip Enhanced-Data-Visioneers-Complete.zip -d ~/projects/
cd ~/projects/Enhanced-Data-Visioneers-Complete
```

---

## Step 2: Set Up MySQL Database

### 2.1 Start MySQL Server

**Windows:**
- MySQL Server should start automatically. If not, search for "Services" and start "MySQL80" (or your version).

**Mac:**
```bash
mysql.server start
```

**Linux:**
```bash
sudo systemctl start mysql
```

### 2.2 Create Database and Tables

Open a terminal and connect to MySQL:

```bash
mysql -u root -p
```

When prompted, enter your MySQL root password (leave blank if you didn't set one).

Once connected, copy and paste the following commands:

```sql
CREATE DATABASE IF NOT EXISTS thesis_finance;
USE thesis_finance;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(80) NOT NULL,
  last_name VARCHAR(80) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','user') NOT NULL DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  project_name VARCHAR(255) NOT NULL,
  project_description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS uploads (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_id INT NOT NULL,
  user_id INT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS finance_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  upload_id INT NOT NULL,
  period VARCHAR(50) NOT NULL,
  project_cost DECIMAL(14,2) NOT NULL,
  vat DECIMAL(14,2) NOT NULL,
  payments_made DECIMAL(14,2) NOT NULL,
  percent_accomplished DECIMAL(6,2) NOT NULL,
  balance DECIMAL(14,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (upload_id) REFERENCES uploads(id)
);

CREATE TABLE IF NOT EXISTS predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  upload_id INT NOT NULL,
  model_name ENUM('mlr','rf','arima') NOT NULL,
  predicted_balance DECIMAL(14,2) NOT NULL,
  mae DECIMAL(14,4),
  rmse DECIMAL(14,4),
  note VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (upload_id) REFERENCES uploads(id)
);

CREATE TABLE IF NOT EXISTS recommendations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  upload_id INT NOT NULL,
  risk_level ENUM('stable','warning','critical') NOT NULL,
  recommendation_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (upload_id) REFERENCES uploads(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  action VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Type `exit` to close MySQL:

```bash
exit
```

---

## Step 3: Set Up Python Environment

### 3.1 Create Virtual Environment

Navigate to your project folder and create a virtual environment:

**Windows:**
```bash
cd path\to\Enhanced-Data-Visioneers-Complete
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
cd path/to/Enhanced-Data-Visioneers-Complete
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal line.

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- mysql-connector-python (database connection)
- pandas (data processing)
- scikit-learn (machine learning)
- statsmodels (time-series analysis)
- numpy (numerical computing)
- Werkzeug (security utilities)
- python-dotenv (environment variables)

---

## Step 4: Configure Environment Variables

The `.env` file is already included in the project. Edit it if needed:

**File:** `.env`

```env
# Flask Configuration
FLASK_APP=app_enhanced.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production-12345

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=thesis_finance
DB_PORT=3306

# Application Settings
DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760
```

**Important:** If your MySQL root user has a password, update the `DB_PASSWORD` line:

```env
DB_PASSWORD=your_mysql_password
```

---

## Step 5: Run the Application

Make sure your virtual environment is activated (you should see `(venv)` in your terminal).

```bash
python app_enhanced.py
```

You should see output like:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## Step 6: Access the Application

Open your web browser and go to:

```
http://localhost:5000
```

You should see the **Data Visioneers** login page.

---

## Step 7: Create Your First Account

1. Click **Register** on the login page
2. Fill in your details:
   - First Name
   - Last Name
   - Email
   - Password
3. Click **Create Account**
4. Login with your credentials

---

## Step 8: Create Your First Project

1. After logging in, click **New Project**
2. Enter:
   - **Project Name** (e.g., "Highway Bridge Construction")
   - **Project Description** (optional)
3. Click **Create Project**

---

## Step 9: Upload Financial Data

1. On the project dashboard, click **Upload Data**
2. Prepare a CSV file with these columns:
   - `Project Cost`
   - `VAT`
   - `Payments Made`
   - `Percent Accomplished`
   - `Balance`
   - `Date/Period`

### Example CSV Format:

```csv
Project Cost,VAT,Payments Made,Percent Accomplished,Balance,Date/Period
1000000,150000,500000,50,650000,2024-01
1100000,165000,600000,55,665000,2024-02
1200000,180000,700000,60,680000,2024-03
1300000,195000,800000,65,695000,2024-04
1400000,210000,900000,70,710000,2024-05
```

3. Click **Select CSV File** and choose your file
4. Click **Upload & Process**

The system will:
- ✅ Clean and validate your data
- ✅ Train forecasting models (MLR, Random Forest, ARIMA)
- ✅ Calculate predictions and accuracy metrics (MAE, RMSE)
- ✅ Generate prescriptive recommendations
- ✅ Display results on the dashboard

---

## Step 10: View Results

After uploading data, you'll see:

### Dashboard Tab:
- **KPI Cards**: Project Cost, VAT, Payments, Accomplishment %, Balance
- **Model Predictions**: MLR, Random Forest, and ARIMA forecasts
- **Accuracy Metrics**: MAE and RMSE for each model
- **Risk Assessment**: Stable/Warning/Critical status
- **Recommendations**: Actionable insights based on forecasts

### Detailed Analysis Tab:
- **Balance Trend Chart**: Line chart showing balance over time
- **Financial Distribution**: Pie chart of cost components
- **Cost Comparison**: Bar chart comparing costs and payments
- **Summary Statistics**: Min, max, average balances
- **Data Table**: Complete financial records

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Make sure your virtual environment is activated:

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Then install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "Can't connect to MySQL server"

**Solution:** Check that:
1. MySQL is running
2. Database name is correct in `.env` (should be `thesis_finance`)
3. Username and password are correct
4. Database tables are created (run the SQL commands from Step 2)

### Problem: "Port 5000 is already in use"

**Solution:** Either:
1. Close the other application using port 5000, or
2. Change the port in `app_enhanced.py`:

Find this line at the bottom:
```python
if __name__ == "__main__":
    app.run(debug=True)
```

Change it to:
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

### Problem: CSV upload fails

**Solution:** Verify your CSV has:
- Exact column names (case-sensitive): `Project Cost`, `VAT`, `Payments Made`, `Percent Accomplished`, `Balance`, `Date/Period`
- No empty rows
- Numeric values in numeric columns
- UTF-8 encoding

### Problem: Models not training

**Solution:** Ensure you have:
- At least 3 rows of data (for MLR and Random Forest)
- At least 6 rows of data (for ARIMA)
- No missing values in numeric columns

---

## File Structure

```
Enhanced-Data-Visioneers-Complete/
├── app_enhanced.py                 # Main Flask application
├── db.py                          # Database connection
├── .env                           # Environment configuration (PRE-CONFIGURED)
├── requirements.txt               # Python dependencies
├── schema.sql                     # Database schema
├── README_ENHANCED.md             # Detailed documentation
├── SETUP_INSTRUCTIONS.md          # This file
├── ENHANCEMENTS_SUMMARY.txt       # Summary of changes
├── templates/
│   ├── base_enhanced.html         # Base template
│   ├── projects.html              # Projects listing
│   ├── new_project.html           # Create project
│   ├── project_dashboard.html     # Main dashboard
│   ├── upload_project_data.html   # Data upload
│   └── project_analysis.html      # Detailed analysis
└── uploads/                       # CSV files storage (auto-created)
```

---

## System Features

### ✅ Multi-Project Management
- Create and manage multiple projects
- Independent data and analysis per project
- Project ownership and access control

### ✅ Financial Forecasting
- Multiple Linear Regression (MLR)
- Random Forest (RF)
- ARIMA time-series validation

### ✅ Model Evaluation
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Accuracy metrics for all models

### ✅ Prescriptive Recommendations
- Automatic risk assessment (Stable/Warning/Critical)
- Context-aware recommendations
- Cost control and budget planning guidance

### ✅ Data Visualization
- Balance trend charts
- Financial distribution pie charts
- Cost comparison bar charts
- Interactive visualizations

### ✅ Professional UI/UX
- Modern, responsive design
- Mobile-friendly interface
- Intuitive navigation
- Professional color scheme

---

## Next Steps

1. **Customize**: Modify the system for your specific needs
2. **Test**: Upload sample data and verify predictions
3. **Deploy**: Move to production when ready
4. **Monitor**: Track system performance and user feedback

---

## Support & Documentation

- **README_ENHANCED.md**: Detailed feature documentation
- **ENHANCEMENTS_SUMMARY.txt**: Summary of all improvements
- **Thesis Reference**: CS0027-DataVisioneers-Chapter1-3

---

## Questions?

Refer to the documentation files included in the project or review the code comments for detailed explanations.

**Happy forecasting! 📊**

---

**Last Updated**: March 2026
**Version**: 2.0 (Enhanced with Project-Based Analysis)
**Status**: Production Ready

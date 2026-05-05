# Complete Setup Guide - Data Visioneers System

This guide will help you set up the updated Data Visioneers system with full support for the advanced dataset schema and ISO 25010 compliance.

## Step 1: Database Migration (If You Have an Existing Database)

If you already have a `thesis_finance` database from a previous version, run the migration script to add all new columns:

```bash
mysql -u root -p thesis_finance < migrate_database.sql
```

If you're starting fresh, simply run the schema:

```bash
mysql -u root -p < schema.sql
```

## Step 2: Install Python Dependencies

Make sure you're in the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Then install the updated requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If you encounter "No matching distribution found for mysql-connector-python":**

Try installing with a specific version:

```bash
pip install mysql-connector-python==8.0.33
```

Or use the alternative MySQL driver:

```bash
pip install mysqlclient
```

## Step 3: Configure Environment Variables

Create or update your `.env` file with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=thesis_finance
DB_PORT=3306
SECRET_KEY=your-secret-key-here
```

For cloud deployment (e.g., Heroku), set the `DATABASE_URL` environment variable instead:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

## Step 4: Run the Application

```bash
python app_enhanced.py
```

The application will start on `http://localhost:5000/`

## Step 5: Upload Your Data

1. Register a new account or login
2. Create a new project
3. Upload a CSV file with the following columns (exact names required):

| Column Name | Type | Example |
|-------------|------|---------|
| Project ID | String | PRJ-001 |
| Date | String | 2019-01-01 0:00:00 |
| Period Index | Numeric | 1 |
| Project Cost (PHP) | Numeric | 21631929.32 |
| VAT (12%) | Numeric | 2595831.519 |
| Payments Made | Numeric | 16852.72242 |
| Percent Accomplished | Numeric | 0.076137625 |
| Financial Balance | Numeric | 24210908.12 |
| Labor Cost | Numeric | 8440070.415 |
| Material Cost | Numeric | 10634570.46 |
| Equipment Cost | Numeric | 2207721.165 |
| Overhead | Numeric | 349567.2892 |
| Lag Project Cost | Numeric | (optional) |
| Lag Payments | Numeric | (optional) |
| Rolling Avg Cost (7) | Numeric | (optional) |
| Rolling Sum Payments (7) | Numeric | (optional) |
| Cost-to-Progress Ratio | Numeric | (optional) |
| Cumulative Payments | Numeric | 284112422.4 |
| Variance | Numeric | 21615076.6 |

## Troubleshooting

### Error: "Unknown column 'labor_cost'"

This means your database hasn't been updated with the new columns. Run the migration script:

```bash
mysql -u root -p thesis_finance < migrate_database.sql
```

### Error: "No matching distribution found for mysql-connector-python"

Upgrade pip and try again:

```bash
python -m pip install --upgrade pip
pip install mysql-connector-python==8.0.33
```

### Error: "Can't connect to MySQL server"

Ensure:
- MySQL is running
- Your credentials in `.env` are correct
- The database exists: `CREATE DATABASE thesis_finance;`

### CSV Upload Fails

Ensure your CSV has:
- Exact column names (case-sensitive)
- Valid numeric values
- UTF-8 encoding
- At least 3 rows for model training

## Features Included

The updated system includes:

1. **Advanced Dataset Support**: Handles all 19 financial variables
2. **ISO 25010 Compliance**: Security, reliability, and maintainability standards
3. **Cloud-Ready**: Supports PostgreSQL and environment-based configuration
4. **Enhanced Security**: CSRF protection, rate limiting, secure headers
5. **Comprehensive Dashboard**: Displays all cost breakdowns and advanced metrics
6. **Machine Learning**: MLR, Random Forest, and ARIMA models with MAE/RMSE metrics

## Deployment to Cloud

### Heroku

1. Create a `Procfile` (already included)
2. Set environment variables:
   ```bash
   heroku config:set DATABASE_URL=postgresql://...
   heroku config:set SECRET_KEY=your-secret-key
   ```
3. Deploy:
   ```bash
   git push heroku main
   ```

### Render / Railway

1. Connect your Git repository
2. Set environment variables in the dashboard
3. Deploy automatically

## Support

For issues or questions, refer to the documentation or contact the development team.

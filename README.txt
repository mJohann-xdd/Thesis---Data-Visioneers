HOW TO RUN (quick)

1) Install packages:
   pip install -r requirements.txt

2) Create database/tables:
   - Open MySQL (phpMyAdmin/Workbench)
   - Run schema.sql

3) Configure DB (optional):
   - Copy .env.example to .env and update DB creds

4) Run Flask:
   python app.py

5) Open:
   http://127.0.0.1:5000/login

NOTES:
- Upload CSV requires these columns:
  Project Cost, VAT, Payments Made, Percent Accomplished, Balance, Date/Period

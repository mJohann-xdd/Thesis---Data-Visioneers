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
  labor_cost DECIMAL(14,2),
  material_cost DECIMAL(14,2),
  equipment_cost DECIMAL(14,2),
  overhead DECIMAL(14,2),
  lag_project_cost DECIMAL(14,2),
  lag_payments DECIMAL(14,2),
  rolling_avg_cost_7 DECIMAL(14,2),
  rolling_sum_payments_7 DECIMAL(14,2),
  cost_to_progress_ratio DECIMAL(14,4),
  cumulative_payments DECIMAL(14,2),
  variance DECIMAL(14,2),
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

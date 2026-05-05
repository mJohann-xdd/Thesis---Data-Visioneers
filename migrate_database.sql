-- Migration Script: Add all new columns to finance_records table
-- Run this if you have an existing database with the old schema

USE thesis_finance;

-- Add missing columns to finance_records table
ALTER TABLE finance_records
ADD COLUMN labor_cost DECIMAL(14,2) AFTER balance,
ADD COLUMN material_cost DECIMAL(14,2) AFTER labor_cost,
ADD COLUMN equipment_cost DECIMAL(14,2) AFTER material_cost,
ADD COLUMN overhead DECIMAL(14,2) AFTER equipment_cost,
ADD COLUMN lag_project_cost DECIMAL(14,2) AFTER overhead,
ADD COLUMN lag_payments DECIMAL(14,2) AFTER lag_project_cost,
ADD COLUMN rolling_avg_cost_7 DECIMAL(14,2) AFTER lag_payments,
ADD COLUMN rolling_sum_payments_7 DECIMAL(14,2) AFTER rolling_avg_cost_7,
ADD COLUMN cost_to_progress_ratio DECIMAL(14,4) AFTER rolling_sum_payments_7,
ADD COLUMN cumulative_payments DECIMAL(14,2) AFTER cost_to_progress_ratio,
ADD COLUMN variance DECIMAL(14,2) AFTER cumulative_payments;

-- Verify the new columns were added
DESCRIBE finance_records;

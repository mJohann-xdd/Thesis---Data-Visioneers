# ISO 25010 Software Quality Compliance Report

This project has been updated to align with the **ISO/IEC 25010:2011** standard for systems and software quality.

## 1. Functional Suitability
- **Functional Completeness**: The system now supports the comprehensive dataset including detailed cost breakdowns (Labor, Material, Equipment, Overhead) and advanced financial metrics (Rolling Averages, Cumulative Payments, Variance).
- **Functional Correctness**: Machine learning models (MLR, RF, ARIMA) provide precise financial forecasting based on the new dataset schema.

## 2. Security
- **Confidentiality**: Password hashing using `Werkzeug`'s security helpers.
- **Integrity**: CSRF protection implemented via `Flask-SeaSurf` to prevent unauthorized command execution.
- **Authenticity**: Secure session management and audit logging of all user actions.
- **Non-repudiation**: Audit logs track every critical action (logins, uploads, project creation) with timestamps and user IDs.
- **Protection**: `Flask-Talisman` integrated for secure HTTP headers (HSTS, XSS protection).
- **Rate Limiting**: `Flask-Limiter` prevents brute-force attacks by limiting request frequency.

## 3. Reliability
- **Maturity**: Automated data validation during CSV uploads ensures only valid data is processed.
- **Fault Tolerance**: Database connection handling with support for both MySQL and PostgreSQL (Cloud-ready).
- **Recoverability**: Transactional database operations with rollbacks on failure.

## 4. Maintainability
- **Modularity**: Separation of concerns between database logic (`db.py`), application logic (`app_enhanced.py`), and presentation (`templates/`).
- **Analysability**: Comprehensive audit logs for system monitoring and debugging.
- **Testability**: Structured schema and clear data mapping for automated testing.

## 5. Portability
- **Installability**: `Procfile` and `requirements.txt` provided for seamless deployment.
- **Adaptability**: Cloud-host ready with environment variable configuration and multi-database support.
- **Replaceability**: Standard CSV-based data exchange format.

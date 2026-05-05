import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from db import get_conn
import json

ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Security Features (ISO 25010: Security)
talisman = Talisman(app, content_security_policy=None)  # Enable HSTS, XSS protection, etc.
csrf = SeaSurf(app)  # CSRF Protection
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    if "user_id" not in session:
        return None
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def log_action(user_id, action, status="OK"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_logs (user_id, action, status) VALUES (%s,%s,%s)",
        (user_id, action, status)
    )
    conn.commit()
    cur.close()
    conn.close()

def require_login() -> bool:
    return "user_id" in session

def require_admin() -> bool:
    user = current_user()
    return bool(user and user["role"] == "admin")

def calculate_metrics(y_true, y_pred):
    """Calculate MAE and RMSE for model evaluation."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return mae, rmse

@app.route("/")
def home():
    if require_login():
        return redirect(url_for("projects"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            log_action(user["id"], "Logged in", "OK")
            return redirect(url_for("projects"))

        flash("Invalid email or password.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        pw2 = request.form.get("confirm_password", "")

        if not first or not last or not email or not pw:
            flash("Please fill up all fields.")
            return render_template("register.html")

        if pw != pw2:
            flash("Passwords do not match.")
            return render_template("register.html")

        pw_hash = generate_password_hash(pw)

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (first_name, last_name, email, password_hash, role) VALUES (%s,%s,%s,%s,'user')",
                (first, last, email, pw_hash)
            )
            conn.commit()
            user_id = cur.lastrowid
            cur.close()
            conn.close()

            log_action(user_id, "Registered account", "OK")
            flash("Account created! You can login now.")
            return redirect(url_for("login"))
        except Exception:
            flash("Email already exists or DB error.")
    return render_template("register.html")

@app.route("/logout")
def logout():
    uid = session.get("user_id")
    session.clear()
    if uid:
        log_action(uid, "Logged out", "OK")
    return redirect(url_for("login"))

@app.route("/projects")
def projects():
    """Display all projects for the current user."""
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM projects WHERE user_id=%s ORDER BY created_at DESC", (user["id"],))
    user_projects = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("projects.html", user=user, projects=user_projects)

@app.route("/project/new", methods=["GET", "POST"])
def new_project():
    """Create a new project."""
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()

    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        project_description = request.form.get("project_description", "").strip()

        if not project_name:
            flash("Project name is required.")
            return render_template("new_project.html", user=user)

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO projects (user_id, project_name, project_description) VALUES (%s,%s,%s)",
                (user["id"], project_name, project_description)
            )
            conn.commit()
            project_id = cur.lastrowid
            cur.close()
            conn.close()

            log_action(user["id"], f"Created project: {project_name}", "OK")
            flash(f"Project '{project_name}' created successfully!")
            return redirect(url_for("project_dashboard", project_id=project_id))
        except Exception as e:
            flash(f"Error creating project: {str(e)}")
    
    return render_template("new_project.html", user=user)

@app.route("/project/<int:project_id>")
def project_dashboard(project_id):
    """Display dashboard for a specific project."""
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Verify project ownership
    cur.execute("SELECT * FROM projects WHERE id=%s AND user_id=%s", (project_id, user["id"]))
    project = cur.fetchone()
    
    if not project:
        flash("Project not found or access denied.")
        cur.close()
        conn.close()
        return redirect(url_for("projects"))

    # Get latest upload for this project
    cur.execute("SELECT * FROM uploads WHERE project_id=%s ORDER BY uploaded_at DESC LIMIT 1", (project_id,))
    upload = cur.fetchone()

    kpis = {"project_cost": 0, "vat": 0, "payments_made": 0, "percent_accomplished": 0, "balance": 0, "period": "-", "labor_cost": 0, "material_cost": 0, "equipment_cost": 0, "overhead": 0, "lag_project_cost": 0, "lag_payments": 0, "rolling_avg_cost_7": 0, "rolling_sum_payments_7": 0, "cost_to_progress_ratio": 0, "cumulative_payments": 0, "variance": 0}
    preds = {"mlr": None, "rf": None, "arima": None}
    model_metrics = {"mlr": {}, "rf": {}, "arima": {}}
    recos = []

    if upload:
        cur.execute("SELECT * FROM finance_records WHERE upload_id=%s ORDER BY id DESC LIMIT 1", (upload["id"],))
        row = cur.fetchone()
        if row:
            kpis = {
                "project_cost": float(row["project_cost"]),
                "vat": float(row["vat"]),
                "payments_made": float(row["payments_made"]),
                "percent_accomplished": float(row["percent_accomplished"]),
                "balance": float(row["balance"]),
                "period": row["period"],
                "labor_cost": float(row["labor_cost"]) if row["labor_cost"] else 0,
                "material_cost": float(row["material_cost"]) if row["material_cost"] else 0,
                "equipment_cost": float(row["equipment_cost"]) if row["equipment_cost"] else 0,
                "overhead": float(row["overhead"]) if row["overhead"] else 0,
                "lag_project_cost": float(row["lag_project_cost"]) if row["lag_project_cost"] else 0,
                "lag_payments": float(row["lag_payments"]) if row["lag_payments"] else 0,
                "rolling_avg_cost_7": float(row["rolling_avg_cost_7"]) if row["rolling_avg_cost_7"] else 0,
                "rolling_sum_payments_7": float(row["rolling_sum_payments_7"]) if row["rolling_sum_payments_7"] else 0,
                "cost_to_progress_ratio": float(row["cost_to_progress_ratio"]) if row["cost_to_progress_ratio"] else 0,
                "cumulative_payments": float(row["cumulative_payments"]) if row["cumulative_payments"] else 0,
                "variance": float(row["variance"]) if row["variance"] else 0
            }

        cur.execute("SELECT model_name, predicted_balance, mae, rmse FROM predictions WHERE upload_id=%s", (upload["id"],))
        for p in cur.fetchall():
            preds[p["model_name"]] = float(p["predicted_balance"])
            model_metrics[p["model_name"]] = {
                "mae": float(p["mae"]) if p["mae"] else None,
                "rmse": float(p["rmse"]) if p["rmse"] else None
            }

        cur.execute("SELECT risk_level, recommendation_text FROM recommendations WHERE upload_id=%s ORDER BY created_at DESC LIMIT 5", (upload["id"],))
        recos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("project_dashboard.html", user=user, project=project, upload=upload, kpis=kpis, preds=preds, model_metrics=model_metrics, recos=recos)

@app.route("/project/<int:project_id>/upload", methods=["GET", "POST"])
def upload_project_data(project_id):
    """Upload CSV data for a specific project."""
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Verify project ownership
    cur.execute("SELECT * FROM projects WHERE id=%s AND user_id=%s", (project_id, user["id"]))
    project = cur.fetchone()
    
    if not project:
        flash("Project not found or access denied.")
        cur.close()
        conn.close()
        return redirect(url_for("projects"))

    if request.method == "POST":
        f = request.files.get("csv_file")
        if not f or f.filename == "":
            flash("Please choose a CSV file.")
            cur.close()
            conn.close()
            return render_template("upload_project_data.html", user=user, project=project)

        if not allowed_file(f.filename):
            flash("Only CSV files are allowed.")
            cur.close()
            conn.close()
            return render_template("upload_project_data.html", user=user, project=project)

        filename = secure_filename(f.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(save_path)

        cur.execute("INSERT INTO uploads (project_id, user_id, filename) VALUES (%s,%s,%s)", (project_id, user["id"], filename))
        conn.commit()
        upload_id = cur.lastrowid

        try:
            df = pd.read_csv(save_path)

            required = ["Project ID", "Date", "Period Index", "Project Cost (PHP)", "VAT (12%)", "Payments Made", "Percent Accomplished", "Financial Balance", "Labor Cost", "Material Cost", "Equipment Cost", "Overhead", "Lag Project Cost", "Lag Payments", "Rolling Avg Cost (7)", "Rolling Sum Payments (7)", "Cost-to-Progress Ratio", "Cumulative Payments", "Variance"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                flash(f"Missing columns: {', '.join(missing)}")
                log_action(user["id"], f"Upload failed: missing columns {missing}", "FAIL")
                cur.close()
                conn.close()
                return render_template("upload_project_data.html", user=user, project=project)

            insert_sql = (
                "INSERT INTO finance_records "
                "(upload_id, period, project_cost, vat, payments_made, percent_accomplished, balance, labor_cost, material_cost, equipment_cost, overhead, lag_project_cost, lag_payments, rolling_avg_cost_7, rolling_sum_payments_7, cost_to_progress_ratio, cumulative_payments, variance) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )

            rows_added = 0
            for _, r in df.head(2000).iterrows():
                cur.execute(insert_sql, (
                    upload_id,
                    str(r["Date"]),
                    float(r["Project Cost (PHP)"]),
                    float(r["VAT (12%)"]),
                    float(r["Payments Made"]),
                    float(r["Percent Accomplished"]),
                    float(r["Financial Balance"]),
                    float(r["Labor Cost"]) if pd.notnull(r["Labor Cost"]) else None,
                    float(r["Material Cost"]) if pd.notnull(r["Material Cost"]) else None,
                    float(r["Equipment Cost"]) if pd.notnull(r["Equipment Cost"]) else None,
                    float(r["Overhead"]) if pd.notnull(r["Overhead"]) else None,
                    float(r["Lag Project Cost"]) if pd.notnull(r["Lag Project Cost"]) else None,
                    float(r["Lag Payments"]) if pd.notnull(r["Lag Payments"]) else None,
                    float(r["Rolling Avg Cost (7)"]) if pd.notnull(r["Rolling Avg Cost (7)"]) else None,
                    float(r["Rolling Sum Payments (7)"]) if pd.notnull(r["Rolling Sum Payments (7)"]) else None,
                    float(r["Cost-to-Progress Ratio"]) if pd.notnull(r["Cost-to-Progress Ratio"]) else None,
                    float(r["Cumulative Payments"]) if pd.notnull(r["Cumulative Payments"]) else None,
                    float(r["Variance"]) if pd.notnull(r["Variance"]) else None
                ))
                rows_added += 1

            last_balance = float(df["Financial Balance"].iloc[-1])

            # Data preprocessing
            num_cols = ["Project Cost (PHP)", "VAT (12%)", "Payments Made", "Percent Accomplished", "Financial Balance"]
            for c in num_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            df = df.dropna(subset=num_cols + ["Date"])

            X = df[["Project Cost (PHP)", "VAT (12%)", "Payments Made", "Percent Accomplished"]].values
            y = df["Financial Balance"].values

            mlr_pred = None
            rf_pred = None
            arima_pred = None
            mlr_mae = None
            mlr_rmse = None
            rf_mae = None
            rf_rmse = None
            arima_mae = None
            arima_rmse = None

            # Multiple Linear Regression
            if len(df) >= 3:
                mlr = LinearRegression()
                mlr.fit(X, y)
                mlr_pred = float(mlr.predict([X[-1]])[0])
                y_pred_mlr = mlr.predict(X)
                mlr_mae, mlr_rmse = calculate_metrics(y, y_pred_mlr)

                # Random Forest
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X, y)
                rf_pred = float(rf.predict([X[-1]])[0])
                y_pred_rf = rf.predict(X)
                rf_mae, rf_rmse = calculate_metrics(y, y_pred_rf)

            # ARIMA for time-series validation
            if len(df) >= 6:
                df_sorted = df.sort_values("Date")
                series = df_sorted["Financial Balance"].astype(float).values

                try:
                    model = ARIMA(series, order=(1, 1, 1))
                    fitted = model.fit()
                    forecast = fitted.forecast(steps=1)
                    arima_pred = float(forecast[0])
                    y_pred_arima = fitted.fittedvalues
                    if len(y_pred_arima) > 0:
                        arima_mae, arima_rmse = calculate_metrics(series[1:], y_pred_arima[1:])
                except Exception:
                    arima_pred = None

            # Save predictions with metrics
            cur.execute("DELETE FROM predictions WHERE upload_id=%s", (upload_id,))

            if mlr_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, mae, rmse, note) VALUES (%s,'mlr',%s,%s,%s,%s)",
                    (upload_id, mlr_pred, mlr_mae, mlr_rmse, "Multiple Linear Regression prediction")
                )

            if rf_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, mae, rmse, note) VALUES (%s,'rf',%s,%s,%s,%s)",
                    (upload_id, rf_pred, rf_mae, rf_rmse, "Random Forest prediction")
                )

            if arima_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, mae, rmse, note) VALUES (%s,'arima',%s,%s,%s,%s)",
                    (upload_id, arima_pred, arima_mae, arima_rmse, "ARIMA time-series forecast (trend validation)")
                )

            # Generate prescriptive recommendations
            cur.execute("DELETE FROM recommendations WHERE upload_id=%s", (upload_id,))

            risk = "stable"
            rec_text = "Balance is stable. Continue monitoring project expenditures and payment schedules."
            
            if mlr_pred and rf_pred:
                avg_pred = (mlr_pred + rf_pred) / 2
                if avg_pred < last_balance * 0.95:
                    risk = "warning"
                    rec_text = "Predicted balance shows declining trend. Recommend strengthening payment monitoring and reviewing spending patterns."
                if last_balance < 0:
                    risk = "critical"
                    rec_text = "Critical: Negative balance detected. Immediate budget review, cost control measures, and contingency planning required."
                elif avg_pred < last_balance * 0.90:
                    risk = "critical"
                    rec_text = "Critical: Forecasts indicate significant balance decline. Recommend immediate cost control review and budget reallocation."

            cur.execute("INSERT INTO recommendations (upload_id, risk_level, recommendation_text) VALUES (%s,%s,%s)", (upload_id, risk, rec_text))

            conn.commit()
            log_action(user["id"], f"Uploaded CSV to project {project['project_name']}: {filename} ({rows_added} rows)", "OK")
            flash("Upload successful! Data processed and models trained.")
        except Exception as e:
            conn.rollback()
            flash(f"CSV read/parse error: {str(e)}")
            log_action(user["id"], f"Upload parse error: {filename}", "FAIL")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("project_dashboard", project_id=project_id))

    cur.close()
    conn.close()
    return render_template("upload_project_data.html", user=user, project=project)

@app.route("/project/<int:project_id>/analysis")
def project_analysis(project_id):
    """Display detailed analysis for a project."""
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    # Verify project ownership
    cur.execute("SELECT * FROM projects WHERE id=%s AND user_id=%s", (project_id, user["id"]))
    project = cur.fetchone()
    
    if not project:
        flash("Project not found or access denied.")
        cur.close()
        conn.close()
        return redirect(url_for("projects"))

    # Get latest upload
    cur.execute("SELECT * FROM uploads WHERE project_id=%s ORDER BY uploaded_at DESC LIMIT 1", (project_id,))
    upload = cur.fetchone()

    periods, balances, costs, vats, payments = [], [], [], [], []
    dist = {"Project Cost": 0, "VAT": 0, "Payments Made": 0}

    if upload:
        cur.execute("SELECT period, project_cost, vat, payments_made, balance FROM finance_records WHERE upload_id=%s ORDER BY id ASC", (upload["id"],))
        rows = cur.fetchall()
        for r in rows:
            periods.append(r["period"])
            balances.append(float(r["balance"]))
            costs.append(float(r["project_cost"]))
            vats.append(float(r["vat"]))
            payments.append(float(r["payments_made"]))
            dist["Project Cost"] += float(r["project_cost"])
            dist["VAT"] += float(r["vat"])
            dist["Payments Made"] += float(r["payments_made"])

    cur.close()
    conn.close()
    return render_template("project_analysis.html", user=user, project=project, periods=periods, balances=balances, costs=costs, vats=vats, payments=payments, dist=dist)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()

    if request.method == "POST":
        old = request.form.get("old_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        if not new:
            flash("Nothing to update.")
            return render_template("profile.html", user=user)

        if new != confirm:
            flash("New passwords do not match.")
            return render_template("profile.html", user=user)

        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT password_hash FROM users WHERE id=%s", (user["id"],))
        db_user = cur.fetchone()

        if not db_user or not check_password_hash(db_user["password_hash"], old):
            flash("Old password is incorrect.")
            cur.close()
            conn.close()
            return render_template("profile.html", user=user)

        new_hash = generate_password_hash(new)
        cur2 = conn.cursor()
        cur2.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, user["id"]))
        conn.commit()

        cur2.close()
        cur.close()
        conn.close()

        log_action(user["id"], "Changed password", "OK")
        flash("Password updated.")

    return render_template("profile.html", user=user)

@app.route("/admin")
def admin():
    if not require_login():
        return redirect(url_for("login"))
    if not require_admin():
        flash("Admins only.")
        return redirect(url_for("projects"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id, first_name, last_name, email, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()

    cur.execute("SELECT a.created_at, u.email, a.action, a.status FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.created_at DESC LIMIT 50")
    logs = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("admin.html", user=current_user(), users=users, logs=logs)

if __name__ == "__main__":
    app.run(debug=True)

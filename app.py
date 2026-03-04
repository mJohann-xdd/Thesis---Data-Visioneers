import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA

from db import get_conn

ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")

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

@app.route("/")
def home():
    if require_login():
        return redirect(url_for("dashboard"))
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
            return redirect(url_for("dashboard"))

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

@app.route("/dashboard")
def dashboard():
    if not require_login():
        return redirect(url_for("login"))

    user = current_user()
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM uploads WHERE user_id=%s ORDER BY uploaded_at DESC LIMIT 1", (user["id"],))
    upload = cur.fetchone()

    kpis = {"project_cost": 0, "vat": 0, "payments_made": 0, "percent_accomplished": 0, "balance": 0, "period": "-"}

    preds = {"mlr": None, "rf": None, "arima": None}
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
                "period": row["period"]
            }

        cur.execute("SELECT model_name, predicted_balance FROM predictions WHERE upload_id=%s", (upload["id"],))
        for p in cur.fetchall():
            preds[p["model_name"]] = float(p["predicted_balance"])

        cur.execute("SELECT risk_level, recommendation_text FROM recommendations WHERE upload_id=%s ORDER BY created_at DESC LIMIT 3", (upload["id"],))
        recos = cur.fetchall()

    cur.close()
    conn.close()

    # Transparent criteria (safe even if no upload/preds)
    criteria = {
        "main_model_used": "None",
        "last_balance": kpis["balance"],
        "main_pred": None,
        "rules": [
            "If main predicted balance < current balance → WARNING",
            "If predicted balance < 0 OR current balance < 0 → CRITICAL",
            "If ARIMA differs a lot from main prediction → add manual review note",
        ],
        "triggered": [],
    }

    # Choose main predicted value (prefer RF, then MLR)
    main_pred = preds.get("rf")
    if main_pred is not None:
        criteria["main_model_used"] = "RF (preferred)"
        criteria["main_pred"] = main_pred
    else:
        main_pred = preds.get("mlr")
        if main_pred is not None:
            criteria["main_model_used"] = "MLR"
            criteria["main_pred"] = main_pred

    # Apply rules and record what triggered
    if criteria["main_pred"] is not None:
        if criteria["main_pred"] < criteria["last_balance"]:
            criteria["triggered"].append(
                "Main prediction is lower than current balance → WARNING rule triggered"
            )

        if criteria["main_pred"] < 0 or criteria["last_balance"] < 0:
            criteria["triggered"].append(
                "Negative balance detected → CRITICAL rule triggered"
            )

    # ARIMA disagreement rule
    if preds.get("arima") is not None and criteria["main_pred"] is not None:
        if abs(preds["arima"] - criteria["main_pred"]) > max(10000, 0.1 * abs(criteria["main_pred"])):
            criteria["triggered"].append(
                "ARIMA differs strongly from main prediction → manual review note triggered"
            )

    return render_template("dashboard.html", user=user, upload=upload, kpis=kpis, preds=preds, recos=recos, criteria=criteria)

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

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not require_login():
        return redirect(url_for("login"))
    user = current_user()

    if request.method == "POST":
        f = request.files.get("csv_file")
        if not f or f.filename == "":
            flash("Please choose a CSV file.")
            return render_template("upload.html", user=user)

        if not allowed_file(f.filename):
            flash("Only CSV files are allowed.")
            return render_template("upload.html", user=user)

        filename = secure_filename(f.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(save_path)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO uploads (user_id, filename) VALUES (%s,%s)", (user["id"], filename))
        conn.commit()
        upload_id = cur.lastrowid

        try:
            df = pd.read_csv(save_path)

            required = ["Project Cost", "VAT", "Payments Made", "Percent Accomplished", "Balance", "Date/Period"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                flash(f"Missing columns: {', '.join(missing)}")
                log_action(user["id"], f"Upload failed: missing columns {missing}", "FAIL")
                cur.close(); conn.close()
                return render_template("upload.html", user=user)

            insert_sql = (
                "INSERT INTO finance_records "
                "(upload_id, period, project_cost, vat, payments_made, percent_accomplished, balance) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            )

            rows_added = 0
            for _, r in df.head(2000).iterrows():
                cur.execute(insert_sql, (
                    upload_id,
                    str(r["Date/Period"]),
                    float(r["Project Cost"]),
                    float(r["VAT"]),
                    float(r["Payments Made"]),
                    float(r["Percent Accomplished"]),
                    float(r["Balance"])
                ))
                rows_added += 1

            last_balance = float(df["Balance"].iloc[-1])
            # ---------- REAL ML + ARIMA PREDICTIONS ----------
            # Clean numeric columns (simple)
            num_cols = ["Project Cost", "VAT", "Payments Made", "Percent Accomplished", "Balance"]
            for c in num_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            df = df.dropna(subset=num_cols + ["Date/Period"])

            # Features (X) and Target (y)
            X = df[["Project Cost", "VAT", "Payments Made", "Percent Accomplished"]].values
            y = df["Balance"].values

            # If too small dataset, just skip models safely
            mlr_pred = None
            rf_pred = None
            arima_pred = None

            if len(df) >= 3:
                # Multiple Linear Regression
                mlr = LinearRegression()
                mlr.fit(X, y)
                mlr_pred = float(mlr.predict([X[-1]])[0])  # predict for latest row

                # Random Forest
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X, y)
                rf_pred = float(rf.predict([X[-1]])[0])    # predict for latest row

            # ARIMA (time series support) - forecast next balance
            # Needs enough points, usually at least 6 for stable result
            if len(df) >= 6:
                # Sort by Date/Period (works if YYYY-MM format or sortable strings)
                df_sorted = df.sort_values("Date/Period")
                series = df_sorted["Balance"].astype(float).values

                try:
                    # Simple ARIMA order (1,1,1) for student demo
                    model = ARIMA(series, order=(1, 1, 1))
                    fitted = model.fit()
                    forecast = fitted.forecast(steps=1)
                    arima_pred = float(forecast[0])
                except Exception:
                    arima_pred = None

            # Save predictions to DB (clear older predictions for same upload first)
            cur.execute("DELETE FROM predictions WHERE upload_id=%s", (upload_id,))

            if mlr_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'mlr',%s,%s)",
                    (upload_id, mlr_pred, "Multiple Linear Regression prediction")
                )

            if rf_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'rf',%s,%s)",
                    (upload_id, rf_pred, "Random Forest prediction")
                )

            if arima_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'arima',%s,%s)",
                    (upload_id, arima_pred, "ARIMA next-step forecast (time series support)")
                )

            # ---------- REAL ML + ARIMA PREDICTIONS ----------
            # Clean numeric columns (simple)
            num_cols = ["Project Cost", "VAT", "Payments Made", "Percent Accomplished", "Balance"]
            for c in num_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            df = df.dropna(subset=num_cols + ["Date/Period"])

            # Features (X) and Target (y)
            X = df[["Project Cost", "VAT", "Payments Made", "Percent Accomplished"]].values
            y = df["Balance"].values

            # If too small dataset, just skip models safely
            mlr_pred = None
            rf_pred = None
            arima_pred = None

            if len(df) >= 3:
                # Multiple Linear Regression
                mlr = LinearRegression()
                mlr.fit(X, y)
                mlr_pred = float(mlr.predict([X[-1]])[0])  # predict for latest row

                # Random Forest
                rf = RandomForestRegressor(n_estimators=100, random_state=42)
                rf.fit(X, y)
                rf_pred = float(rf.predict([X[-1]])[0])    # predict for latest row

            # ARIMA (time series support) - forecast next balance
            # Needs enough points, usually at least 6 for stable result
            if len(df) >= 6:
                # Sort by Date/Period (works if YYYY-MM format or sortable strings)
                df_sorted = df.sort_values("Date/Period")
                series = df_sorted["Balance"].astype(float).values

                try:
                    # Simple ARIMA order (1,1,1) for student demo
                    model = ARIMA(series, order=(1, 1, 1))
                    fitted = model.fit()
                    forecast = fitted.forecast(steps=1)
                    arima_pred = float(forecast[0])
                except Exception:
                    arima_pred = None

            # Save predictions to DB (clear older predictions for same upload first)
            cur.execute("DELETE FROM predictions WHERE upload_id=%s", (upload_id,))

            if mlr_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'mlr',%s,%s)",
                    (upload_id, mlr_pred, "Multiple Linear Regression prediction")
                )

            if rf_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'rf',%s,%s)",
                    (upload_id, rf_pred, "Random Forest prediction")
                )

            if arima_pred is not None:
                cur.execute(
                    "INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'arima',%s,%s)",
                    (upload_id, arima_pred, "ARIMA next-step forecast (time series support)")
                )

            # ---------- SIMPLE PRESCRIPTIVE RECOMMENDATIONS ----------
            last_balance = float(df["Balance"].iloc[-1])

            # Choose a "main" predicted value: prefer RF, then MLR, else last balance
            main_pred = rf_pred if rf_pred is not None else (mlr_pred if mlr_pred is not None else last_balance)

            risk = "stable"
            rec_text = "Balance looks stable. Continue monitoring."

            # Example thresholds (student-friendly)
            if main_pred < last_balance:
                risk = "warning"
                rec_text = "Forecast shows a possible decrease in balance. Review expenses and payment schedule."

            if main_pred < 0 or last_balance < 0:
                risk = "critical"
                rec_text = "Balance is negative or forecasted to be negative. Immediate budget review and cost control recommended."

            # If ARIMA disagrees strongly, add note
            if arima_pred is not None and abs(arima_pred - main_pred) > max(10000, 0.1 * abs(main_pred)):
                rec_text += " ARIMA trend check shows a different direction—consider manual review."

            cur.execute("DELETE FROM recommendations WHERE upload_id=%s", (upload_id,))
            cur.execute(
                "INSERT INTO recommendations (upload_id, risk_level, recommendation_text) VALUES (%s,%s,%s)",
                (upload_id, risk, rec_text)
            )

            cur.execute("INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'mlr',%s,'Simple demo')", (upload_id, mlr_pred))
            cur.execute("INSERT INTO predictions (upload_id, model_name, predicted_balance, note) VALUES (%s,'rf',%s,'Simple demo')", (upload_id, rf_pred))

            risk = "stable"
            rec_text = "Balance looks stable. Continue monitoring."
            if mlr_pred < last_balance or rf_pred < last_balance:
                risk = "warning"
                rec_text = "Predicted balance may drop. Review expenses and payment schedule."
            if last_balance < 0:
                risk = "critical"
                rec_text = "Balance is negative. Immediate budget review and cost control recommended."

            cur.execute("INSERT INTO recommendations (upload_id, risk_level, recommendation_text) VALUES (%s,%s,%s)", (upload_id, risk, rec_text))

            conn.commit()
            log_action(user["id"], f"Uploaded CSV: {filename} ({rows_added} rows)", "OK")
            flash("Upload successful! Data processed.")
        except Exception:
            conn.rollback()
            flash("CSV read/parse error. Check numbers/format.")
            log_action(user["id"], f"Upload parse error: {filename}", "FAIL")
        finally:
            cur.close(); conn.close()

        return redirect(url_for("dashboard"))

    return render_template("upload.html", user=user)

@app.route("/visualization")
def visualization():
    if not require_login():
        return redirect(url_for("login"))
    user = current_user()

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM uploads WHERE user_id=%s ORDER BY uploaded_at DESC LIMIT 1", (user["id"],))
    upload = cur.fetchone()

    periods, balances = [], []
    dist = {"Project Cost": 0, "VAT": 0, "Payments Made": 0}

    if upload:
        cur.execute("SELECT period, project_cost, vat, payments_made, balance FROM finance_records WHERE upload_id=%s ORDER BY id ASC LIMIT 12", (upload["id"],))
        rows = cur.fetchall()
        for r in rows:
            periods.append(r["period"])
            balances.append(float(r["balance"]))
            dist["Project Cost"] += float(r["project_cost"])
            dist["VAT"] += float(r["vat"])
            dist["Payments Made"] += float(r["payments_made"])

    cur.close(); conn.close()

    # --- simple insights (student-friendly) ---
    insights = []

    if len(balances) >= 2:
        start_b = balances[0]
        end_b = balances[-1]
        change = end_b - start_b
        pct_change = (change / start_b * 100) if start_b != 0 else 0

        trend = "increasing" if change > 0 else ("decreasing" if change < 0 else "stable")
        insights.append(f"Balance trend is {trend} from the first period to the last period.")

        insights.append(f"Overall change: {change:,.2f} ({pct_change:.1f}%).")

    if len(balances) >= 1:
        insights.append(f"Highest balance: {max(balances):,.2f}. Lowest balance: {min(balances):,.2f}.")

    # distribution insight
    total_dist = sum(dist.values())
    if total_dist > 0:
        biggest_key = max(dist, key=dist.get)
        biggest_pct = dist[biggest_key] / total_dist * 100
        insights.append(f"Biggest share in the pie chart is {biggest_key} ({biggest_pct:.1f}%).")
    return render_template("visualization.html", user=user, periods=periods, balances=balances,  dist=dist, insights=insights)

@app.route("/admin")
def admin():
    if not require_login():
        return redirect(url_for("login"))
    if not require_admin():
        flash("Admins only.")
        return redirect(url_for("dashboard"))

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT id, first_name, last_name, email, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()

    cur.execute("SELECT a.created_at, u.email, a.action, a.status FROM audit_logs a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.created_at DESC LIMIT 20")
    logs = cur.fetchall()

    cur.close(); conn.close()
    return render_template("admin.html", user=current_user(), users=users, logs=logs)

if __name__ == "__main__":
    app.run(debug=True)

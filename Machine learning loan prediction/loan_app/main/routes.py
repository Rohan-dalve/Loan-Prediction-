import io
import csv
from flask import Blueprint, render_template, request, flash, current_app, session, redirect, url_for, send_file
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:  # Optional dependency for PDF export.
    letter = None
    canvas = None
from loan_app.db import get_db
from loan_app.utils.decorators import login_required
from loan_app.utils.validators import validate_prediction_payload

bp = Blueprint("main", __name__, url_prefix="/app")


@bp.route("/home")
@login_required
def home():
    return render_template("main/home.html")


@bp.route("/predict", methods=["POST"])
@login_required
def predict():
    payload = {
        "gender": request.form.get("gender", ""),
        "married": request.form.get("married", ""),
        "dependents": request.form.get("dependents", ""),
        "self_employed": request.form.get("self_employed", ""),
        "income": request.form.get("income", ""),
        "credit_history": request.form.get("credit_history", ""),
        "property_area": request.form.get("property_area", ""),
    }
    errors = validate_prediction_payload(payload)
    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("main.home"))

    pred = current_app.ml_service.predict(payload)
    db = get_db()
    db.execute(
        """
        INSERT INTO loan_applications
        (user_id, gender, married, dependents, self_employed, income, credit_history, property_area, loan_status, loan_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            payload["gender"],
            payload["married"],
            payload["dependents"],
            payload["self_employed"],
            float(payload["income"]),
            int(payload["credit_history"]),
            payload["property_area"],
            pred["loan_status"],
            pred["loan_amount"],
        ),
    )
    db.commit()
    result = "Loan Approved" if pred["loan_status"] == 1 else "Loan Not Approved"
    flash(f"{result} | Predicted amount: Rs {pred['loan_amount']:.2f}", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/dashboard")
@login_required
def dashboard():
    rows = get_db().execute(
        """
        SELECT id, gender, married, dependents, self_employed, income, credit_history,
               property_area, loan_status, loan_amount, created_at
        FROM loan_applications
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()
    return render_template("main/dashboard.html", history=rows)


@bp.route("/report/<format_type>")
@login_required
def report(format_type):
    rows = get_db().execute(
        """
        SELECT gender, married, dependents, self_employed, income, credit_history,
               property_area, loan_status, loan_amount, created_at
        FROM loan_applications
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    ).fetchall()

    if format_type == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Gender", "Married", "Dependents", "Self Employed", "Income", "Credit", "Area", "Status", "Amount", "Date"])
        for row in rows:
            writer.writerow(
                [
                    row["gender"],
                    row["married"],
                    row["dependents"],
                    row["self_employed"],
                    row["income"],
                    row["credit_history"],
                    row["property_area"],
                    "Approved" if row["loan_status"] == 1 else "Rejected",
                    row["loan_amount"],
                    row["created_at"],
                ]
            )
        mem = io.BytesIO(output.getvalue().encode("utf-8"))
        return send_file(mem, as_attachment=True, download_name="loan_history.csv", mimetype="text/csv")

    if format_type == "pdf":
        if canvas is None or letter is None:
            flash("PDF export requires reportlab. Install it and try again.", "warning")
            return redirect(url_for("main.dashboard"))
        mem = io.BytesIO()
        pdf = canvas.Canvas(mem, pagesize=letter)
        pdf.setFont("Helvetica", 10)
        y = 760
        pdf.drawString(50, y, "Loan Prediction History")
        y -= 25
        for row in rows[:30]:
            line = (
                f"{row['created_at']} | {row['gender']} | {row['income']} | "
                f"{'Approved' if row['loan_status'] == 1 else 'Rejected'} | {row['loan_amount']:.2f}"
            )
            pdf.drawString(50, y, line[:110])
            y -= 18
            if y < 50:
                pdf.showPage()
                y = 760
        pdf.save()
        mem.seek(0)
        return send_file(mem, as_attachment=True, download_name="loan_history.pdf", mimetype="application/pdf")

    flash("Unsupported report format.", "warning")
    return redirect(url_for("main.dashboard"))

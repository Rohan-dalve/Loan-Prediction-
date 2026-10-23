from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from loan_app.db import get_db
from loan_app.utils.validators import validate_signup_payload

bp = Blueprint("auth", __name__)


@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html"), 401

        session.clear()
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["role"] = user["role"]
        flash("Welcome back!", "success")
        return redirect(url_for("admin.panel" if user["role"] == "admin" else "main.home"))

    return render_template("auth/login.html")


@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        errors = validate_signup_payload(name, email, password)

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("auth/signup.html"), 400

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Email already registered.", "warning")
            return render_template("auth/signup.html"), 409

        role = "admin" if email == "admin@gmail.com" else "user"
        db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, generate_password_hash(password), role),
        )
        db.commit()
        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(password) < 6:
            flash("New password must be at least 6 characters.", "danger")
            return render_template("auth/forgot.html"), 400

        db = get_db()
        result = db.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (generate_password_hash(password), email),
        )
        db.commit()

        if result.rowcount == 0:
            flash("Account not found.", "warning")
            return render_template("auth/forgot.html"), 404

        flash("Password updated successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))

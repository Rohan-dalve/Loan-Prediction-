from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from loan_app.db import get_db
from loan_app.utils.decorators import login_required, role_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
@role_required("admin")
def panel():
    q = request.args.get("q", "").strip().lower()
    page = max(1, int(request.args.get("page", 1)))
    per_page = 10
    offset = (page - 1) * per_page

    where = ""
    params = []
    if q:
        where = "WHERE lower(u.name) LIKE ? OR lower(u.email) LIKE ?"
        params.extend([f"%{q}%", f"%{q}%"])

    db = get_db()
    total_users = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    total_predictions = db.execute("SELECT COUNT(*) AS c FROM loan_applications").fetchone()["c"]
    approved = db.execute("SELECT COUNT(*) AS c FROM loan_applications WHERE loan_status = 1").fetchone()["c"]

    users = db.execute(
        f"""
        SELECT u.id, u.name, u.email, u.role, COUNT(la.id) AS predictions, MAX(la.created_at) AS last_prediction
        FROM users u
        LEFT JOIN loan_applications la ON la.user_id = u.id
        {where}
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT ? OFFSET ?
        """,
        (*params, per_page, offset),
    ).fetchall()

    total_filtered = db.execute(
        f"SELECT COUNT(*) AS c FROM users u {where}",
        tuple(params),
    ).fetchone()["c"]
    total_pages = (total_filtered + per_page - 1) // per_page

    return render_template(
        "admin/panel.html",
        users=users,
        total_users=total_users,
        total_predictions=total_predictions,
        approved=approved,
        query=q,
        page=page,
        total_pages=max(1, total_pages),
    )


@bp.route("/stats")
@login_required
@role_required("admin")
def stats():
    db = get_db()
    total_users = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    total_predictions = db.execute("SELECT COUNT(*) AS c FROM loan_applications").fetchone()["c"]
    approved = db.execute("SELECT COUNT(*) AS c FROM loan_applications WHERE loan_status = 1").fetchone()["c"]
    rejected = max(0, total_predictions - approved)
    return jsonify(
        {
            "total_users": total_users,
            "total_predictions": total_predictions,
            "approved": approved,
            "rejected": rejected,
        }
    )


@bp.route("/delete_user", methods=["POST"])
@login_required
@role_required("admin")
def delete_user():
    user_id = request.form.get("user_id")
    if not user_id:
        flash("User id is required.", "danger")
        return redirect(url_for("admin.panel"))
    get_db().execute("DELETE FROM users WHERE id = ?", (user_id,))
    get_db().commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin.panel"))

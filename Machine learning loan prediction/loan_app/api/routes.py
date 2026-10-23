from flask import Blueprint, request, jsonify, current_app
from loan_app.db import get_db
from loan_app.utils.validators import validate_prediction_payload
from loan_app.utils.decorators import login_required, role_required

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(silent=True) or {}
    errors = validate_prediction_payload(payload)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    pred = current_app.ml_service.predict(payload)
    return jsonify({"ok": True, "data": pred})


@bp.route("/users", methods=["GET"])
@login_required
@role_required("admin")
def api_users():
    users = get_db().execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    return jsonify({"ok": True, "data": [dict(u) for u in users]})


@bp.route("/health")
def health():
    return jsonify({"ok": True, "status": "healthy"})

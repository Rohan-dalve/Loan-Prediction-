from functools import wraps
from flask import session, redirect, url_for, flash, abort


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator

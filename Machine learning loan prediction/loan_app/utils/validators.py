import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup_payload(name, email, password):
    errors = []
    if len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    return errors


def validate_prediction_payload(payload):
    required = [
        "gender",
        "married",
        "dependents",
        "self_employed",
        "income",
        "credit_history",
        "property_area",
    ]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return [f"Missing fields: {', '.join(missing)}"]

    errors = []
    if payload["gender"] not in {"Male", "Female"}:
        errors.append("Gender must be Male or Female.")
    if payload["married"] not in {"Yes", "No"}:
        errors.append("Married must be Yes or No.")
    if payload["self_employed"] not in {"Yes", "No"}:
        errors.append("Self employed must be Yes or No.")
    if payload["property_area"] not in {"Urban", "Semiurban", "Rural"}:
        errors.append("Invalid property area.")
    if payload["dependents"] not in {"0", "1", "2", "3+"}:
        errors.append("Dependents must be 0, 1, 2, or 3+.")

    try:
        if float(payload["income"]) < 0:
            errors.append("Income cannot be negative.")
    except (TypeError, ValueError):
        errors.append("Income must be numeric.")

    try:
        credit = int(payload["credit_history"])
        if credit not in {0, 1}:
            errors.append("Credit history must be 0 or 1.")
    except (TypeError, ValueError):
        errors.append("Credit history must be integer.")

    return errors

from flask import Flask, render_template
from loan_app.config import Config
from loan_app.db import init_db, close_db
from loan_app.ml.service import MLService
from loan_app.auth.routes import bp as auth_bp
from loan_app.main.routes import bp as main_bp
from loan_app.admin.routes import bp as admin_bp
from loan_app.api.routes import bp as api_bp


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    app.ml_service = MLService(
        model_bundle_path=app.config["MODEL_BUNDLE_PATH"],
        training_data_path=app.config["TRAINING_DATA_PATH"],
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("errors/500.html"), 500

    return app

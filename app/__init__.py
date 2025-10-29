# app/__init__.py
from typing import Optional
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_object: Optional[str] = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    config = config_object or "app.config.Config"
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import models so user_loader can work
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Tell Flask-Login how to get a user by ID"""
        return User.query.get(int(user_id))

    # Register blueprints
    from .auth import bp as auth_bp
    from .complaints import bp as complaints_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaints_bp)

    # Redirect root URL to login or complaints page
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            # Customers go to complaint form page
            if current_user.role == "customer":
                return redirect(url_for("complaints.submit"))
            # Admin goes to dashboard
            return redirect(url_for("complaints.dashboard"))
        return redirect(url_for("auth.login"))

    return app

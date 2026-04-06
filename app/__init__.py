from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS

from app.config import Config
from app.models import db, User

login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.user import user_bp
    from app.blueprints.reviewer import reviewer_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.mobile_api import mobile_api

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reviewer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(mobile_api)

    # Exempt API blueprints from CSRF (uses JSON, not form submissions)
    csrf.exempt(api_bp)
    csrf.exempt(mobile_api)

    # Enable CORS for mobile API
    CORS(app, resources={r"/api/mobile/*": {"origins": "*"}})

    # Create DB tables and seed admin
    with app.app_context():
        db.create_all()
        _seed_admin()

    # Start scheduler
    from app.services.scheduler import init_scheduler
    init_scheduler(app, mail)

    return app


def _seed_admin():
    """Create default admin account if it doesn't exist."""
    admin = User.query.filter_by(email='admin@health.app').first()
    if not admin:
        admin = User(email='admin@health.app', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

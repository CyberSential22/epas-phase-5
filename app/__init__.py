import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from app.config import config
from app.utils.logger import setup_logger

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_name: str = None) -> Flask:
    """
    Application Factory Pattern.
    Initializes Flask app, extensions, and logs.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Setup Logging
    setup_logger(app)

    with app.app_context():
        # Setup Login Manager Loader
        from app.models.user import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        # Register Blueprints
        from app.blueprints.main import main_bp
        from app.blueprints.events import events_bp
        from app.blueprints.auth import auth_bp
        from app.blueprints.faculty import faculty_bp
        from app.blueprints.dept_head import dept_head_bp
        from app.blueprints.admin import admin_bp
        from app.blueprints.approvals import approvals_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(events_bp, url_prefix='/events')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(faculty_bp, url_prefix='/faculty')
        app.register_blueprint(dept_head_bp, url_prefix='/depthead')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(approvals_bp, url_prefix='/approvals')

    # Global Error Handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)

    # Custom Jinja2 Filters
    @app.template_filter('format_inr')
    def format_inr(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    return app

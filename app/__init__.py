from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db
import json

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Add custom template filter
    @app.template_filter('json_loads')
    def json_loads_filter(value):
        return json.loads(value)

    @app.template_filter('parse_json')
    def parse_json(value):
        try:
            return json.loads(value)
        except:
            return {}

    # Configure LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes.auth import auth
    from .routes.main import main
    
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # Add CLI commands
    from .cli import create_admin
    app.cli.add_command(create_admin)

    return app
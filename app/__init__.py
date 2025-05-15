from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import json
from base64 import b64encode

# Create extensions instances
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object('config.Config')
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables within app context
    with app.app_context():
        db.create_all()

    # Configure LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader 
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Add template filters
    @app.template_filter('json_loads')
    def json_loads_filter(value):
        return json.loads(value)

    @app.template_filter('parse_json')
    def parse_json(value):
        try:
            return json.loads(value)
        except:
            return {}

    @app.template_filter('b64encode')
    def b64encode_filter(data):
        if data is None:
            return ''
        import base64
        return base64.b64encode(data).decode('utf-8')

    # Register blueprints
    from .routes.auth import auth
    from .routes.main import main
    
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # Add CLI commands
    from .cli import create_admin, delete_user
    app.cli.add_command(create_admin)
    app.cli.add_command(delete_user)

    return app
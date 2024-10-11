from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    """Configuracion"""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Directorio donde se guardarán las imágenes
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Tamaño máximo del archivo (16 MB en este caso)
    
    """Inicializacion"""
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    """Blueprints"""
    from app.routes import main
    app.register_blueprint(main)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('public/403.html'), 403
    
    """Get user in each request for more info"""
    from app.models import Usuario
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "danger"
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app
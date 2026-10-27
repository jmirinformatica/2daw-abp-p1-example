from flask import Flask
from flask_login import LoginManager
from flask_principal import Principal

login_manager = LoginManager()
principal_manager =  Principal()

def configure_plugins(app):
    # Inicialitza el login manager
    login_manager.init_app(app)

    # Initialitza flask_principal per a gestionar els rols
    principal_manager.init_app(app)

    from .models import db
    db.init_app(app)
    
    app.logger.info("Database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    app.logger.info("Configuració de la base de dades aplicada")

def create_app():
    app = Flask(__name__)

    # Llegeixo la configuració del config.py de l'arrel
    app.config.from_object('config.Config')

    # Configuració dels plugins
    configure_plugins(app)
    
    with app.app_context():
        from . import routes_main, routes_auth, routes_admin

        # Registra els blueprints
        app.register_blueprint(routes_main.main_bp)
        app.register_blueprint(routes_auth.auth_bp)
        app.register_blueprint(routes_admin.admin_bp)

    app.logger.info("Aplicació iniciada")

    return app
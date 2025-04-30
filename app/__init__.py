import os 
from flask import Flask
from app.database import db 
from app.routes.boleto_route import boleto_bp


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all() 

    app.register_blueprint(boleto_bp)

    return app
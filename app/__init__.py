import os 
from flask import Flask
from flask_cors import CORS
from app.database import db 
from app.routes.boleto_route import boleto_bp
from app.routes.auth_route import auth_bp


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:8100", "https://detecta-bb.vercel.app"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all() 

    app.register_blueprint(boleto_bp)
    app.register_blueprint(auth_bp)

    return app
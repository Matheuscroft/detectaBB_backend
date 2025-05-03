from flask import Blueprint, request, jsonify
from app.models.user_model import User
from app.database import db
import jwt
import datetime
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email já cadastrado"}), 400

    user = User(nome=data["nome"], email=data["email"])
    user.set_password(data["senha"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário registrado com sucesso!"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["senha"]):
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, os.getenv("SECRET_KEY"), algorithm="HS256")

        return jsonify({"token": token}), 200

    return jsonify({"error": "Credenciais inválidas"}), 401

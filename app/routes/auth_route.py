from flask import Blueprint, request, jsonify
from app.models.user_model import User
from app.database import db
import jwt
import datetime
import os
from functools import wraps

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

        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email
            }
        }), 200

    return jsonify({"error": "Credenciais inválidas"}), 401

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token ausente!'}), 401

        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado'}), 404
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_user_data(current_user):
    return jsonify({
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email
    }), 200

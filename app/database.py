import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
print("🧪 DATABASE_URL carregada do .env:", os.getenv("DATABASE_URL"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

try:
    with app.app_context():
        db.engine.connect()
    print("✅ Conexão bem-sucedida com o banco de dados!")
except Exception as e:
    print("❌ Falha na conexão com o banco de dados:", e)

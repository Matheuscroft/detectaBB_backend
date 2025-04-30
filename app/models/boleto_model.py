from datetime import datetime
from ..database import db

class BoletoVerificado(db.Model):
    __tablename__ = "boleto_verificado"
    id = db.Column(db.Integer, primary_key=True, index=True)
    banco = db.Column(db.Integer)
    codigo_banco = db.Column(db.Integer)
    agencia = db.Column(db.Integer)
    valor = db.Column(db.DECIMAL(10,2))
    linha_cod_banco = db.Column(db.Integer)
    linha_moeda = db.Column(db.Integer)
    linha_valor = db.Column(db.BIGINT)
    resultado = db.Column(db.String(10))
    data_criacao = db.Column(db.TIMESTAMP, default=datetime.utcnow)

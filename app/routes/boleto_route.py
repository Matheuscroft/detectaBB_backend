from flask import Blueprint, request, jsonify
from app.database import db
from app.models.boleto_model import BoletoVerificado
from datetime import datetime
import pytz
from app.services.ocr_service import perform_ocr, parse_ocr_text, preparar_para_predicao
from app.services.predict_service import fazer_predicao

boleto_bp = Blueprint("boleto", __name__, url_prefix="/boleto")

@boleto_bp.route("/", methods=["POST"])
def criar_boleto():
    try:
        data = request.get_json()

        boleto = BoletoVerificado(
            banco=data.get("banco"),
            codigo_banco=data.get("codigo_banco"),
            agencia=data.get("agencia"),
            valor=data.get("valor"),
            linha_cod_banco=data.get("linha_cod_banco"),
            linha_moeda=data.get("linha_moeda"),
            linha_valor=data.get("linha_valor"),
            resultado=data.get("resultado")
        )

        recife_tz = pytz.timezone('America/Recife')
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_time = utc_now.astimezone(recife_tz)

        boleto.data_criacao = local_time 

        db.session.add(boleto)
        db.session.commit()

        return jsonify({
            "id": boleto.id,
            "banco": boleto.banco,
            "codigo_banco": boleto.codigo_banco,
            "agencia": boleto.agencia,
            "valor": str(boleto.valor),
            "linha_cod_banco": boleto.linha_cod_banco,
            "linha_moeda": boleto.linha_moeda,
            "linha_valor": boleto.linha_valor,
            "resultado": boleto.resultado,
            "data_criacao": boleto.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@boleto_bp.route("/", methods=["GET"])
def get_all_boletos():
    try:
        boletos = BoletoVerificado.query.all()
        
        boletos_list = []
        for boleto in boletos:
            boletos_list.append({
                "id": boleto.id,
                "banco": boleto.banco,
                "codigo_banco": boleto.codigo_banco,
                "agencia": boleto.agencia,
                "valor": str(boleto.valor),
                "linha_cod_banco": boleto.linha_cod_banco,
                "linha_moeda": boleto.linha_moeda,
                "linha_valor": boleto.linha_valor,
                "resultado": boleto.resultado,
                "data_criacao": boleto.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify(boletos_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@boleto_bp.route("/<int:id>", methods=["GET"])
def get_boleto(id):
    try:
        boleto = BoletoVerificado.query.get(id)
        if boleto:
            return jsonify({
                "id": boleto.id,
                "banco": boleto.banco,
                "codigo_banco": boleto.codigo_banco,
                "agencia": boleto.agencia,
                "valor": str(boleto.valor),
                "linha_cod_banco": boleto.linha_cod_banco,
                "linha_moeda": boleto.linha_moeda,
                "linha_valor": boleto.linha_valor,
                "resultado": boleto.resultado,
                "data_criacao": boleto.data_criacao.strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        else:
            return jsonify({"error": "Boleto não encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@boleto_bp.route("/<int:id>", methods=["DELETE"])
def delete_boleto(id):
    try:
        boleto = BoletoVerificado.query.get(id)
        if boleto:
            db.session.delete(boleto)
            db.session.commit()
            return jsonify({"message": "Boleto excluído com sucesso!"}), 200
        else:
            return jsonify({"error": "Boleto não encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@boleto_bp.route("/upload", methods=["POST"])
def upload_boleto():
    try:
        image = request.files.get('image')
        password = request.form.get('password')
        
        if image:
            extracted_data = perform_ocr(image, password) 
            parsed_data = parse_ocr_text(extracted_data.get('texto_extraido'))

            dados_para_predicao = preparar_para_predicao(parsed_data)

            resultado_predicao = fazer_predicao(dados_para_predicao)

            return jsonify({
                "message": "OCR processado com sucesso!",
                "dados_extraidos": parsed_data,
                "ocr_texto": extracted_data.get('texto_extraido'),
                "resultado_modelo": resultado_predicao
            }), 200

        else:
            return jsonify({"error": "Imagem não recebida."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

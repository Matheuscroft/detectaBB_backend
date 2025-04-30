import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import pikepdf
import io
import re

bancos = {
    "Santander": "033",
    "Bradesco": "237",
    "Itaú": "341",
    "Banco do Brasil": "001",
    "Caixa Econômica Federal": "104",
}

mapeamento_bancos = {
    "Banco do Brasil": 0,
    "Itaú": 1,
    "Bradesco": 2,
    "Santander": 3,
    "Caixa Econômica": 4
}

def perform_ocr(file, password=None):
    if file.filename.lower().endswith('.pdf'):
        file_bytes = file.read()

        if password:
            try:
                pdf = pikepdf.open(io.BytesIO(file_bytes), password=password)
                unlocked_bytes = io.BytesIO()
                pdf.save(unlocked_bytes)
                pdf.close()
                file_bytes = unlocked_bytes.getvalue()
            except pikepdf._qpdf.PasswordError:
                raise Exception("Senha incorreta para desbloquear o PDF.")

        poppler_path = r'C:\poppler-24.08.0\Library\bin'

        images = convert_from_bytes(file_bytes, poppler_path=poppler_path)

        if images:
            img = images[0]  
            ocr_result = pytesseract.image_to_string(img, lang='por')
        else:
            raise Exception("Não foi possível converter o PDF em imagem.")
    else:
        img = Image.open(file)
        ocr_result = pytesseract.image_to_string(img, lang='por')

    return {
        "texto_extraido": ocr_result
    }

def parse_ocr_text(texto_extraido: str):
    """Processa o texto extraído e separa os dados relevantes."""

    banco = None
    texto_minusculo = texto_extraido.lower()
    for nome_banco in bancos:
        if nome_banco.lower() in texto_minusculo:
            banco = nome_banco
            break

    codigo_banco = None
    linhas = texto_extraido.splitlines()
    for linha in linhas:
        if banco and banco.split()[0] in linha:
            codigo_banco_match = re.search(r'(\d{3})-\d', linha)
            if codigo_banco_match:
                codigo_banco = codigo_banco_match.group(1)
                break
    if not codigo_banco:
        codigo_banco_match = re.search(r'(\d{3})-\d', texto_extraido)
        if codigo_banco_match:
            codigo_banco = codigo_banco_match.group(1)

    linha_digitavel_match = re.search(r'(\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14})', texto_extraido)
    if not linha_digitavel_match:
        linha_digitavel_match = re.search(r'(\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d{1}\s\d{14})', texto_extraido)
    linha_digitavel = linha_digitavel_match.group(0).replace(" ", "") if linha_digitavel_match else None

    valor_doc_match = re.search(r'Valor do Documento:.*?R\$\s?([\d,.]+)', texto_extraido, re.DOTALL)
    valor = valor_doc_match.group(1).replace('.', '').replace(',', '.') if valor_doc_match else None

    agencia_match = re.search(r'Ag[êe]ncia\/C[óo]digo Benefici[áa]rio:\s*(\d{4})', texto_extraido)
    if not agencia_match:
        agencia_match = re.search(r'(\d{4})\s*/\s*\d+', texto_extraido)

    agencia = agencia_match.group(1) if agencia_match else None

    return {
        "banco": banco,
        "codigo_banco": codigo_banco,
        "linha_digitavel": linha_digitavel,
        "valor": valor,
        "agencia": agencia
    }

def preparar_para_predicao(parsed_data: dict):
    linha = parsed_data.get('linha_digitavel', '')
    
    if linha:
        linha = linha.replace(" ", "")
        linha_codBanco = int(linha[0:3]) if len(linha) >= 3 else None
        linha_moeda = int(linha[3]) if len(linha) >= 4 else None
        linha_valor = int(linha[-10:]) if len(linha) >= 10 else None
    else:
        linha_codBanco = linha_moeda = linha_valor = None

    banco_nome = parsed_data.get('banco')
    banco_mapeado = mapeamento_bancos.get(banco_nome)

    return {
        "banco": banco_mapeado,
        "codigoBanco": int(parsed_data.get('codigo_banco')) if parsed_data.get('codigo_banco') else None,
        "agencia": int(parsed_data.get('agencia')) if parsed_data.get('agencia') else None,
        "valor": float(parsed_data.get('valor')) if parsed_data.get('valor') else None,
        "linha_codBanco": linha_codBanco,
        "linha_moeda": linha_moeda,
        "linha_valor": linha_valor
    }

import os, pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import fitz
import pikepdf
import io
import re
import unicodedata
tess_path = os.environ.get("TESSERACT_CMD")

if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").lower()

def corrigir_ocr(texto: str) -> str:
    return (
        texto.upper()
        .replace('O', '0')
        .replace('I', '1')
        .replace('L', '1')
        .replace('|', '1')
        .replace('>', '2')
    )

def identificar_banco_automatico(texto_ocr: str, bancos: dict) -> str | None:
    texto_normalizado = normalizar(texto_ocr)

    for nome_banco in bancos:
        nome_normalizado = normalizar(nome_banco)
        if nome_normalizado in texto_normalizado:
            print(f"🎯 Match direto com banco: {nome_banco}")
            return nome_banco

    melhor_banco = None
    maior_score = 0

    for nome_banco in bancos:
        nome_normalizado = normalizar(nome_banco)
        palavras_banco = nome_normalizado.split()
        score = sum(1 for palavra in palavras_banco if palavra in texto_normalizado)

        if score > maior_score or (score == maior_score and melhor_banco and len(nome_banco) > len(melhor_banco)):
            melhor_banco = nome_banco
            maior_score = score

    return melhor_banco if maior_score > 0 else None

def extrair_agencia(texto_extraido: str) -> str | None:
    linhas = texto_extraido.splitlines()

    for i, linha in enumerate(linhas):
        if "Agência" in linha:
            for j in range(i + 1, min(i + 3, len(linhas))):
                trecho = linhas[j].strip()
                match1 = re.search(r'(\d{4})-\d\s*/\s*\d+', trecho)
                if match1:
                    return match1.group(1)

                match2 = re.search(r'(\d{4})\s*/\s*\d+', trecho)
                if match2:
                    return match2.group(1)

    match_fallback = re.search(r'Ag[êe]ncia.*?(\d{4})\s*/\s*\d+', texto_extraido, flags=re.IGNORECASE)
    if match_fallback:
        return match_fallback.group(1)

    return None

def buscar_codigo_banco(texto: str, banco: str, linha_digitavel: str = None) -> str:
    linhas = texto.splitlines()

    linha_digitavel_limpa = linha_digitavel.replace(" ", "").replace(".", "") if linha_digitavel else None

    padrao_codigo = r'\b(\d{3,4})-\d\b'

    if linha_digitavel_limpa:
        for i, linha in enumerate(linhas):
            if linha_digitavel_limpa[:10].replace(".", "")[:5] in linha.replace(" ", ""):
                for offset in range(-1, 2):
                    idx = i + offset
                    if 0 <= idx < len(linhas):
                        linha_verificada = linhas[idx]
                        match = re.search(padrao_codigo, linha_verificada)
                        if match:
                            codigo_bruto = match.group(1)
                            codigo_banco = codigo_bruto[-3:]
                            return codigo_banco

    for i, linha in enumerate(linhas[:5]):
        if banco and banco.split()[0].lower() in linha.lower():
            match = re.search(padrao_codigo, linha)
            if match:
                codigo_bruto = match.group(1)
                codigo_banco = codigo_bruto[-3:]
                return codigo_banco

    return None

def parse_valor(valor_str: str) -> float | None:
    valor_str = valor_str.strip()

    if ',' in valor_str:
        try:
            return float(valor_str.replace('.', '').replace(',', '.'))
        except:
            return None

    if '.' in valor_str and valor_str.count('.') == 1:
        try:
            return float(valor_str)
        except:
            return None

    try:
        return float(valor_str)
    except:
        return None

def extrair_valor(texto: str) -> float | None:
    linhas = texto.splitlines()
    padrao_valor_com_sifrao = re.compile(r'(?:R\$|RS)[\s:]?([\d,.]+)', re.IGNORECASE)
    padrao_valor_decimal = re.compile(r'\b([\d]{1,3}(?:[.,]\d{3})*[.,]\d{2})\b')

    candidatos = {} 
    valores_encontrados = []  

    for i, linha in enumerate(linhas):
        linha_normalizada = linha.replace('6S', 'R$').replace('R S', 'R$').replace('RS', 'R$')

        palavras_chave = {
            'valor cobrado': ['valor cobrado'],
            'valor a pagar': ['valor a pagar', 'valor total'],
            'valor documento': ['valor do documento', 'valor documento']
        }

        for chave, palavras in palavras_chave.items():
            if any(palavra in linha.lower() for palavra in palavras):
                for j in range(i, min(i + 3, len(linhas))):
                    linha_busca = linhas[j].replace('6S', 'R$').replace('R S', 'R$').replace('RS', 'R$')
                    match = padrao_valor_com_sifrao.search(linha_busca) or padrao_valor_decimal.search(linha_busca)
                    if match:
                        valor_raw = match.group(1)
                        valor_float = parse_valor(valor_raw)
                        if valor_float is not None:
                            candidatos[chave] = valor_float
                            valores_encontrados.append(valor_float)
                            break

        match_livre = padrao_valor_com_sifrao.search(linha_normalizada) or padrao_valor_decimal.search(linha_normalizada)
        if match_livre:
            valor_raw = match_livre.group(1)
            valor_float = parse_valor(valor_raw)
            if valor_float is not None:
                valores_encontrados.append(valor_float)

    def valor_valido(v):
        return isinstance(v, (int, float)) and v > 0

    if valor_valido(candidatos.get('valor cobrado')):
        return round(candidatos['valor cobrado'], 2)
    elif valor_valido(candidatos.get('valor a pagar')):
        return round(candidatos['valor a pagar'], 2)
    elif valor_valido(candidatos.get('valor documento')):
        return round(candidatos['valor documento'], 2)
    elif valores_encontrados:
        return round(max(valores_encontrados), 2)
    else:
        return None

def extrair_linha_digitavel(texto_corrigido: str) -> str | None:
    padrao_linha_digitavel = re.compile(r'(\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14,15})')
    match = padrao_linha_digitavel.search(texto_corrigido)
    if not match:
        return None
    linha = match.group(0)
    return corrigir_linha_digitavel(linha)

def corrigir_linha_digitavel(linha: str) -> str:
    """Corrige possíveis erros na linha digitável, como 15 dígitos no campo final."""
    so_digitos = re.sub(r'\D', '', linha)

    if len(so_digitos) == 48:
        final = so_digitos[-15:]
        if final.startswith('0'):
            final_corrigido = final[1:]
            so_digitos = so_digitos[:-15] + final_corrigido
    elif len(so_digitos) != 47:
        print("⚠️ Atenção: linha digitável fora do padrão esperado.")

    return (
        f"{so_digitos[0:5]}.{so_digitos[5:10]} "
        f"{so_digitos[10:15]}.{so_digitos[15:21]} "
        f"{so_digitos[21:26]}.{so_digitos[26:32]} "
        f"{so_digitos[32]} "
        f"{so_digitos[33:]}"
    )

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

def pdf_para_imagem_pymupdf(pdf_bytes: bytes) -> Image.Image:
    """
    Converte o primeiro página do PDF em objeto PIL.Image usando PyMuPDF.
    """
    documento = fitz.open(stream=pdf_bytes, filetype="pdf")
    pagina = documento.load_page(0)
    pix = pagina.get_pixmap(alpha=False)
    img_bytes = pix.tobytes("png")
    documento.close()
    return Image.open(io.BytesIO(img_bytes))

def perform_ocr(file, password=None):
    """
    Função principal de OCR, agora usando PyMuPDF em vez de Poppler.
    Mantém o mesmo nome e estrutura, mas faz a conversão de PDF → imagem
    via PyMuPDF.
    """
    file_bytes = file.read()

    if password:
        try:
            pdf = pikepdf.open(io.BytesIO(file_bytes), password=password)
            unlocked = io.BytesIO()
            pdf.save(unlocked)
            pdf.close()
            file_bytes = unlocked.getvalue()
        except pikepdf._qpdf.PasswordError:
            raise Exception("Senha incorreta para desbloquear o PDF.")

   # if file.filename.lower().endswith('.pdf'):
       # img = pdf_para_imagem_pymupdf(file_bytes)
      #  ocr_result = pytesseract.image_to_string(img, lang='por')

    if file.filename.lower().endswith('.pdf'):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap(alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        doc.close()
    else:
        img = Image.open(io.BytesIO(file_bytes))
        ocr_result = pytesseract.image_to_string(img, lang='por')

    return {
        "texto_extraido": ocr_result
    }

def parse_ocr_text(texto_extraido: str):
    """Processa o texto extraído e separa os dados relevantes."""

    banco = identificar_banco_automatico(texto_extraido, bancos)

    texto_corrigido = corrigir_ocr(texto_extraido)

    linha_digitavel = extrair_linha_digitavel(texto_corrigido)

    codigo_banco = buscar_codigo_banco(texto_extraido, banco, linha_digitavel)

    if not codigo_banco:
        codigo_banco = buscar_codigo_banco(texto_corrigido, banco, linha_digitavel)

    valor = extrair_valor(texto_extraido)

    agencia = extrair_agencia(texto_extraido)

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
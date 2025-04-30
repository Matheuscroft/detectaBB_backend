import pickle
import pandas as pd

model = pickle.load(open('modelo_boleto.pkl', 'rb'))

def fazer_predicao(boleto_dict):
    dado_teste = pd.DataFrame([{
        'banco': boleto_dict.get('banco'),
        'codigoBanco': boleto_dict.get('codigoBanco'),
        'agencia': boleto_dict.get('agencia'),
        'valor': boleto_dict.get('valor'),
        'linha_codBanco': boleto_dict.get('linha_codBanco'),
        'linha_moeda': boleto_dict.get('linha_moeda'),
        'linha_valor': boleto_dict.get('linha_valor')
    }])
    pred = model.predict(dado_teste)
    return 'Verdadeiro' if pred[0] == 1 else 'Falso'
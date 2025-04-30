from pydantic import BaseModel

class BoletoEntrada(BaseModel):
    banco: float
    codigoBanco: int
    agencia: int
    valor: float
    linha_codBanco: int
    linha_moeda: int
    linha_valor: int

class BoletoSaida(BoletoEntrada):
    id: int
    resultado: str

    class Config:
        orm_mode = True

from pydantic import BaseModel

class DadosBasicos(BaseModel):
    data_da_fatura: str
    referencia: str
    montante: str
    texto: str
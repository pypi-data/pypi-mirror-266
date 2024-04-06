from pydantic import BaseModel

class ChaveAcesso(BaseModel):
    numero_aleatorio: str
    dig_verif: str
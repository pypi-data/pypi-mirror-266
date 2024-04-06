from pydantic import BaseModel

class Item(BaseModel):
    centro: str
    centro_custo: str
    cod_imposto: str
    valor_bruto: str
from pydantic import BaseModel

class NfeSefaz(BaseModel):
    numero_log: str
    data_procmto: str
    hora_procmto: str
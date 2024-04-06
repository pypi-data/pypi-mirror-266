from pydantic import BaseModel

from typing import List

from .sintese_itens import SinteseItens
from .anexo import Anexo
from .jira_info import JiraInfo

class NotaPedido(BaseModel):
    tipo: str
    org_compras: str
    grp_compradores: str
    empresa: str
    cod_fornecedor: str
    sintese_itens: List[SinteseItens]
    anexo: Anexo
    jira_info: JiraInfo
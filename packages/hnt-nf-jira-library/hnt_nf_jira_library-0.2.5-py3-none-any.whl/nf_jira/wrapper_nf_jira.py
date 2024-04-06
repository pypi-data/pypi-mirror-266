import json
import requests
import os
from os import getcwd, path
from datetime import datetime

from pydantic import ValidationError
from .entities.nota_pedido import NotaPedido
from .entities.miro import Miro
from .entities.constants import *

from nf_consumo.consumo_service import ConsumoService


class wrapper_jira:

    def __init__(self, debug=False):
        self._auth = (os.getenv("USER"), os.getenv("ACCESS_TOKEN"))
        self._n8n_auth = (os.getenv("N8N_USERNAME"), os.getenv("N8N_PASSWORD"))
        self._api_issue_url = os.getenv("ISSUE_URL")
        self._api_form_url = os.getenv("FORM_URL")
        self._cloud_id = os.getenv("CLOUD_ID")
        self._api_domain_url = os.getenv("DOMAIN_URL")
        self._test_mode = debug
        self._form_template_automacao = FORM_TEMPLATE_AUTOMACAO
        self._form_template_complemento = FORM_TEMPLATE_COMPLEMENTO
        self._set_request()

    def _set_request(self):
        self._api_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self._api_attachment_headers = {
            "Accept": "*/*",
        }
        self._api_atlassian_headers = {
            "Accept": "application/json",
            "X-ExperimentalApi": "opt-in",
        }

    def _remove_null_fields(self, fields):
        fields_data_without_nulls = {}

        for key, value in fields.items():
            if value is not None:
                fields_data_without_nulls[key] = value

        return fields_data_without_nulls

    def _rename_fields(self, fields):
        fields = self._fields
        new_fields_data = {}

        for key, value in self._jira_fields.items():
            if value in fields:
                if "text" in fields[value]:
                    new_value = fields[value].get("text")
                elif "date" in fields[value]:
                    new_value = fields[value].get("date")
                elif "value" in fields[value]:
                    new_value = fields[value].get("value")
                else:
                    new_value = fields[value]

                new_fields_data[key] = new_value

        self._fields = new_fields_data

    def _issue_factory(self, issue: dict):

        sintese_itens = []
        validTotalPercents = 0.0

        if not issue["allocation_data"]:

            item = {
                "centro": issue["domain_data"]["centro"]["centro"],
                "centro_custo": f"{issue['domain_data']['centro']['centro']}210",
                "cod_imposto": "C6",
                "valor_bruto": str(issue["json_data"][VALOR_TOTAL_DA_FATURA]),
            }

            sintese_item = {
                "categoria_cc": "K",
                "quantidade": 1,
                "cod_material": issue["domain_data"]["fornecedor"]["codigo_material"],
                "item": item,
            }

            sintese_itens.append(sintese_item)

        else:

            for centro_issue in issue["allocation_data"]["centro_custos"]:

                validTotalPercents += float(centro_issue["porcentagem"])

                item = {
                    "centro": centro_issue["nome"].split("210")[0],
                    "centro_custo": centro_issue["nome"],
                    "cod_imposto": "C6",
                    "valor_bruto": "{:.2f}".format(
                        issue["json_data"][VALOR_TOTAL_DA_FATURA]
                        * float(centro_issue["porcentagem"])
                        / 100,
                        2,
                    ),
                }

                sintese_item = {
                    "categoria_cc": "K",
                    "quantidade": 1,
                    "cod_material": issue["domain_data"]["fornecedor"][
                        "codigo_material"
                    ],
                    "item": item,
                }

                sintese_itens.append(sintese_item)

            if validTotalPercents != 100.0:
                raise Exception(f"Invalid total percentage: {validTotalPercents}%")

        anexo = {
            "path": issue["pdf_data"]["path_dir"],
            "filename": issue["pdf_data"]["filename"],
        }

        nota_pedido = {
            "tipo": "ZCOR",
            "org_compras": issue["domain_data"]["centro"]["org_compras"],
            "grp_compradores": "S01",
            "empresa": "HFNT",
            "cod_fornecedor": issue["domain_data"]["fornecedor"]["codigo_sap"],
            "sintese_itens": sintese_itens,
            "anexo": anexo,
            "jira_info": issue["jira_info"],
        }

        return nota_pedido

    def _miro_factory(self, issue: dict):

        data_ref = issue[DATA_DE_REFERÊNCIA](
            datetime.strptime(issue[DATA_DE_REFERÊNCIA], "%m/%Y")
            .strftime("%b/%y")
            .upper()
        )

        if issue[COMPLEMENTO_DE_ÁGUA] is not None:
            leitura_anterior = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_ÁGUA]["DataLeituraAnterior"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                .strftime("%b/%y")
                .upper()
            )
            leitura_atual = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_ÁGUA]["DataLeituraAtual"], "%Y-%m-%dT%H:%M:%S"
                )
                .strftime("%b/%y")
                .upper()
            )
        elif issue[COMPLEMENTO_DE_ENERGIA] is not None:
            leitura_anterior = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_ENERGIA]["DataLeituraAnterior"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                .strftime("%b/%y")
                .upper()
            )
            leitura_atual = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_ENERGIA]["DataLeituraAtual"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                .strftime("%b/%y")
                .upper()
            )
        elif issue[COMPLEMENTO_DE_GÁS] is not None:
            leitura_anterior = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_GÁS]["DataLeituraAnterior"],
                    "%Y-%m-%dT%H:%M:%S",
                )
                .strftime("%b/%y")
                .upper()
            )
            leitura_atual = (
                datetime.strptime(
                    issue[COMPLEMENTO_DE_GÁS]["DataLeituraAtual"], "%Y-%m-%dT%H:%M:%S"
                )
                .strftime("%b/%y")
                .upper()
            )

        texto = f"REF: {data_ref} PERIODO: {leitura_anterior} A {leitura_atual}"

        dados_basicos = {
            "data_da_fatura": datetime.strptime(
                issue[DATA_DE_EMISSÃO], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%d%m%Y"),
            "referencia": f"{issue['ChaveAcessoNotaFiscal'][25:34]}-{issue['ChaveAcessoNotaFiscal'][22:25]}",
            "montante": str(issue[VALOR_TOTAL_DA_FATURA]),
            "texto": texto,
        }

        referencia_pedido = {"numero_pedido": issue["cod_sap"]}

        detalhe = {"ctg_nf": issue["domain_data"]["fornecedor"]["categoria_nf"]}

        sintese = {"CFOP": issue["domain_data"]["fornecedor"]["cfop"]}

        chave_acesso = {
            "numero_aleatorio": f"{issue['ChaveAcessoNotaFiscal'][35:43]}",
            "dig_verif": f"{issue['ChaveAcessoNotaFiscal'][43:]}",
        }

        nfe_sefaz = {
            "numero_log": issue["numero_log"],
            "data_procmto": issue["data_procmto"],
            "hora_procmto": issue["hora_procmto"],
        }

        dados_nfe = {"chave_acesso_sefaz": chave_acesso, "nfe_sefaz": nfe_sefaz}

        miro_model = {
            "dados_basicos": dados_basicos,
            "referencia_pedido": referencia_pedido,
            "detalhe": detalhe,
            "sintese": sintese,
            "dados_nfe": dados_nfe,
        }

        return miro_model

    def get_nf_issue_context(self, issue_id: str):
        try:

            issue_json = self._get_nf_jira(issue_id)

            attachment = issue_json["attachment"]
            jira_info = issue_json["jira_info"]

            ##### GET DOMAIN #####
            ## FORNECEDOR
            cnpj_fornecedor = attachment.get(CNPJ_DO_FORNECEDOR)
            fornecedor = self._get_nf_domain("fornecedor", cnpj_fornecedor)

            ## CENTRO
            cnpj_centro = attachment.get(CNPJ_DO_CLIENTE)
            centro = self._get_nf_domain("centro", cnpj_centro)

            domain = {"fornecedor": fornecedor, "centro": centro}

            ##### GET PDF #####
            pdf_data = self._download_pdf(attachment[ARQUIVOS_DA_FATURA][0])

            ##### GET ALLOCATION #####
            allocation = self._get_allocation(
                attachment[CNPJ_DO_FORNECEDOR],
                attachment[CNPJ_DO_CLIENTE],
                attachment[NÚMERO_DO_CONTRATO],
            )

            ##### FORMAT JSON #####
            issue = {
                "issue_data": issue_json["issue_data"],
                "json_data": attachment,
                "domain_data": domain,
                "allocation_data": allocation,
                "pdf_data": pdf_data,
                "jira_info": jira_info,
            }

            ##### PARSE JSON #####
            issue_model = self._issue_factory(issue)

            ##### CREATE MODEL #####
            nota_pedido = NotaPedido(**issue_model)

            #### SAVE JSON ####
            if self._test_mode:
                with open("issue_context_model.json", "w") as json_file:
                    json.dump(nota_pedido.model_dump(), json_file, indent=4)

            return NotaPedido(**issue_model).model_dump()

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

    def get_nf_miro_context(self, issue_id: str, cod_sap: str):
        try:

            issue_data = self._get_nf_jira(issue_id)

            clean_fields = self._remove_null_fields(
                issue_data["issue_data"].get("fields")
            )
            issue_data["issue_data"]["fields"] = clean_fields

            attachment = issue_data["attachment"]
            attachment["cod_sap"] = cod_sap

            ##### GET DOMAIN #####
            ## FORNECEDOR
            cnpj_fornecedor = attachment.get(CNPJ_DO_FORNECEDOR)
            fornecedor = self._get_nf_domain("fornecedor", cnpj_fornecedor)

            ## CENTRO
            cnpj_centro = attachment.get(CNPJ_DO_CLIENTE)
            centro = self._get_nf_domain("centro", cnpj_centro)

            attachment["domain_data"] = {"fornecedor": fornecedor, "centro": centro}

            miro_model = self._miro_factory(attachment)

            miro = Miro(**miro_model)

            if self._test_mode:
                with open("miro_context_model.json", "w") as json_file:
                    json.dump(miro.model_dump(), json_file, indent=4)

            return Miro(**miro_model).model_dump()

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

    def _get_nf_jira(self, issue_id: str):
        try:
            #### REQUEST ####
            issue_request = requests.get(
                f"{self._api_issue_url}/issue/{issue_id}",
                headers=self._api_headers,
                auth=self._auth,
            )
            issue_request.raise_for_status()
            issue_data = issue_request.json()

            form_id_request = requests.get(
                f"{self._api_form_url}/{self._cloud_id}/issue/{issue_id}/form",
                headers=self._api_atlassian_headers,
                auth=self._auth,
            )
            form_id_request.raise_for_status()
            form_json = form_id_request.json()

            for form in form_json:
                if form.get("formTemplate")["id"] == self._form_template_complemento:
                    form_id = form.get("id")
                elif form.get("formTemplate")["id"] == self._form_template_automacao:
                    automacao_form_id = form.get("id")

            # Get the extra Issue Data From Issue ID and Form ID
            form_request = requests.get(
                f"{self._api_form_url}/{self._cloud_id}/issue/{issue_id}/form/{form_id}",
                headers=self._api_atlassian_headers,
                auth=self._auth,
            )
            form_request.raise_for_status()
            form_data = form_request.json()

            #### REMOVE NULL FIELDS ####
            issue_data["fields"] = self._remove_null_fields(issue_data.get("fields"))

            ### GET ATTACHMENT ###
            if issue_data.get("fields")["attachment"] is None:
                raise Exception("Could not find attachment")

            for attachment in issue_data.get("fields")["attachment"]:
                attachment_id = attachment["id"]
                attachment = self._get_nf_issue_attachment(attachment_id)

                if attachment is not None:
                    attachment_data = attachment

            if "58" in form_data["state"]["answers"] is not None:
                nf_type_id = form_data["state"]["answers"]["58"]["choices"][0]

                if nf_type_id == "1":
                    nf_type = COMPLEMENTO_DE_ÁGUA

                elif nf_type_id == "2":
                    nf_type = COMPLEMENTO_DE_ENERGIA

                elif nf_type_id == "3":
                    nf_type = COMPLEMENTO_DE_GÁS

            else:
                if attachment[COMPLEMENTO_DE_ÁGUA] is not None:
                    nf_type = COMPLEMENTO_DE_ÁGUA
                elif attachment[COMPLEMENTO_DE_ENERGIA] is not None:
                    nf_type = COMPLEMENTO_DE_ENERGIA
                elif attachment[COMPLEMENTO_DE_GÁS] is not None:
                    nf_type = COMPLEMENTO_DE_GÁS

            attachment[CNPJ_DO_FORNECEDOR] = (
                form_data["state"]["answers"]["33"]["text"]
                if "33" in form_data["state"]["answers"]
                else attachment.get(CNPJ_DO_FORNECEDOR)
            )
            attachment[RAZÃO_SOCIAL_DO_FORNECEDOR] = (
                form_data["state"]["answers"]["59"]["text"]
                if "59" in form_data["state"]["answers"]
                else attachment.get(RAZÃO_SOCIAL_DO_FORNECEDOR)
            )
            attachment[CNPJ_DO_CLIENTE] = (
                form_data["state"]["answers"]["42"]["text"]
                if "42" in form_data["state"]["answers"]
                else attachment.get(CNPJ_DO_CLIENTE)
            )
            attachment[NÚMERO_DA_FATURA] = (
                form_data["state"]["answers"]["44"]["text"]
                if "44" in form_data["state"]["answers"]
                else attachment.get(NÚMERO_DA_FATURA)
            )
            attachment[NÚMERO_DA_FATURA_DO_FORNECEDOR] = (
                form_data["state"]["answers"]["45"]["text"]
                if "45" in form_data["state"]["answers"]
                else attachment.get(NÚMERO_DA_FATURA_DO_FORNECEDOR)
            )
            attachment[DATA_DE_EMISSÃO] = (
                form_data["state"]["answers"]["46"]["date"]
                if "46" in form_data["state"]["answers"]
                else attachment.get(DATA_DE_EMISSÃO)
            )
            attachment[DATA_DE_VENCIMENTO] = (
                form_data["state"]["answers"]["47"]["date"]
                if "47" in form_data["state"]["answers"]
                else attachment.get(DATA_DE_VENCIMENTO)
            )
            attachment[CHAVE_DE_ACESSO_DA_FATURA] = (
                form_data["state"]["answers"]["49"]["text"]
                if "49" in form_data["state"]["answers"]
                else attachment.get(CHAVE_DE_ACESSO_DA_FATURA)
            )
            attachment[DATA_DE_REFERÊNCIA] = (
                form_data["state"]["answers"]["50"]["text"]
                if "50" in form_data["state"]["answers"]
                else attachment.get(DATA_DE_REFERÊNCIA)
            )
            attachment["numero_log"] = (
                form_data["state"]["answers"]["52"]["text"]
                if "52" in form_data["state"]["answers"]
                else attachment.get("numero_log")
            )
            attachment["data_procmto"] = (
                form_data["state"]["answers"]["53"]["date"]
                if "53" in form_data["state"]["answers"]
                else attachment.get("data_procmto")
            )
            attachment["hora_procmto"] = (
                form_data["state"]["answers"]["54"]["text"]
                if "54" in form_data["state"]["answers"]
                else attachment.get("hora_procmto")
            )
            attachment[nf_type]["DataLeituraAnterior"] = (
                form_data["state"]["answers"]["55"]["date"]
                if "55" in form_data["state"]["answers"]
                else attachment[nf_type].get("DataLeituraAnterior")
            )
            attachment[nf_type]["DataLeituraAtual"] = (
                form_data["state"]["answers"]["56"]["date"]
                if "56" in form_data["state"]["answers"]
                else attachment[nf_type].get("DataLeituraAtual")
            )

            # Validação de Valor Liquido da Fatura
            if "62" in form_data["state"]["answers"]:
                attachment[VALOR_TOTAL_DA_FATURA] = form_data["state"]["answers"]["62"][
                    "text"
                ]
            elif "48" in form_data["state"]["answers"]:
                attachment[VALOR_TOTAL_DA_FATURA] = form_data["state"]["answers"]["48"][
                    "text"
                ]
            else:
                attachment[VALOR_TOTAL_DA_FATURA] = attachment.get(
                    VALOR_TOTAL_DA_FATURA
                )

            jira_info = {"issue_id": issue_id, "form_id": automacao_form_id}

            nf_jira_json = {
                "issue_data": issue_data,
                "attachment": attachment_data,
                "jira_info": jira_info,
            }

            return nf_jira_json

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

    def _get_nf_issue_attachment(self, attachment_id: str):
        try:
            attachment_request = requests.get(
                f"{self._api_issue_url}/attachment/content/{attachment_id}",
                headers=self._api_attachment_headers,
                auth=self._auth,
            )
            attachment_request.raise_for_status()
            content_type = attachment_request.headers.get("Content-Type", "")
            if "application/pdf" in content_type:
                return None
            attachment_data = attachment_request.json()

            return attachment_data

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")

    def _get_nf_domain(self, type: str, cnpj: str):

        try:
            domain_request = requests.get(
                f"{self._api_domain_url}/{'fornecedores' if type == 'fornecedor' else 'centros'}?cnpj={cnpj}",
                auth=self._n8n_auth,
            )
            domain_request.raise_for_status()
            domain_data = domain_request.json()

            if not domain_data:
                raise Exception("Could not find domain")

        except Exception as e:
            raise Exception(f"Erro ao receber {type}:\n{e}")

        return domain_data

    def _get_allocation(
        self, cnpj_fornecedor: str, cnpj_cliente: str, numero_contrato: str
    ):

        try:
            allocation_request = requests.get(
                f"{self._api_domain_url}/rateio?cnpj_fornecedor={cnpj_fornecedor}&cnpj_hortifruti={cnpj_cliente}&numero_contrato={numero_contrato}",
                auth=self._n8n_auth,
            )
            allocation_request.raise_for_status()
            if allocation_request.text.strip() != "":
                allocation_data = allocation_request.json()
            else:
                allocation_data = None
        except Exception as e:
            raise Exception(f"Erro ao receber rateio:\n{e}")

        return allocation_data

    def _download_pdf(self, pdf_path):
        path_dir = path.join(getcwd(), "output")
        pdf_file = ConsumoService().download_pdf(pdf_path, path_dir)

        return pdf_file

    def _save_form_answers(self, answers, issue_id, form_id):

        try:
            save_request = requests.put(
                f"{self._api_form_url}/{self._cloud_id}/issue/{issue_id}/form/{form_id}",
                headers=self._api_atlassian_headers,
                auth=self._auth,
                json=answers,
            )

            return save_request.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")

    def update_jira_form(self, issue, data):

        answers = {
            "answers": {
                "4": {
                    "text": (
                        data["cod_fatura"] if "cod_fatura" in data else None
                    )  ##Codigo SAP FV60
                },
                "5": {
                    "text": (
                        data["status_liberacao"] if "status_liberacao" in data else None
                    )  ##Status de Aprovação
                },
                "7": {
                    "text": (
                        data["cod_miro"] if "cod_miro" in data else None
                    )  ##Codigo SAP Miro
                },
                "6": {
                    "text": (
                        data["data_liberacao"] if "data_liberacao" in data else None
                    )  ##Data de Aprovação
                },
                "1": {
                    "text": (
                        data["cod_nota_pedido"] if "cod_nota_pedido" in data else None
                    )  ##Codigo SAP Nota de Pedido
                },
            }
        }

        self._save_form_answers(answers, issue["issue_id"], issue["form_id"])

        return True

    def post_transition(self, transition_id, issue_id):
        payload = json.dumps(
            {
                "transition": {"id": transition_id},
                "update": {"comment": []},
            }
        )
        res = requests.post(
            f"{self._api_issue_url}/issue/{issue_id}/transitions",
            auth=self._auth,
            headers=self._api_headers,
            data=payload,
        )
        res.raise_for_status()

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
from django.db import transaction as transaction_django

from apps.accounts.models import Account, Installment, OmieAccount
from apps.transactions.models import Transaction


class OmieService:
    def __init__(self):
        self.omie_app_key = str(os.getenv("OMIE_APP_KEY"))
        self.omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))
        self.base_url = "https://app.omie.com.br/api/v1/financas"
        self.headers = {"Content-Type": "application/json"}

    def create_transactions(self) -> str:
        with transaction_django.atomic():
            transaction_ids = self.get_omie_transactions()
            with ThreadPoolExecutor(max_workers=3) as executor:
                results = executor.map(self.consult_omie_transaction, transaction_ids)

            transactions_data = [result for result in results if result]
            self._bulk_create_transactions(transactions_data)
            return "Success"

    def consult_omie_transaction(self, omie_id: int) -> dict:
        payload = {
            "call": "ConsultarContaReceber",
            "param": [{"codigo_lancamento_omie": omie_id}],
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret,
        }

        response = self._send_request(payload, "contareceber")
        if response and response.status_code == 200:
            transaction = response.json()
            return {
                "cod_id_omie": omie_id,
                "omie_account_id": transaction.get("id_conta_corrente", "NULO"),
                "tid": transaction.get("nsu", "NULO"),
                "expected_value": transaction.get("valor_documento", 0.0),
                "fee": transaction.get("numero_parcela", "001/001"),
                "balance": 0.0,
                "expected_date": transaction.get("data_registro", "NULO"),
                "accounts_receivable_note": transaction.get("observacao", "NULO"),
                "document_type": transaction.get("codigo_tipo_documento", "NULO"),
                "status": "Aguardando pagamento",
                "status_titulo": transaction.get("status_titulo", "NULO"),
                "project": transaction.get("codigo_projeto", None),
                "department": (transaction.get("distribuicao") or [{}])[0].get(
                    "cCodDep", None
                ),
            }
        return {}

    def consult_omie_fee(self):
        nPage = 1
        nPerPage = 500
        codes = []

        while True:
            payload = {
                "call": "ListarLancCC",
                "param": [{"nPagina": nPage, "nRegPorPagina": nPerPage}],
                "app_key": self.omie_app_key,
                "app_secret": self.omie_app_secret,
            }

            response = self._send_request(payload, "contacorrentelancamentos")

            if response and response.status_code == 200:
                data = response.json()
                fees = data.get("listaLancamentos", [])

                if not fees:
                    break

                codes.extend(item.get("cCodIntLanc") for item in fees)

                nPage += 1
            else:
                raise Exception("Erro ao consultar API OMIE")

        return codes

    def release_omie_receipt(self, transaction: Transaction) -> bool:
        date = datetime.now().strftime("%d/%m/%Y")
        payment_date = (
            transaction.payment_date.strftime("%d/%m/%Y")
            if transaction.payment_date
            else None
        )
        value = (
            transaction.received_value
            if transaction.received_value
            and transaction.received_value <= transaction.expected_value
            else transaction.expected_value
        )
        payload = {
            "call": "LancarRecebimento",
            "param": [
                {
                    "codigo_lancamento": transaction.cod_id_omie,
                    "codigo_baixa": 0,
                    "codigo_conta_corrente": transaction.account.omie_account_origin.omie_id,
                    "valor": value,
                    "data": payment_date if payment_date else date,
                    "observacao": "Baixa via sistema Conciliadora CC",
                }
            ],
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret,
        }

        response = self._send_request(payload, "contareceber")
        if response and response.status_code == 200:
            return True

        return False

    def launch_omie_fee(self, transaction: Transaction) -> bool:
        date = datetime.now().strftime("%d/%m/%Y")
        payment_date = (
            transaction.payment_date.strftime("%d/%m/%Y")
            if transaction.payment_date
            else None
        )
        doc_type = (
            "CRT" if transaction.document_type in ["CREDIT", "DEBIT"] else "99999"
        )
        detalhes = {
            "cCodCateg": "2.05.02",
            "cTipo": doc_type,
            "cObs": "Lançamento via sistema Conciliadora CC",
        }

        if transaction.project:
            detalhes["nCodProjeto"] = transaction.project

        param_item = {
            "cCodIntLanc": f"{transaction.tid}-{transaction.installment}",
            "cabecalho": {
                "nCodCC": transaction.account.omie_account_origin.omie_id,
                "dDtLanc": payment_date if payment_date else date,
                "nValorLanc": transaction.acquirer_fee,
            },
            "detalhes": detalhes,
        }

        if transaction.department:
            param_item["departamentos"] = {
                "cCodDep": transaction.department,
                "nValDep": transaction.acquirer_fee,
            }

        payload = {
            "call": "IncluirLancCC",
            "param": [param_item],
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret,
        }

        response = self._send_request(payload, "contacorrentelancamentos")
        if response and response.status_code == 200:
            return True

        return False

    def transfer_omie_value(self, transaction: Transaction) -> bool:
        date = datetime.now().strftime("%d/%m/%Y")
        payment_date = (
            transaction.payment_date.strftime("%d/%m/%Y")
            if transaction.payment_date
            else None
        )
        doc_type = (
            "CRT" if transaction.document_type in ["CREDIT", "DEBIT"] else "99999"
        )
        detalhes = {
            "cCodCateg": "0.01.02",
            "cTipo": doc_type,
            "cObs": "Transferência via sistema Conciliadora CC",
        }

        if transaction.project:
            detalhes["nCodProjeto"] = transaction.project

        param_item = {
            "cCodIntLanc": f"{transaction.tid}-{transaction.installment}",
            "cabecalho": {
                "nCodCC": transaction.account.omie_account_origin.omie_id,
                "dDtLanc": payment_date if payment_date else date,
                "nValorLanc": transaction.received_value - transaction.acquirer_fee,
            },
            "detalhes": detalhes,
            "transferencia": {
                "nCodCCDestino": transaction.account.omie_account_destiny.omie_id,
            },
        }

        if transaction.department:
            param_item["departamentos"] = {
                "cCodDep": transaction.department,
                "nValDep": transaction.received_value - transaction.acquirer_fee,
            }

        payload = {
            "call": "IncluirLancCC",
            "param": [param_item],
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret,
        }

        response = self._send_request(payload, "contacorrentelancamentos")
        if response and response.status_code == 200:
            return True

        return False

    def get_omie_transactions(self) -> list:
        ids = []
        date = datetime.now().strftime("%d/%m/%Y")
        page = 1
        existing_ids = set(Transaction.objects.values_list("cod_id_omie", flat=True))

        while True:
            payload = {
                "call": "ListarContasReceber",
                "param": [
                    {
                        "pagina": page,
                        "registros_por_pagina": 20,
                        "apenas_importado_api": "N",
                        "filtrar_por_data_de": date,
                        "filtrar_por_data_ate": date,
                    }
                ],
                "app_key": self.omie_app_key,
                "app_secret": self.omie_app_secret,
            }

            response = self._send_request(payload, "contareceber")
            if not response or response.status_code != 200:
                break

            data = response.json()
            if not (transactions := data.get("conta_receber_cadastro", [])):
                break

            for transaction in transactions:
                cod_id_omie = transaction.get("codigo_lancamento_omie")
                document_type = transaction.get("codigo_tipo_documento", "")
                if (
                    document_type in ["PIX", "CRC", "CRD"]
                    and cod_id_omie not in existing_ids
                ):
                    ids.append(cod_id_omie)
                    existing_ids.add(cod_id_omie)

            page += 1

        return ids

    def _bulk_create_transactions(self, transactions_data: list) -> None:
        transactions_to_create = []
        start_date = datetime(2024, 11, 1).date()

        for data in transactions_data:
            account_omie = OmieAccount.objects.get(omie_id=data["omie_account_id"])
            account = Account.objects.get(omie_account_origin=account_omie)

            days_plus = account.days_to_receive
            date_obj = datetime.strptime(data["expected_date"], "%d/%m/%Y").date()
            date_obj += timedelta(days=days_plus)

            if date_obj >= start_date:
                fee_number = int(data["fee"].split("/")[1])
                installment = Installment.objects.get(
                    account=account, installment_number=fee_number
                )
                fee_percent = installment.fee
                formatted_value = round(data["expected_value"], 2)
                new_fee = round(formatted_value * (fee_percent / 100), 2)
                new_balance = round(formatted_value - new_fee, 2)

                doc_type = {"PIX": "PIX", "CRC": "CREDIT", "CRD": "DEBIT"}
                transaction = Transaction(
                    cod_id_omie=data["cod_id_omie"],
                    account=account,
                    tid=data["tid"],
                    expected_value=formatted_value,
                    fee=new_fee,
                    balance=new_balance,
                    expected_date=date_obj,
                    accounts_receivable_note=data["accounts_receivable_note"],
                    document_type=doc_type[data["document_type"]],
                    installment=data["fee"],
                    status=data["status"],
                    project=data["project"],
                    department=data["department"],
                )
                transactions_to_create.append(transaction)

        Transaction.objects.bulk_create(transactions_to_create)

        for transaction in transactions_to_create:
            if transaction.account.settle:
                if self.release_omie_receipt(transaction):
                    transaction.omie_receipt_releasead = True
                    transaction.save()

    def _send_request(self, payload: dict, endpoint: str):
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}/",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=(5, 15),
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

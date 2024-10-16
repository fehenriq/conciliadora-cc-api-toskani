import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

from apps.accounts.models import Account, Installment, OmieAccount
from apps.transactions.models import Transaction


class OmieService:
    def __init__(self):
        self.omie_app_key = str(os.getenv("OMIE_APP_KEY"))
        self.omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))
        self.base_url = "https://app.omie.com.br/api/v1/financas/contareceber/"
        self.headers = {"Content-Type": "application/json"}

    def create_transactions(self) -> str:
        transaction_ids = self.get_omie_transactions()
        with ThreadPoolExecutor(max_workers=10) as executor:
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

        response = self._send_request(payload)
        if response and response.status_code == 200:
            transaction = response.json()
            return {
                "cod_id_omie": omie_id,
                "omie_account_id": transaction.get("id_conta_corrente", "NULO"),
                "tid": transaction.get("nsu", "NULO"),
                "expected_value": transaction.get("valor_documento", 0.0),
                "fee": transaction.get("numero_parcela", "001/001"),
                "balance": 0.0,
                "expected_date": transaction.get("data_previsao", "NULO"),
                "accounts_receivable_note": transaction.get("observacao", "NULO"),
                "document_type": transaction.get("codigo_tipo_documento", "NULO"),
            }
        return {}

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

            response = self._send_request(payload)
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
        for data in transactions_data:
            account_omie = OmieAccount.objects.get(omie_id=data["omie_account_id"])
            account = Account.objects.get(omie_account=account_omie)

            date_obj = datetime.strptime(data["expected_date"], "%d/%m/%Y").date()
            fee_number = int(data["fee"].split("/")[0])
            installment = Installment.objects.get(
                account=account, installment_number=fee_number
            )
            fee_percent = installment.fee
            new_fee = data["expected_value"] * (fee_percent / 100)
            new_balance = data["expected_value"] - new_fee

            doc_type = {"PIX": "PIX", "CRC": "CREDIT", "CRD": "DEBIT"}
            transaction = Transaction(
                cod_id_omie=data["cod_id_omie"],
                account=account,
                tid=data["tid"],
                expected_value=data["expected_value"],
                fee=new_fee,
                balance=new_balance,
                expected_date=date_obj,
                accounts_receivable_note=data["accounts_receivable_note"],
                document_type=doc_type[data["document_type"]],
            )
            transactions_to_create.append(transaction)

        Transaction.objects.bulk_create(transactions_to_create)

    def _send_request(self, payload: dict):
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=(5, 15),
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

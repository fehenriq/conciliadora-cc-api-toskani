import json
import os
from datetime import datetime

import requests

from apps.accounts.models import Account, OmieAccount, Installment
from apps.transactions.models import Transaction


def create_transactions() -> str:
    trasactions_ids = get_omie_transactions()
    for transaction_id in trasactions_ids:
        transaction_data = consult_omie_transaction(transaction_id)

        account_omie = OmieAccount.objects.get(
            omie_id=transaction_data["omie_account_id"]
        )
        account = Account.objects.get(omie_account=account_omie)

        date_obj = datetime.strptime(
            transaction_data["expected_date"], "%d/%m/%Y"
        ).date()

        fee_number = int(transaction_data["fee"].split("/")[0])
        installment = Installment.objects.get(
            account=account, installment_number=fee_number
        )
        fee_percent = installment.fee
        new_fee = transaction_data["expected_value"] * (fee_percent / 100)
        new_balance = transaction_data["expected_value"] - new_fee

        doc_type = {"PIX": "PIX", "CRC": "CREDIT", "CRD": "DEBIT"}

        Transaction.objects.get_or_create(
            cod_id_omie=transaction_data["cod_id_omie"],
            defaults={
                "account": account,
                "tid": transaction_data["tid"],
                "expected_value": transaction_data["expected_value"],
                "fee": new_fee,
                "balance": new_balance,
                "expected_date": date_obj,
                "accounts_receivable_note": transaction_data[
                    "accounts_receivable_note"
                ],
                "document_type": doc_type[transaction_data["document_type"]],
            },
        )

    return "Success"


def consult_omie_transaction(omie_id: int) -> dict:
    url = "https://app.omie.com.br/api/v1/financas/contareceber/"
    omie_app_key = str(os.getenv("OMIE_APP_KEY"))
    omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))

    payload = {
        "call": "ConsultarContaReceber",
        "param": [{"codigo_lancamento_omie": omie_id}],
        "app_key": omie_app_key,
        "app_secret": omie_app_secret,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
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


def get_omie_transactions() -> list:
    url = "https://app.omie.com.br/api/v1/financas/contareceber/"
    omie_app_key = str(os.getenv("OMIE_APP_KEY"))
    omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))
    date = datetime.now().strftime("%d/%m/%Y")
    ids = []

    page = 1
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
            "app_key": omie_app_key,
            "app_secret": omie_app_secret,
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code != 200:
            break

        data = response.json()
        transactions = data.get("conta_receber_cadastro", [])
        if not transactions:
            break

        for transaction in transactions:
            cod_id_omie = transaction.get("codigo_lancamento_omie")
            document_type = transaction.get("codigo_tipo_documento", "")

            if (
                document_type in ["PIX", "CRC", "CRD"]
                and not Transaction.objects.filter(cod_id_omie=cod_id_omie).exists()
            ):
                ids.append(cod_id_omie)

        page += 1

    return ids

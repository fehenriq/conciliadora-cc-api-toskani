import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

import requests
from django.db import transaction as transaction_django
from django.db.models import Q
from django.utils import timezone

from apps.accounts.services.account_service import AccountService
from apps.transactions.models import Transaction
from apps.transactions.services.omie_service import OmieService


class ToskaniService:
    def __init__(self):
        self.base_url = (
            "https://api.toskani.com.br/app/v3/consulta?token=8a1ff28c5c7d&ref=bs"
        )
        self.headers = {
            "Content-Type": "application/json",
        }
        self.omie_service = OmieService()
        self.account_service = AccountService()

    def consult_toskani(self) -> str:
        transactions = Transaction.objects.filter(
            (
                Q(omie_receipt_releasead=False)
                | Q(omie_fee_launched=False)
                | (
                    Q(omie_value_transferred=False)
                    & Q(account__omie_account_destiny__isnull=False)
                )
            )
            & Q(expected_date__lte=timezone.now().date())
        )

        with transaction_django.atomic():
            with ThreadPoolExecutor(max_workers=3) as executor:
                consult_func = partial(self.consult_toskani_by_order, sum_all=True)
                results = executor.map(consult_func, transactions)

            updates = []
            for transaction, toskani_data in zip(transactions, results):
                if toskani_data:
                    installment_number = int(transaction.installment.split("/")[0])
                    account = transaction.account

                    formatted_value = round(toskani_data.get("received_value"), 2)
                    formatted_fee = (
                        self.account_service.get_installment_by_account_and_number(
                            account, installment_number
                        ).fee
                    )
                    value_diff = transaction.balance - (formatted_value - formatted_fee)
                    tolerance = 0.0005 * formatted_value

                    transaction.received_value = formatted_value
                    transaction.acquirer_fee = formatted_fee
                    transaction.value_difference = value_diff
                    transaction.payment_date = toskani_data.get("payment_date")
                    transaction.status = (
                        "Pagamento recebido com sucesso"
                        if abs(value_diff) <= tolerance
                        else "Pagamento recebido parcialmente"
                    )
                    updates.append(transaction)

            Transaction.objects.bulk_update(
                updates,
                ["received_value", "acquirer_fee", "value_difference", "status"],
            )

            print(len(updates))
            for transaction in updates:
                time.sleep(2)
                print(transaction.cod_id_omie)
                self.process_transaction_updates(transaction)

            return "Success"

    def process_transaction_updates(self, transaction: Transaction):
        if not transaction.account.settle:
            if not transaction.omie_receipt_releasead:
                if self.omie_service.release_omie_receipt(transaction):
                    transaction.omie_receipt_releasead = True
                    transaction.save()
                    print("Release Receipt: OK")

        if not transaction.omie_fee_launched:
            if self.omie_service.launch_omie_fee(transaction):
                transaction.omie_fee_launched = True
                transaction.save()
                print("Launch Fee: OK")

        if transaction.account.omie_account_destiny:
            if not transaction.omie_value_transferred:
                if self.omie_service.transfer_omie_value(transaction):
                    transaction.omie_value_transferred = True
                    transaction.save()
                    print("Transfer Value: OK")

    def consult_toskani_by_order(self, transaction: Transaction) -> dict:
        url = f"{self.base_url}&pedido={transaction.cod_id_omie}"
        response = self._send_request(url)
        if response and response.json():
            response_data = response.json()

            if response_data.get("status_pedido") == 2:
                toskani_data = {
                    "received_value": response_data.get("valor"),
                    "payment_date": datetime.strptime(
                        response_data.get("data_pagamento"), "%Y-%m-%d %H:%M:%S"
                    ).date(),
                }
                return toskani_data

        return {}

    def _send_request(self, url: str):
        try:
            response = requests.get(url, headers=self.headers, timeout=(5, 15))
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

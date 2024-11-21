import base64
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

import requests
from django.db import transaction as transaction_django
from django.db.models import Q
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.transactions.services.omie_service import OmieService


class PagarmeService:
    def __init__(self):
        self.base_url = "https://api.pagar.me/1/transactions"
        self.access_token = str(os.getenv("PAGARME_ACCESS_KEY"))
        self.headers = {
            "Authorization": f"Basic {self._encode_token()}",
            "Content-Type": "application/json",
        }
        self.cache = {}
        self.omie_service = OmieService()

    def consult_pagarme(self) -> str:
        transactions = Transaction.objects.filter(
            (
                Q(omie_receipt_releasead=False)
                | Q(omie_fee_launched=False)
                | Q(omie_value_transferred=False)
            )
            & Q(expected_date__lte=timezone.now().date())
        )

        with transaction_django.atomic():
            with ThreadPoolExecutor(max_workers=3) as executor:
                consult_func = partial(self.consult_pagarme_by_nsu, sum_all=True)
                results = executor.map(consult_func, transactions)

            updates = []
            for transaction, pagarme_data in zip(transactions, results):
                if pagarme_data:
                    formatted_value = round(pagarme_data.get("received_value"), 2)
                    formatted_fee = round(pagarme_data.get("acquirer_fee"), 2)
                    value_diff = transaction.balance - (formatted_value - formatted_fee)
                    tolerance = 0.0005 * formatted_value

                    transaction.received_value = formatted_value
                    transaction.acquirer_fee = formatted_fee
                    transaction.value_difference = value_diff
                    transaction.payment_date = pagarme_data.get("payment_date")
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

        if not transaction.omie_fee_launched:
            if self.omie_service.launch_omie_fee(transaction):
                transaction.omie_fee_launched = True
                transaction.save()

        if transaction.account.omie_account_destiny:
            if not transaction.omie_value_transferred:
                if self.omie_service.transfer_omie_value(transaction):
                    transaction.omie_value_transferred = True
                    transaction.save()

    def consult_pagarme_by_nsu(self, transaction: Transaction, sum_all: bool) -> dict:
        response_data = None
        if transaction.tid not in self.cache:
            url = f"{self.base_url}/{transaction.tid}/payables"
            response = self._send_request(url)
            if response and response.json():
                response_data = response.json()
        else:
            response_data = self.cache[transaction.tid]

        if response_data:
            self.cache[transaction.tid] = response_data

            installment_number = int(transaction.installment.split("/")[0])

            if sum_all:
                filtered_payables = [
                    payable
                    for payable in response_data
                    if payable.get("installment") == installment_number
                    and payable.get("status") == "paid"
                    and payable.get("amount", 0) > 0
                ]

                total_received_value = sum(
                    payable.get("amount") / 100 for payable in filtered_payables
                )

                total_acquirer_fee = sum(
                    payable.get("fee") / 100 for payable in filtered_payables
                )

                if total_received_value <= 0:
                    return {}

                pagarme_data = {
                    "received_value": total_received_value,
                    "acquirer_fee": total_acquirer_fee,
                    "payment_date": datetime.fromisoformat(
                        filtered_payables[-1].get("payment_date").rstrip("Z")
                    ).date(),
                }

                return pagarme_data

            installment_data = next(
                (
                    payable
                    for payable in response_data
                    if payable.get("installment") == installment_number
                    and payable.get("status") == "paid"
                    and payable.get("amount") > 0
                ),
                None,
            )

            if installment_data:
                received_value_real = installment_data.get("amount") / 100
                acquirer_fee_real = installment_data.get("fee") / 100
                pagarme_data = {
                    "received_value": received_value_real,
                    "acquirer_fee": acquirer_fee_real,
                    "payment_date": datetime.fromisoformat(
                        installment_data.get("payment_date").rstrip("Z")
                    ).date(),
                }
                return pagarme_data

        return {}

    def _encode_token(self) -> str:
        return base64.b64encode(f"{self.access_token}:".encode()).decode()

    def _send_request(self, url: str):
        try:
            response = requests.get(url, headers=self.headers, timeout=(5, 15))
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

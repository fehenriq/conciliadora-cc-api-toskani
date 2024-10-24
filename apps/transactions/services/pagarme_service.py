import base64
import os
from concurrent.futures import ThreadPoolExecutor

import requests

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
        transactions = Transaction.objects.filter(received_value__isnull=True)
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.consult_pagarme_by_nsu, transactions)

        updates = []
        for transaction, pagarme_data in zip(transactions, results):
            if pagarme_data:
                formatted_value = round(pagarme_data.get("received_value"), 2)
                value_diff = transaction.expected_value - formatted_value
                transaction.received_value = formatted_value
                transaction.value_difference = value_diff
                transaction.status = (
                    "Pagamento recebido com sucesso"
                    if value_diff <= 0
                    else "Pagamento recebido parcialmente"
                )
                updates.append(transaction)

        Transaction.objects.bulk_update(
            updates, ["received_value", "value_difference", "status"]
        )

        # TODO: Change when ready
        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     executor.map(self.process_transaction_updates, updates)

        return "Success"

    def process_transaction_updates(self, transaction: Transaction):
        if transaction.account.settle:
            self.omie_service.release_omie_receipt(transaction)

        self.omie_service.launch_omie_fee(transaction)

        if transaction.account.omie_account_destiny:
            self.omie_service.transfer_omie_value(transaction)

    def consult_pagarme_by_nsu(self, transaction: Transaction) -> dict:
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
                pagarme_data = {
                    "received_value": received_value_real,
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

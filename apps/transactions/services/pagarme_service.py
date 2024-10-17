import base64
import os
from concurrent.futures import ThreadPoolExecutor

import requests

from apps.transactions.models import Transaction


class PagarmeService:
    def __init__(self):
        self.base_url = "https://api.pagar.me/1/transactions"
        self.access_token = str(os.getenv("PAGARME_ACCESS_KEY"))
        self.headers = {
            "Authorization": f"Basic {self._encode_token()}",
            "Content-Type": "application/json",
        }
        self.cache = {}

    def consult_pagarme(self) -> str:
        transactions = Transaction.objects.filter(received_value__isnull=True)
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.consult_pagarme_by_nsu, transactions)

        updates = []
        for transaction, pagarme_data in zip(transactions, results):
            if pagarme_data:
                formatted_value = round(pagarme_data.get("received_value"), 2)
                transaction.received_value = formatted_value
                transaction.value_difference = (
                    transaction.expected_value - formatted_value
                )
                transaction.status = pagarme_data.get("status")
                updates.append(transaction)

        Transaction.objects.bulk_update(
            updates, ["received_value", "value_difference", "status"]
        )

        return "Success"

    def consult_pagarme_by_nsu(self, transaction: Transaction) -> dict:
        if transaction.tid in self.cache:
            return self.cache[transaction.tid]

        url = f"{self.base_url}/{transaction.tid}"
        response = self._send_request(url)

        if response and response.json():
            response_data = response.json()
            received_value_real = (
                response_data.get("paid_amount") / 100
            ) / response_data.get("installments")
            pagarme_data = {
                "received_value": received_value_real,
                "status": response_data.get("acquirer_response_message", ""),
            }
            self.cache[transaction.tid] = pagarme_data
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

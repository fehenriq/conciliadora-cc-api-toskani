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

    def consult_pagarme(self) -> str:
        transactions = Transaction.objects.all()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.consult_pagarme_by_nsu, transactions)

        updates = []
        for transaction, pagarme_data in zip(transactions, results):
            if pagarme_data:
                transaction.received_value = pagarme_data.get("received_value")
                transaction.value_difference = (
                    transaction.expected_value - pagarme_data.get("received_value", 0)
                )
                transaction.status = pagarme_data.get("status")
                transaction.alert = pagarme_data.get("alert")
                updates.append(transaction)

        Transaction.objects.bulk_update(
            updates, ["received_value", "value_difference", "status", "alert"]
        )

        return "Success"

    def consult_pagarme_by_nsu(self, transaction: Transaction) -> dict:
        url = f"{self.base_url}?tid={transaction.tid}"
        response = self._send_request(url)

        if response and response.json():
            response_data = response.json()[0]
            return {
                "received_value": response_data.get("paid_amount", 0.0),
                "status": response_data.get("acquirer_response_message", ""),
                "alert": response_data.get("date_updated", ""),
            }
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
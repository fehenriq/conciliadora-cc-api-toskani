import base64
import os

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
        for transaction in transactions:
            if pagarme_data := self.consult_pagarme_by_nsu(transaction.tid):
                transaction.received_value = pagarme_data.get("received_value")
                transaction.value_difference = (
                    transaction.expected_value - pagarme_data.get("received_value", 0)
                )
                transaction.status = pagarme_data.get("status")
                transaction.alert = pagarme_data.get("alert")
                transaction.save()

        return "Success"

    def consult_pagarme_by_nsu(self, tid: str) -> dict:
        url = f"{self.base_url}?tid={tid}"
        response = self._send_request(url)

        if response_data := response.json():
            return {
                "received_value": response_data[0].get("paid_amount", 0.0),
                "value_difference": 0.0,
                "status": response_data[0].get("acquirer_response_message", ""),
                "alert": response_data[0].get("date_updated", ""),
            }

        return {}

    def _encode_token(self) -> str:
        return base64.b64encode(f"{self.access_token}:".encode()).decode()

    def _send_request(self, url: str):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

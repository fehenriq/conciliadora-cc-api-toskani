import base64
import os

import requests
from apps.transactions.models import Transaction


def consult_pagarme():
    transactions = Transaction.objects.all()
    for transaction in transactions:
        if pagarme_data := consult_pagarme_by_nsu(transaction.tid):
            transaction.received_value = pagarme_data.get("received_value")
            transaction.value_difference = (
                transaction.expected_value - pagarme_data.get("received_value", 0)
            )
            transaction.status = pagarme_data.get("status")
            transaction.alert = pagarme_data.get("alert")
            transaction.save()

    return "Success"


def consult_pagarme_by_nsu(tid):
    url = "https://api.pagar.me/1/transactions"
    acess_token = str(os.getenv("PAGARME_ACCESS_KEY"))

    base64_token = base64.b64encode(f"{acess_token}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {base64_token}",
        "Content-Type": "application/json",
    }

    params = {"tid": tid}

    response = requests.get(url, headers=headers, params=params)

    if response_data := response.json():
        return {
            "received_value": response_data[0].get("paid_amount"),
            "value_difference": 0.0,
            "status": response_data[0].get("acquirer_response_message"),
            "alert": response_data[0].get("date_updated"),
        }

    return {}

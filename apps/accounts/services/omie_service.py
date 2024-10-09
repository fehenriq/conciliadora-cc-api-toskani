import json
import os

import requests

from apps.accounts.models import OmieAccount


def get_omie_accounts():
    url = "https://app.omie.com.br/api/v1/geral/contacorrente/"
    omie_app_key = str(os.getenv("OMIE_APP_KEY"))
    omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))

    payload = {
        "call": "ListarContasCorrentes",
        "param": [
            {"pagina": 1, "registros_por_pagina": 100, "apenas_importado_api": "N"}
        ],
        "app_key": omie_app_key,
        "app_secret": omie_app_secret,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        for conta in data.get("ListarContasCorrentes", []):
            nCodCC = conta.get("nCodCC")
            numero_conta_corrente = conta.get("numero_conta_corrente", "Sem Número CC")
            descricao = conta.get("descricao", "Sem Descrição")

            OmieAccount.objects.get_or_create(
                omie_id=nCodCC,
                defaults={
                    "account_number": numero_conta_corrente,
                    "description": descricao,
                },
            )

    return "Success"

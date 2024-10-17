import json
import os

import requests

from apps.accounts.models import OmieAccount


class OmieService:
    def __init__(self):
        self.url = "https://app.omie.com.br/api/v1/geral/contacorrente/"
        self.omie_app_key = str(os.getenv("OMIE_APP_KEY"))
        self.omie_app_secret = str(os.getenv("OMIE_APP_SECRET"))
        self.headers = {"Content-Type": "application/json"}

    def get_omie_accounts(self) -> str:
        payload = self._build_payload()
        response = self._send_request(payload)

        if response and response.status_code == 200:
            data = response.json()
            self._process_accounts(data)
            return "Success"
        return "Failed"

    def _build_payload(self) -> dict:
        return {
            "call": "ListarContasCorrentes",
            "param": [
                {"pagina": 1, "registros_por_pagina": 100, "apenas_importado_api": "N"}
            ],
            "app_key": self.omie_app_key,
            "app_secret": self.omie_app_secret,
        }

    def _send_request(self, payload: dict):
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=(5, 15),
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def _process_accounts(self, data: dict) -> None:
        for conta in data.get("ListarContasCorrentes", []):
            nCodCC = conta.get("nCodCC")
            descricao = conta.get("descricao", "Sem Descrição")

            OmieAccount.objects.get_or_create(
                omie_id=nCodCC,
                defaults={
                    "description": descricao,
                },
            )

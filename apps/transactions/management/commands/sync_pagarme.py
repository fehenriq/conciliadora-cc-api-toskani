from django.core.management.base import BaseCommand

from apps.transactions.services.pagarme_service import PagarmeService


class Command(BaseCommand):
    help = "Consulta cada Transaction pelo cod_id_pagarme e atualiza com os dados da API Pagarme."

    def handle(self, *args, **kwargs):
        pagarme_service = PagarmeService()

        pagarme_service.consult_pagarme()

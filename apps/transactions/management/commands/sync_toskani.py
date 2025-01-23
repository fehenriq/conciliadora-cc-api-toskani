from django.core.management.base import BaseCommand

from apps.transactions.services.toskani_service import ToskaniService


class Command(BaseCommand):
    help = "Consulta cada Transaction e atualiza com os dados da API Toskani."

    def handle(self, *args, **kwargs):
        toskani_service = ToskaniService()

        toskani_service.consult_toskani()

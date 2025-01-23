from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.transactions.models import Transaction
from apps.transactions.services.omie_service import OmieService


class Command(BaseCommand):
    help = "Consulta cada Transaction pelo cod_id_omie e atualiza com os dados da API Omie."

    def handle(self, *args, **kwargs):
        omie_service = OmieService()

        transactions = Transaction.objects.filter(
            (
                Q(omie_receipt_releasead=False)
                | Q(omie_fee_launched=False)
                | (
                    Q(omie_value_transferred=False)
                    & Q(account__omie_account_destiny__isnull=False)
                )
            )
            & Q(expected_date__lte=timezone.now().date())
            & Q(expected_date__gte=datetime(2024, 12, 1))
        )

        print(transactions.count())

        for transaction in transactions:
            cod_id_omie = transaction.cod_id_omie
            self.stdout.write(f"Consultando cod_id_omie: {cod_id_omie}")

            if result := omie_service.consult_omie_transaction(cod_id_omie):
                title_status = result.get("title_status")
                self.stdout.write(
                    f"Transação {cod_id_omie} consultada com sucesso: {title_status}"
                )

                if (
                    title_status == "RECEBIDO"
                    and not transaction.omie_receipt_releasead
                ):
                    transaction.omie_receipt_releasead = True
                    transaction.save()
                    self.stdout.write(
                        f"Transação {cod_id_omie} atualizada: omie_receipt_releasead=True"
                    )
            else:
                self.stdout.write(f"Erro ao consultar cod_id_omie: {cod_id_omie}")

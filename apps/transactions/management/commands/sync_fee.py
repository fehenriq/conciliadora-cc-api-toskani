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

        int_codes = omie_service.consult_omie_fee()

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
            & Q(expected_date__gte=datetime(2024, 11, 1))
        )

        print(transactions.count())

        for transaction in transactions:
            identifier = f"{transaction.tid}-{transaction.installment}"
            if identifier in int_codes:
                self.stdout.write(
                    self.style.SUCCESS(f"Transaction {identifier} foi lançado.")
                )

                if not transaction.omie_fee_launched:
                    transaction.omie_fee_launched = True
                    transaction.save()
                    self.stdout.write(
                        f"Transação {identifier} atualizada: omie_fee_launched=True"
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Transaction {identifier} não foi lançado.")
                )

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from apps.transactions.models import Transaction
from apps.transactions.services.omie_service import OmieService


class Command(BaseCommand):
    help = "Consulta cada Transaction pelo cod_id_omie e atualiza o campo expected_date com a data_registro da API Omie."

    def handle(self, *args, **kwargs):
        omie_service = OmieService()

        transactions = Transaction.objects.all()

        print(transactions.count())

        for transaction in transactions:
            cod_id_omie = transaction.cod_id_omie
            self.stdout.write(f"Consultando cod_id_omie: {cod_id_omie}")

            if result := omie_service.consult_omie_transaction(cod_id_omie):
                register_date = result.get("expected_date")
                self.stdout.write(
                    f"Transação {cod_id_omie} consultada com sucesso: data_registro={register_date}"
                )

                if register_date:
                    installment = int(transaction.installment.split("/")[0])
                    days_plus = (
                        (installment - 1) * 30
                    ) + transaction.account.days_to_receive
                    date_obj = datetime.strptime(register_date, "%d/%m/%Y").date()
                    date_obj += timedelta(days=days_plus)

                    if transaction.expected_date != date_obj:
                        transaction.expected_date = date_obj
                        transaction.save()
                        self.stdout.write(
                            f"Transação {cod_id_omie} atualizada: expected_date={date_obj}"
                        )
            else:
                self.stdout.write(f"Erro ao consultar cod_id_omie: {cod_id_omie}")

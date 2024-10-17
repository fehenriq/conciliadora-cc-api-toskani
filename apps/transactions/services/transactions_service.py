from django.utils import timezone

from apps.transactions.models import Transaction


class TransactionService:
    def get_all_transactions(self):
        return Transaction.objects.select_related(
            "account__omie_account_origin", "account__omie_account_destiny"
        )

    def list_transactions(self, **kwargs) -> dict:
        transactions = self.get_all_transactions()
        total = transactions.count()
        data = {"total": total, "transactions": transactions}
        return data

    def check_late_bills(self) -> str:
        transactions = Transaction.objects.filter(
            received_value__isnull=True, expected_date__lt=timezone.now().date()
        )

        if transactions:
            transactions.update(status="Pagamento em atraso")

        return "Success"

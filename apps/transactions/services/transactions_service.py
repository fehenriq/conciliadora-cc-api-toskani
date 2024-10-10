from apps.transactions.models import Transaction


class TransactionService:
    def get_all_transactions(self):
        return Transaction.objects.all()

    def list_transactions(self, **kwargs) -> dict:
        transactions = self.get_all_transactions()
        total = transactions.count()
        data = {"total": total, "transactions": transactions}
        return data

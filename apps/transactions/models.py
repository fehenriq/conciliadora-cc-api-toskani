from uuid import uuid4

from django.db import models

from apps.accounts.models import Account


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cod_id_omie = models.BigIntegerField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    tid = models.CharField(max_length=50)
    expected_value = models.FloatField()
    fee = models.FloatField()
    balance = models.FloatField()
    expected_date = models.DateField()
    accounts_receivable_note = models.TextField(blank=True, null=True)
    document_type = models.CharField(
        max_length=50,
        choices=[("DEBIT", "Debit"), ("CREDIT", "Credit"), ("PIX", "Pix")],
    )
    installment = models.CharField(max_length=255, blank=True, null=True)

    received_value = models.FloatField(blank=True, null=True)
    acquirer_fee = models.FloatField(blank=True, null=True)
    value_difference = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"TID {str(self.tid)} - Installment {self.installment}"

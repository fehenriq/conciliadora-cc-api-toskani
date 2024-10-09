from uuid import uuid4

from django.db import models


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account_number = models.CharField(max_length=50)
    acquirer = models.CharField(max_length=50)
    settle = models.BooleanField()
    days_to_receive = models.IntegerField()

    def __str__(self):
        return f"Account {self.account_number} - {self.acquirer}"


class Installment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(
        Account, related_name="installments", on_delete=models.CASCADE
    )
    installment_number = models.IntegerField()
    fee = models.FloatField()

    def __str__(self):
        return f"Installment {self.installment_number} - Fee {self.fee}%"

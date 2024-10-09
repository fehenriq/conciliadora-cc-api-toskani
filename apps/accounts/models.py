from uuid import uuid4

from django.db import models


class OmieAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    omie_id = models.BigIntegerField()
    account_number = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f"Account {self.account_number} - {self.description}"


class Account(models.Model):
    ACQUIRER_CHOICES = [
        ("PAGAR.ME", "Pagar.me"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    omie_account = models.ForeignKey(
        OmieAccount, on_delete=models.CASCADE, null=True, blank=True
    )
    acquirer = models.CharField(max_length=50, choices=ACQUIRER_CHOICES)
    settle = models.BooleanField()
    days_to_receive = models.IntegerField()

    def __str__(self):
        return f"Account {self.omie_account.account_number} - {self.acquirer}"


class Installment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(
        Account, related_name="installments", on_delete=models.CASCADE
    )
    installment_number = models.IntegerField()
    fee = models.FloatField()

    def __str__(self):
        return f"Installment {self.installment_number} - Fee {self.fee}%"

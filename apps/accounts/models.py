from uuid import uuid4

from django.db import models


class OmieAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    omie_id = models.BigIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"Omie Account {str(self.omie_id)} - {self.description}"


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    omie_account_origin = models.ForeignKey(
        OmieAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="origin",
    )
    omie_account_destiny = models.ForeignKey(
        OmieAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="destiny",
    )
    settle = models.BooleanField()
    days_to_receive = models.IntegerField()

    def __str__(self):
        return f"Account {str(self.id)}"


class Installment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    account = models.ForeignKey(
        Account, related_name="installments", on_delete=models.CASCADE
    )
    installment_number = models.IntegerField()
    fee = models.FloatField()

    def __str__(self):
        return f"Installment {self.installment_number} - Fee {self.fee}%"

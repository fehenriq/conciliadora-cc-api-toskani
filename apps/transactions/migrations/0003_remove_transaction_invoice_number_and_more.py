# Generated by Django 4.2.14 on 2024-10-10 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0002_remove_transaction_account_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="invoice_number",
        ),
        migrations.AlterField(
            model_name="transaction",
            name="cod_id_omie",
            field=models.BigIntegerField(),
        ),
    ]

# Generated by Django 4.2.14 on 2024-10-10 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="account_name",
        ),
    ]

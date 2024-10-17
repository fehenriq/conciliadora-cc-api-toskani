from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "cod_id_omie",
        "account",
        "document_type",
        "tid",
        "expected_value",
        "received_value",
        "value_difference",
        "status",
        "expected_date",
    )
    list_filter = ("document_type", "status", "expected_date")
    search_fields = ("cod_id_omie", "tid", "account__omie_account__account_number")
    readonly_fields = ("value_difference", "alert")

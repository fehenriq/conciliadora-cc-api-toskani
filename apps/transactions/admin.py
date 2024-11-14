from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "cod_id_omie",
        "document_type",
        "omie_receipt_releasead",
        "omie_fee_launched",
        "omie_value_transferred",
        "tid",
        "installment",
        "expected_value",
        "received_value",
        "acquirer_fee",
        "value_difference",
        "status",
        "expected_date",
    )
    list_filter = (
        "document_type",
        "status",
        "expected_date",
        "omie_receipt_releasead",
        "omie_fee_launched",
        "omie_value_transferred",
    )
    search_fields = ("cod_id_omie", "tid")
    readonly_fields = ("value_difference", "received_value")

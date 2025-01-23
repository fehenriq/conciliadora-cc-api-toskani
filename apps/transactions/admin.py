from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "cod_id_omie",
        "acquirer_fee",
        "document_type",
        "omie_receipt_releasead",
        "omie_fee_launched",
        "omie_value_transferred",
        "tid",
        "installment",
        "status",
        "expected_date",
    )
    list_filter = (
        "document_type",
        "acquirer_fee",
        "status",
        "expected_date",
        "omie_receipt_releasead",
        "omie_fee_launched",
        "omie_value_transferred",
    )
    search_fields = ("cod_id_omie", "tid")
    readonly_fields = ("value_difference", "received_value")
    list_per_page = 250

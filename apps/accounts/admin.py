from django.contrib import admin

from .models import Account, Installment, OmieAccount


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1


@admin.register(OmieAccount)
class OmieAccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "description", "omie_id")
    search_fields = ("account_number", "description", "omie_id")


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("omie_account", "acquirer", "settle", "days_to_receive")
    list_filter = ("acquirer", "settle")
    search_fields = ("omie_account__account_number", "acquirer")
    inlines = [InstallmentInline]


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ("account", "installment_number", "fee")
    list_filter = ("installment_number",)
    search_fields = ("account__omie_account__account_number", "installment_number")

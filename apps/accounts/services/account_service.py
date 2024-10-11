import uuid
from http import HTTPStatus

from ninja.errors import HttpError

from apps.accounts.models import Account, Installment, OmieAccount
from apps.accounts.schema import (
    AccountInputSchema,
    AccountUpdateSchema,
    InstallmentInputSchema,
    InstallmentUpdateSchema,
)


class AccountService:
    def get_all_accounts(self):
        return Account.objects.all()

    def get_all_omie_accounts(self):
        return OmieAccount.objects.all()

    def get_account_by_id(self, account_id: uuid.UUID) -> Account:
        return Account.objects.filter(id=account_id).first()

    def get_omie_account_by_id(self, omie_account_id: uuid.UUID) -> OmieAccount:
        return OmieAccount.objects.filter(id=omie_account_id).first()

    def get_installment_by_account_and_number(
        self, account: Account, installment_number: int
    ) -> Installment:
        return Installment.objects.filter(
            account=account, installment_number=installment_number
        ).first()

    def list_accounts(self) -> dict:
        accounts = self.get_all_accounts()
        total = accounts.count()
        data = {"total": total, "accounts": accounts}
        return data

    def get_account(self, account_id: uuid.UUID) -> Account:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")
        return account

    def create_account(self, input_data: AccountInputSchema) -> Account:
        if not (omie_account := self.get_omie_account_by_id(input_data.omie_account)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta Omie não encontrada")

        account = Account.objects.create(
            omie_account=omie_account,
            acquirer=input_data.acquirer,
            settle=input_data.settle,
            days_to_receive=input_data.days_to_receive,
        )

        for installment_data in input_data.installments:
            Installment.objects.create(
                account=account,
                installment_number=installment_data.installment_number,
                fee=installment_data.fee,
            )

        return account

    def update_account(
        self, account_id: uuid.UUID, input_data: AccountUpdateSchema
    ) -> Account:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")

        for attr, value in input_data.model_dump(
            exclude_defaults=True, exclude_unset=True
        ).items():
            if attr == "omie_account":
                if not (value := self.get_omie_account_by_id(input_data.omie_account)):
                    raise HttpError(HTTPStatus.NOT_FOUND, "Conta Omie não encontrada")

            setattr(account, attr, value)

        account.save()
        return account

    def add_installments(
        self, account_id: uuid.UUID, installments: list[InstallmentInputSchema]
    ) -> Account:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")

        for installment_data in installments:
            Installment.objects.create(
                account=account,
                installment_number=installment_data.installment_number,
                fee=installment_data.fee,
            )

        return account

    def update_installment(
        self,
        account_id: uuid.UUID,
        installment_number: int,
        input_data: InstallmentUpdateSchema,
    ) -> Account:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")

        if not (
            installment := self.get_installment_by_account_and_number(
                account, installment_number
            )
        ):
            raise HttpError(HTTPStatus.NOT_FOUND, "Parcela não encontrada")

        for attr, value in input_data.model_dump(
            exclude_defaults=True, exclude_unset=True
        ).items():
            setattr(installment, attr, value)

        installment.save()

        return account

    def list_omie_accounts(self) -> dict:
        accounts = self.get_all_omie_accounts()
        total = accounts.count()
        data = {"total": total, "omie_accounts": accounts}
        return data

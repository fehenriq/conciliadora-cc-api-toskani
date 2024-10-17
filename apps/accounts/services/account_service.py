import uuid
from http import HTTPStatus

from django.http import JsonResponse
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

    def create_account(self, input_data: AccountInputSchema) -> Account:
        if not (
            omie_account_origin := self.get_omie_account_by_id(
                input_data.omie_account_origin
            )
        ):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta Omie origem não encontrada")

        if Account.objects.filter(omie_account_origin=omie_account_origin).exists():
            raise HttpError(
                HTTPStatus.CONFLICT, "Já existe uma conta com essa Conta Omie"
            )

        omie_account_destiny = None
        if input_data.omie_account_destiny:
            omie_account_destiny = self.get_omie_account_by_id(
                input_data.omie_account_destiny
            )
            if not omie_account_destiny:
                raise HttpError(
                    HTTPStatus.NOT_FOUND, "Conta Omie destino não encontrada"
                )

        account = Account.objects.create(
            omie_account_origin=omie_account_origin,
            omie_account_destiny=omie_account_destiny,
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
            if attr == "omie_account_origin":
                if not (value := self.get_omie_account_by_id(value)):
                    raise HttpError(
                        HTTPStatus.NOT_FOUND, "Conta Omie origem não encontrada"
                    )

            elif attr == "omie_account_destiny":
                if value:
                    if not (value := self.get_omie_account_by_id(value)):
                        raise HttpError(
                            HTTPStatus.NOT_FOUND, "Conta Omie destino não encontrada"
                        )
                else:
                    value = None

            setattr(account, attr, value)

        account.save()
        return account

    def delete_account(self, account_id: uuid.UUID) -> JsonResponse:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")

        account.delete()

        return JsonResponse({"message": "Conta deletada com sucesso"})

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

        installment.delete()

        return JsonResponse({"message": "Parcela deletada com sucesso"})

    def delete_installment(
        self, account_id: uuid.UUID, installment_number: int
    ) -> JsonResponse:
        if not (account := self.get_account_by_id(account_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Conta não encontrada")

        if not (
            installment := self.get_installment_by_account_and_number(
                account, installment_number
            )
        ):
            raise HttpError(HTTPStatus.NOT_FOUND, "Parcela não encontrada")

        installment.save()

        return account

    def list_omie_accounts(self) -> dict:
        accounts = self.get_all_omie_accounts()
        total = accounts.count()
        data = {"total": total, "omie_accounts": accounts}
        return data

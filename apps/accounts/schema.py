import uuid
from typing import Optional

from ninja import Schema


class InstallmentInputSchema(Schema):
    installment_number: int
    fee: float


class InstallmentSchema(InstallmentInputSchema):
    id: uuid.UUID


class InstallmentUpdateSchema(Schema):
    fee: Optional[float] = None


class OmieAccountSchema(Schema):
    id: uuid.UUID
    omie_id: int
    account_number: str
    description: str


class AccountDashboardSchema(Schema):
    id: uuid.UUID
    omie_account: OmieAccountSchema
    acquirer: str


class AccountSchema(AccountDashboardSchema):
    settle: bool
    days_to_receive: int
    installments: list[InstallmentSchema]


class AccountUpdateSchema(Schema):
    omie_account: Optional[uuid.UUID] = None
    acquirer: Optional[str] = None
    settle: Optional[bool] = None
    days_to_receive: Optional[int] = None


class AccountListSchema(Schema):
    total: int
    accounts: list[AccountSchema]


class AccountInputSchema(Schema):
    omie_account: uuid.UUID
    acquirer: str
    settle: bool
    days_to_receive: int
    installments: list[InstallmentInputSchema]


class OmieAccountListSchema(Schema):
    total: int
    omie_accounts: list[OmieAccountSchema]

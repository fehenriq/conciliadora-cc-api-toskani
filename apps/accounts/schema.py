import uuid
from typing import Optional

from ninja import Schema


class InstallmentSchema(Schema):
    id: uuid.UUID
    installment_number: int
    fee: float


class InstallmentInputSchema(Schema):
    installment_number: int
    fee: float


class InstallmentUpdateSchema(Schema):
    fee: Optional[float] = None


class AccountSchema(Schema):
    id: uuid.UUID
    account_number: str
    acquirer: str
    settle: bool
    days_to_receive: int
    installments: list[InstallmentSchema]


class AccountUpdateSchema(Schema):
    account_number: Optional[str] = None
    acquirer: Optional[str] = None
    settle: Optional[bool] = None
    days_to_receive: Optional[int] = None


class AccountListSchema(Schema):
    total: int
    accounts: list[AccountSchema]


class AccountInputSchema(Schema):
    account_number: str
    acquirer: str
    settle: bool
    days_to_receive: int
    installments: list[InstallmentInputSchema]

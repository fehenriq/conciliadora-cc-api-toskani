import uuid
from datetime import date
from typing import Optional

from ninja import Schema

from apps.accounts.schema import AccountSchema


class TransactionSchema(Schema):
    id: uuid.UUID
    cod_id_omie: int
    account: AccountSchema
    tid: str
    invoice_number: str
    expected_value: float
    fee: float
    balance: float
    expected_date: date
    accounts_receivable_note: Optional[str]
    document_type: str
    received_value: Optional[float]
    value_difference: Optional[float]
    status: Optional[str]
    alert: Optional[str]


class TransactionListSchema(Schema):
    total: int
    transactions: list[TransactionSchema]

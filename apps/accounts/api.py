import uuid

from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import (
    AccountInputSchema,
    AccountListSchema,
    AccountSchema,
    AccountUpdateSchema,
    InstallmentInputSchema,
    InstallmentUpdateSchema,
    OmieAccountListSchema,
)
from .services.account_service import AccountService
from .services.omie_service import get_omie_accounts

account_router = Router(auth=JWTAuth())
service = AccountService()


@account_router.post("/", response=AccountSchema)
def create_account(request, payload: AccountInputSchema):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.create_account(payload)


@account_router.get("/", response=AccountListSchema)
def list_accounts(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.list_accounts(**request.GET.dict())


@account_router.get("/{account_id}/", response=AccountSchema)
def get_account(request, account_id: uuid.UUID):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.get_account(account_id)


@account_router.patch("/{account_id}/", response=AccountSchema)
def update_account(request, account_id: uuid.UUID, payload: AccountUpdateSchema):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.update_account(account_id, payload)


@account_router.post("/{account_id}/installments/", response=AccountSchema)
def add_installments(
    request, account_id: uuid.UUID, installments: list[InstallmentInputSchema]
):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.add_installments(account_id, installments)


@account_router.patch(
    "/{account_id}/installments/{installment_number}", response=AccountSchema
)
def update_installment(
    request,
    account_id: uuid.UUID,
    installment_number: int,
    payload: InstallmentUpdateSchema,
):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.update_installment(account_id, installment_number, payload)


@account_router.get("/omie", response=OmieAccountListSchema)
def list_omie_accounts(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.list_omie_accounts(**request.GET.dict())


@account_router.post("/omie", response=str)
def sync_omie(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return get_omie_accounts()

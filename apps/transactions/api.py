import uuid

from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import TransactionListSchema
from .services.transactions_service import TransactionService
from .services.omie_service import create_transactions

transaction_router = Router(auth=JWTAuth())
service = TransactionService()


@transaction_router.get("", response=TransactionListSchema)
def list_transactions(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.list_transactions(**request.GET.dict())


@transaction_router.post("/omie", response=str)
def sync_omie(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return create_transactions()

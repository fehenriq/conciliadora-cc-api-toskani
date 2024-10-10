import uuid

from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import TransactionListSchema
from .services.transactions_service import TransactionService

transaction_router = Router(auth=JWTAuth())
service = TransactionService()


@transaction_router.get("", response=TransactionListSchema)
def list_transactions(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.list_transactions(**request.GET.dict())

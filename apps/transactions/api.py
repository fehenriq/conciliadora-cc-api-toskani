from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import TransactionListSchema
from .services.omie_service import OmieService
from .services.toskani_service import ToskaniService
from .services.transactions_service import TransactionService

transaction_router = Router(auth=JWTAuth())
transaction_service = TransactionService()
omie_service = OmieService()
toskani_service = ToskaniService()


@transaction_router.get("", response=TransactionListSchema)
def list_transactions(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return transaction_service.list_transactions(**request.GET.dict())


@transaction_router.patch("/verify-dates", response=str)
def check_late_bills(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return transaction_service.check_late_bills()


@transaction_router.post("/omie", response=str)
def sync_omie(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return omie_service.create_transactions()


@transaction_router.patch("/toskani", response=str)
def sync_toskani(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return toskani_service.consult_toskani()

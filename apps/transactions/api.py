from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import TransactionListSchema
from .services.omie_service import OmieService
from .services.pagarme_service import PagarmeService
from .services.transactions_service import TransactionService

transaction_router = Router(auth=JWTAuth())
transaction_service = TransactionService()
omie_service = OmieService()
pagarme_service = PagarmeService()


@transaction_router.get("", response=TransactionListSchema)
def list_transactions(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return transaction_service.list_transactions(**request.GET.dict())


@transaction_router.post("/omie", response=str)
def sync_omie(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return omie_service.create_transactions()


@transaction_router.patch("/pagarme", response=str)
def sync_pagarme(request):
    decode_jwt_token(request.headers.get("Authorization"))
    return pagarme_service.consult_pagarme()

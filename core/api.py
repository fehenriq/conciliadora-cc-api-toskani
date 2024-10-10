from ninja import NinjaAPI, Redoc

from apps.accounts.api import account_router
from apps.authentication.api import authentication_router
from apps.transactions.api import transaction_router
from apps.users.api import user_router

api = NinjaAPI(
    csrf=False,
    title="API",
    version="1.0.0",
    description="This is a API to manage data",
)


api.add_router("/auth", authentication_router, tags=["Authentication"])
api.add_router("/users", user_router, tags=["Users"])
api.add_router("/accounts", account_router, tags=["Accounts"])
api.add_router("/transactions", transaction_router, tags=["Transactions"])

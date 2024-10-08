from ninja import NinjaAPI, Redoc

from apps.authentication.api import authentication_router
from apps.users.api import user_router

api = NinjaAPI(
    csrf=False,
    title="API",
    version="1.0.0",
    description="This is a API to manage data",
)


api.add_router("/auth", authentication_router, tags=["Authentication"])
api.add_router("/users", user_router, tags=["Users"])

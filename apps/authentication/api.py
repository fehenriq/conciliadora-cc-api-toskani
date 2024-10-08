from ninja import Router

from apps.authentication.schema import LoginSchemaInput, UserOutputSchema
from apps.authentication.service import AuthenticationService

from utils.jwt import JWTAuth, decode_jwt_token

authentication_router = Router(auth=JWTAuth())

service = AuthenticationService()


@authentication_router.post("/login", auth=None)
def auth_login(request, input_schema: LoginSchemaInput):
    """Autenticação de usuário"""
    return service.auth_login(request, input_schema)


@authentication_router.get("/me", response=UserOutputSchema)
def auth_me(request):
    """Retorna o usuário autenticado"""
    token = decode_jwt_token(request.headers.get("Authorization"))
    return service.get_me(token["user_id"])

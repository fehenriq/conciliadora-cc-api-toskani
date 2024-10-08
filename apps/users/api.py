import uuid

from ninja import Router

from utils.jwt import JWTAuth, decode_jwt_token

from .schema import ChangePasswordSchema, UserSchema
from .service import UserService

user_router = Router(auth=JWTAuth())
service = UserService()


@user_router.get("/{user_id}", response=UserSchema)
def retrieve_user(request, user_id: uuid.UUID):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.get_user(user_id)


@user_router.post("/{user_id}/change-password")
def change_password(request, user_id: uuid.UUID, payload: ChangePasswordSchema):
    decode_jwt_token(request.headers.get("Authorization"))
    return service.change_user_password(user_id, payload)

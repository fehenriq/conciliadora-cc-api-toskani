import uuid
from http import HTTPStatus

from django.contrib.auth import authenticate
from django.http import JsonResponse
from ninja.errors import HttpError

from apps.authentication.schema import LoginSchemaInput
from apps.users.models import CustomUser

from utils.jwt import generate_jwt_token


class AuthenticationService:
    def auth_login(self, request, input_schema: LoginSchemaInput) -> JsonResponse:
        if not (user := CustomUser.objects.filter(email=input_schema.email).first()):
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não cadastrado no sistema")

        user = authenticate(
            request, email=input_schema.email, password=input_schema.password
        )

        if not user:
            raise HttpError(
                HTTPStatus.UNAUTHORIZED, "Senha incorreta, verifique e tente novamente"
            )

        token = generate_jwt_token(user=user)

        return JsonResponse(
            data={"access_token": token},
            status=HTTPStatus.OK,
        )

    def get_me(self, user_id: uuid.UUID) -> CustomUser:
        if not (user := CustomUser.objects.filter(id=user_id).first()):
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não encontrado")
        return user

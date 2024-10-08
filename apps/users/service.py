import re
import uuid
from http import HTTPStatus

from django.http import JsonResponse
from ninja.errors import HttpError

from utils.validation import ValidationService

from .models import CustomUser
from .schema import ChangePasswordSchema, UserSchema


class UserService:
    @property
    def validation_service(self):
        return ValidationService()

    @staticmethod
    def build_user_response(user: CustomUser):
        user_data = UserSchema(id=user.id, email=user.email, name=user.name)

        return user_data

    @staticmethod
    def validate_password(password: str) -> bool:
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[@$!%*?&#]", password):
            return False
        return True

    def get_user_by_id(self, user_id: uuid.UUID) -> CustomUser:
        return CustomUser.objects.get(pk=user_id)

    def get_user(self, user_id: uuid.UUID) -> UserSchema:
        if not (user := self.get_user_by_id(user_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não encontrado")

        user_data = self.build_user_response(user=user)

        return user_data

    def change_user_password(
        self, user_id: uuid.UUID, payload: ChangePasswordSchema
    ) -> JsonResponse:
        if not (user := self.get_user_by_id(user_id)):
            raise HttpError(HTTPStatus.NOT_FOUND, "Usuário não encontrado")

        self._validate_passwords(payload)

        user.set_password(payload.new_password)
        user.save()

        return JsonResponse(
            {"success": "Senha alterada com sucesso"}, status=HTTPStatus.OK
        )

    def _validate_passwords(self, payload: ChangePasswordSchema) -> None:
        if payload.new_password != payload.confirm_password:
            raise HttpError(HTTPStatus.BAD_REQUEST, "As senhas não coincidem")

        if not self.validate_password(payload.new_password):
            raise HttpError(
                HTTPStatus.BAD_REQUEST,
                "A nova senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e símbolos.",
            )

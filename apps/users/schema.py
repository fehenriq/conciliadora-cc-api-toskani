import uuid

from ninja import Schema


class UserSchema(Schema):
    id: uuid.UUID
    email: str
    name: str


class ChangePasswordSchema(Schema):
    new_password: str
    confirm_password: str

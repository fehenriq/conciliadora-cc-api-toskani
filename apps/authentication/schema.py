import uuid

from ninja import Schema


class LoginSchemaInput(Schema):
    email: str
    password: str


class UserOutputSchema(Schema):
    id: uuid.UUID
    email: str

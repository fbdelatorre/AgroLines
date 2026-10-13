from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

Role = Literal["administrator", "editor", "operator", "viewer"]


class Registration(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("name")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Nome obrigatório")
        return value.strip()


class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenInput(BaseModel):
    token: str = Field(min_length=20, max_length=256)


class Recovery(BaseModel):
    email: EmailStr


class Reset(TokenInput):
    password: str = Field(min_length=12, max_length=128)


class Named(BaseModel):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Nome obrigatório")
        return value.strip()


class Scope(BaseModel):
    role: Role
    season_id: str | None = Field(default=None, min_length=36, max_length=36)
    operation_id: str | None = Field(default=None, min_length=36, max_length=36)

    @model_validator(mode="after")
    def hierarchy(self):
        if self.operation_id and not self.season_id:
            raise ValueError("Operação exige safra")
        if self.role == "administrator" and self.season_id:
            raise ValueError("Administrador exige escopo de fazenda inteira")
        return self


class InviteInput(BaseModel):
    user_id: str | None = Field(default=None, min_length=36, max_length=36)
    email: EmailStr | None = None
    scopes: list[Scope] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def recipient(self):
        if bool(self.user_id) == bool(self.email):
            raise ValueError("Informe e-mail ou identificador, não ambos")
        return self


class Transfer(BaseModel):
    user_id: str = Field(min_length=1, max_length=36)

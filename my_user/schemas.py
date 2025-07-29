from pydantic import BaseModel
from ninja import Field, Schema


class UserCreate(Schema):
    username: str = Field(..., title="User name", description="Unique username")
    first_name: str = Field(..., title="First Name")
    last_name: str = Field(..., title="Last Name")
    password: str = Field(..., title="Password", min_length=6)


class UserUpdate(Schema):
    username: str = Field(None, title="User name", description="Unique username")
    first_name: str = Field(None, title="First Name")
    last_name: str = Field(None, title="Last Name")
    password: str = Field(None, title="Password", min_length=6)


class UserOut(Schema):
    username: str
    first_name: str
    last_name: str
    role: str


class TokenOut(BaseModel):
    access: str
    refresh: str


class TokenRefreshIn(BaseModel):
    refresh: str

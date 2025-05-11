from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"
    owner = "owner"
    kitchen_staff = "kitchen_staff"
    driver = "driver"

class UserCreate(SQLModel):
    username: str
    password: str = Field(min_length=3)
    email: EmailStr
    role: UserRole = UserRole.customer

class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str
    email: EmailStr = Field(unique=True)
    role: UserRole = Field(default=UserRole.customer)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
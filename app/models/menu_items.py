from sqlmodel import SQLModel, Field
from decimal import Decimal
from datetime import datetime

class MenuItemCreate(SQLModel):
    name: str
    description: str | None = None
    price: Decimal = Field(max_digits=12, decimal_places=3, ge=0)
    is_available: bool | None = True

class MenuItemUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: Decimal  | None = Field(default=None, max_digits=12, decimal_places=3, ge=0)
    is_available: bool | None = None

class MenuItemPublic(SQLModel):
    id: int
    branch_id: int
    name: str
    description: str | None
    price: Decimal = Field(max_digits=12, decimal_places=3, ge=0)
    is_available: bool
    created_at: datetime
    updated_at: datetime | None

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"

    id: int = Field(default=None, primary_key=True)
    branch_id: int = Field(foreign_key="branches.id")
    name: str
    description: str | None = None
    price: Decimal = Field(max_digits=12, decimal_places=3, ge=0)
    is_available: bool | None = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
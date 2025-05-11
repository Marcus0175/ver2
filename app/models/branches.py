from sqlmodel import SQLModel, Field
from decimal import Decimal
from datetime import datetime

class BranchCreate(SQLModel):
    name: str
    address: str
    latitude: Decimal = Field(max_digits=9, decimal_places=6)
    longitude: Decimal = Field(max_digits=9, decimal_places=6)

class BranchUpdate(SQLModel):
    name: str = None
    address: str = None
    latitude: Decimal = None
    longitude: Decimal = None

class BranchPublic(SQLModel):
    id: int
    name: str
    address: str
    latitude: Decimal = Field(max_digits=9, decimal_places=6)
    longitude: Decimal = Field(max_digits=9, decimal_places=6)
    created_at: datetime
    updated_at: datetime | None

class Branch(SQLModel, table=True):
    __tablename__ = "branches"

    id: int = Field(default=None, primary_key=True)
    name: str
    address: str
    latitude: Decimal = Field(max_digits=9, decimal_places=6)
    longitude: Decimal = Field(max_digits=9, decimal_places=6)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
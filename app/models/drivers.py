from sqlmodel import SQLModel, Field
from datetime import datetime

class DriverCreate(SQLModel):
    user_id: int
    branch_id: int

class DriverPublic(SQLModel):
    id: int
    user_id: int
    branch_id: int
    is_active: bool
    created_at: datetime

class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    branch_id: int = Field(foreign_key="branches.id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
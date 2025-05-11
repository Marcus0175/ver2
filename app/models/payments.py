from sqlmodel import SQLModel, Field
from decimal import Decimal
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    e_wallet = "e_wallet"
    credit_card = "credit_card"
    bank_transfer = "bank_transfer"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"

class PaymentPublic(SQLModel):
    id: int
    order_id: int
    customer_id: int
    total_order_amount: Decimal
    shipping_fee: Decimal 
    total_amount: Decimal
    method: PaymentMethod | None
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime | None

class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    id: int = Field(default=None, primary_key=True)
    order_id: int = Field(unique=True, foreign_key="orders.id")
    customer_id: int = Field(foreign_key="users.id")
    total_order_amount: Decimal = Field(max_digits=12, decimal_places=3)
    shipping_fee: Decimal = Field(max_digits=12, decimal_places=3)
    total_amount: Decimal = Field(max_digits=12, decimal_places=3)
    method: PaymentMethod | None = None
    status: PaymentStatus = PaymentStatus.pending
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
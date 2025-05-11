from sqlmodel import SQLModel, Field, Relationship
from decimal import Decimal
from datetime import datetime
from enum import Enum

from ..models.orders import Order, OrderCreate, OrderPublic, OrderPublicForCustomer

class OrderItemStatus(str, Enum):
    preparing = "preparing"
    ready = "ready"
    canceled = "canceled"

class OrderItemCreate(SQLModel):
    menu_item_id: int
    quanity: int = Field(default=1, ge=1)

OrderCreate.model_rebuild()

class OrderItemPublicV1(SQLModel):
    id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    ks_id: int | None
    status: OrderItemStatus | None
    created_at: datetime
    updated_at: datetime | None

class OrderItemPublicV2(SQLModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price: Decimal
    ks_id: int | None
    status: OrderItemStatus | None
    created_at: datetime
    updated_at: datetime | None

OrderPublic.model_rebuild()
OrderPublicForCustomer.model_rebuild()

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: int = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    menu_item_id: int = Field(foreign_key="menu_items.id")
    quantity: int = Field(default=1, ge=1)
    price: Decimal = Field(default=0, max_digits=12, decimal_places=3, ge=0)
    ks_id: int | None = Field(default=None, foreign_key="kitchen_staffs.id")
    status: OrderItemStatus | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    order: Order = Relationship(back_populates="order_items")

Order.model_rebuild()
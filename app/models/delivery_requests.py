from sqlmodel import SQLModel, Field
from decimal import Decimal
from datetime import datetime
from enum import Enum

class DeliveryRequestStatus(str, Enum):
    pending = "pending"
    delivering = "delivering"
    delivered = "delivered"

class DeliveryRequestPublic(SQLModel):
    id: int
    order_id: int
    branch_id: int
    customer_id: int
    driver_id: int | None
    status: DeliveryRequestStatus
    dropoff_lat: Decimal
    dropoff_lon: Decimal
    shipping_fee: Decimal 
    is_forced_assignment: bool
    is_active: bool
    created_at: datetime
    assigned_at: datetime | None
    accepted_at: datetime | None
    picked_up_at: datetime | None
    delivered_at: datetime | None
    is_confirmed_by_customer: bool
    is_confirmed_by_driver: bool

class DeliveryRequestForCustomer(SQLModel):
    id: int
    order_id: int
    branch_id: int
    customer_id: int
    driver_id: int | None
    status: DeliveryRequestStatus
    dropoff_lat: Decimal
    dropoff_lon: Decimal
    created_at: datetime
    assigned_at: datetime | None
    accepted_at: datetime | None
    picked_up_at: datetime | None
    delivered_at: datetime | None
    is_confirmed_by_customer: bool

class DeliveryRequest(SQLModel, table=True):
    __tablename__ = "delivery_requests"
    id: int = Field(default=None, primary_key=True)
    order_id: int = Field(unique=True, foreign_key="orders.id")
    branch_id: int = Field(foreign_key="branches.id")
    customer_id: int = Field(foreign_key="users.id")
    driver_id: int | None = Field(foreign_key="drivers.id")
    status: DeliveryRequestStatus = DeliveryRequestStatus.pending
    dropoff_lat: Decimal = Field(max_digits=9, decimal_places=6)
    dropoff_lon: Decimal = Field(max_digits=9, decimal_places=6)
    distance_km: Decimal = Field(max_digits=5, decimal_places=3)
    shipping_fee: Decimal = Field(default=0, max_digits=12, decimal_places=3, ge=0)
    is_forced_assignment: bool = False
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    assigned_at: datetime | None = None
    accepted_at: datetime | None = None
    picked_up_at: datetime | None = None
    delivered_at: datetime | None = None
    is_confirmed_by_customer: bool = False
    is_confirmed_by_driver: bool = False
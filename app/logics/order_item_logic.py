from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime

from . import dr_logic, ks_logic, order_logic
from ..models.users import User, UserRole
from ..models.orders import Order, OrderStatus
from ..models.order_items import OrderItem, OrderItemStatus
from ..websocket import events
import asyncio
from ..background_tasks import force_assign_driver_if_unclaimed

def get_order_item_by_id(session: Session, id: int) -> OrderItem:
    order_item_db = session.get(OrderItem, id)
    if not order_item_db:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return order_item_db

def are_all_order_items_ready(order_db: Order):
    for order_item in order_db.order_items:
        if order_item.status is OrderItemStatus.preparing:
            return False
    return True

def get_order_items_for_ks(
    session: Session, user_id: int
) -> list[OrderItem]:
    ks_db = ks_logic.get_ks_by_user_id(session, user_id)
    stmt = (
        select(OrderItem)
        .join(Order)
        .where(OrderItem.ks_id == ks_db.id,
                Order.status == OrderStatus.preparing.value)
        )
    return session.exec(stmt).all()

async def ready_order_item(session: Session, id: int, user_id: int) -> OrderItem:
    ks_db = ks_logic.get_ks_by_user_id(session, user_id)
    order_item_db = get_order_item_by_id(session, id)

    # Check the involvement
    if order_item_db.ks_id != ks_db.id:
        raise HTTPException(status_code=403, detail="You are not allowed to modify this order item")
    
    order_item_db.status = OrderItemStatus.ready
    order_item_db.updated_at = datetime.now()
    session.add(order_item_db)
    session.commit()

    order_db = order_item_db.order
    if are_all_order_items_ready(order_db):
        order_logic.ready_for_delivering_order(session, order_db)
        dr_db = dr_logic.toggle_active_dr(session, order_db.id, is_active=True)

        await events.broadcast_to_drivers_for_branch(
            dr_db.branch_id, 
            {
                "event": "delivery_request_active",
                "data": dr_db.model_dump(mode="json")
            }
        )

        # Waiting for acceptance of drivers in this branch
        # If not, do auto-assignement
        asyncio.create_task(force_assign_driver_if_unclaimed(dr_db.id))

    session.refresh(order_item_db)
    return order_item_db
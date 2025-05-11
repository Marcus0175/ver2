from fastapi import HTTPException
from sqlmodel import Session, select, func, col
from datetime import datetime

from ..logics import user_logic, branch_logic
from ..models.users import User, UserRole
from ..models.kitchen_staffs import KitchenStaffCreate, KitchenStaff
from ..models.order_items import OrderItem, OrderItemStatus
from ..websocket.connection_manager import manager

def assign_ks_to_branch(session: Session, cur_act_user: User, ks: KitchenStaffCreate) -> KitchenStaff:
    
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])

    user_db: User = user_logic.get_user_by_id(session, ks.user_id)
    if user_db.role is not UserRole.kitchen_staff:
        raise HTTPException(status_code=400, detail="User's role is not kitchen_staff")
    branch_logic.get_branch_by_id(session, ks.branch_id)

    ks_db = session.exec(
        select(KitchenStaff)
        .where(KitchenStaff.user_id == ks.user_id, KitchenStaff.branch_id == ks.branch_id)
    ).first()

    if ks_db:
        raise HTTPException(status_code=400, detail="Assignment of kitchen staff already existed")
    
    ks_db = KitchenStaff.model_validate(ks)
    session.add(ks_db)
    session.commit()
    session.refresh(ks_db)
    return ks_db

def get_ks_by_id(session: Session, id: int):
    ks_db = session.get(KitchenStaff, id)
    if not ks_db:
        raise HTTPException(status_code=404, detail="Kitchen staff not found")
    return ks_db

def get_ks_by_user_id(session: Session, user_id: int) -> KitchenStaff:
    stmt = select(KitchenStaff).where(KitchenStaff.user_id == user_id)
    ks_db = session.exec(stmt).first()
    if not ks_db:
        raise HTTPException(status_code=404, detail="Kitchen Staff not found")
    return ks_db

def toggle_active_ks(
    session: Session,
    cur_act_user: User,
    id: int,
    is_active: bool = True
) -> KitchenStaff:
    
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])
    ks_db = get_ks_by_id(session, id)

    ks_db.is_active = is_active
    session.add(ks_db)
    session.commit()
    session.refresh(ks_db)
    return ks_db

def get_kss_by_branch_id(
    session: Session,  
    branch_id: int,
    is_active: bool | None = None
) -> list[KitchenStaff]:
    
    statement = select(KitchenStaff).where(KitchenStaff.branch_id == branch_id)
    if is_active is not None:
        statement = statement.where(KitchenStaff.is_active == is_active)

    kss_db = session.exec(statement).all()

    return kss_db

def count_order_items_for_ks(session: Session, ks_id: int) -> int:
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())

    stmt = (
        select(func.count(OrderItem.id))
        .where(
            OrderItem.ks_id == ks_id,
            OrderItem.created_at >= start_of_day,
            col(OrderItem.status).in_([OrderItemStatus.preparing, OrderItemStatus.ready])
        )
    )
    return session.exec(stmt).one()

def get_least_busy_ks(session: Session, branch_id: int) -> KitchenStaff:
    ks_list = get_kss_by_branch_id(session, branch_id, True)

    if not ks_list:
        raise HTTPException(status_code=404, detail="There are not active kitchen staffs")
    
    ks_load = [
        (ks, count_order_items_for_ks(session, ks.id))
        for ks in ks_list
    ]

    return min(ks_load, key=lambda x: x[1])[0]

async def assign_kss_to_order_items(session: Session, branch_id: int, order_items: list[OrderItem]):
    # This function will be triggered by system
    for order_item in order_items:
        least_busy_ks = get_least_busy_ks(session, branch_id)

        # Fill ks_id of order_item
        order_item.ks_id = least_busy_ks.id
        order_item.status = OrderItemStatus.preparing
        order_item.updated_at = datetime.now()
        session.add(order_item)

        # Notify to specific kitchen staff
        await manager.send_to_user(
            least_busy_ks.user_id, 
            {
                "event": "order_item_assigned",
                "data": order_item.model_dump(mode="json")
            }
        )
    session.commit()

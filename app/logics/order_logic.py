from fastapi import HTTPException, status
from sqlmodel import Session, select, col
from datetime import timedelta, datetime

from ..helpers import calculate_distance_km, calculate_shipping_fee
from ..logics  import user_logic, menu_item_logic, branch_logic, dr_logic, payment_logic, ks_logic
from ..models.users import User, UserRole
from ..models.branches import Branch
from ..models.orders import OrderCreate, Order, OrderStatus, OrderPublicForCustomer
from ..models.order_items import OrderItem
from ..models.delivery_requests import DeliveryRequest
from ..models.payments import Payment
from ..config import get_settings

settings = get_settings()

async def create_new_order(session: Session, cur_act_user: User, order: OrderCreate) -> Order:
    user_logic.require_role(cur_act_user, [UserRole.customer])

    ids = [_.menu_item_id for _ in order.items]
    prices = menu_item_logic.get_menu_item_prices_by_ids(session, ids)

    order_items = []
    total_amount = 0
    for i in range(len(order.items)):
        # Create order items for order
        order_items.append(
            OrderItem(
                menu_item_id=order.items[i].menu_item_id, 
                quantity=order.items[i].quanity,
                price=prices[i]
            )
        )
        # Calculate total_amount of order
        total_amount += float(order.items[i].quanity * prices[i])
    
    # Calculate distance
    branch_db = branch_logic.get_branch_by_id(session, order.branch_id)
    pickup_lon, pickup_lat = branch_db.longitude, branch_db.latitude
    distance_km = await calculate_distance_km(pickup_lon, pickup_lat, order.dropoff_lon, order.dropoff_lat)

    # Add order to DB
    order_db = Order(
        customer_id=cur_act_user.id,
        branch_id=order.branch_id,
        total_amount=total_amount,
        order_items=order_items
    )

    session.add(order_db)
    session.commit()

    # Calculae shipping fee
    shipping_fee = 0.0
    shipping_fee = calculate_shipping_fee(distance_km)

    # Add delivery request to DB, shipping_fee in this table is the commision for driver
    # customers don't see shipping_fee field in this table
    dr_db = DeliveryRequest(
        order_id=order_db.id, 
        branch_id=order.branch_id,
        customer_id=cur_act_user.id,
        dropoff_lon=order.dropoff_lon,
        dropoff_lat=order.dropoff_lat,
        distance_km=distance_km,
        shipping_fee=shipping_fee
    )
    dr_logic.create_delivery_request(session, dr_db)

    # Set shipping_fee is free when it exceeds the threshold
    customer_shipping_fee = 0 if shipping_fee >= settings.FREE_SHIPPING_THRESHOLD else shipping_fee
    payment_db = Payment(
        order_id=order_db.id,
        customer_id=cur_act_user.id,
        total_order_amount = total_amount,
        shipping_fee=customer_shipping_fee,
        total_amount=customer_shipping_fee + total_amount
    )

    # Add payment to DB
    payment_logic.create_payment(session, payment_db)

    session.refresh(order_db)
    return order_db

def get_enrich_orders_by_customer_id(
    session: Session, customer_id: int, offset: int, limit: int
) -> list[OrderPublicForCustomer]:
    
    stmt = (
        select(Order, col(Branch.name))
        .select_from(Order)
        .join(Branch, Order.branch_id == Branch.id)
        .where(Order.customer_id == customer_id)
        .offset(offset).limit(limit)
    )
    
    results = session.exec(stmt).all()

    return [
        OrderPublicForCustomer(
            id=order.id,
            branch_id=order.branch_id,
            branch_name = branch_name,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            order_items=order.order_items
        )
        for order, branch_name in results
    ]

def get_order_by_id(session: Session, order_id: int) -> Order:
    order_db = session.get(Order, order_id)
    if not order_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_db

def preparing_order(session: Session, order_id: int):
    # This function is triggered by system
    order_db = get_order_by_id(session, order_id)
    order_db.status = OrderStatus.preparing
    order_db.updated_at = datetime.now()
    session.add(order_db)
    session.commit()
    session.refresh(order_db)
    return order_db

def ready_for_delivering_order(session: Session, order_db: Order) -> Order:

    order_db.status = OrderStatus.ready_for_delivery
    order_db.updated_at = datetime.now()
    session.add(order_db)
    session.commit()
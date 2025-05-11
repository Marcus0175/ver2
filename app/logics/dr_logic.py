from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime

from ..logics import driver_logic
from ..models.users import User, UserRole
from ..models.delivery_requests import DeliveryRequest, DeliveryRequestForCustomer, DeliveryRequestPublic, DeliveryRequestStatus
from ..websocket.connection_manager import manager

def create_delivery_request(
    session: Session,
    delivery_request: DeliveryRequest
):
    # This function will be triggered by system, not by any actor
    session.add(delivery_request)
    session.commit()

def get_dr_by_id(session: Session, id: int) -> DeliveryRequest:
    dr_db = session.get(DeliveryRequest, id)
    if not dr_db:
        raise HTTPException(status_code=404, detail="Delivery request not found")
    return dr_db

def get_dr_by_order_id(session: Session, order_id: int):
    dr_db = session.exec(
        select(DeliveryRequest).where(DeliveryRequest.order_id == order_id)
    ).first()
    if not dr_db:
        raise HTTPException(status_code=404, detail="Delivery request not found")
    return dr_db

def toggle_active_dr(session: Session, order_id: int, is_active: bool = True) -> DeliveryRequest:
    dr_db = get_dr_by_order_id(session, order_id)
    dr_db.is_active = is_active
    session.add(dr_db)
    session.commit()
    session.refresh(dr_db)
    return dr_db
    
def get_delivery_requests(session: Session, offset: int, limit: int, is_active: bool=None) -> list[DeliveryRequest]:
    statement = select(DeliveryRequest)
    if is_active is not None:
        statement = statement.where(DeliveryRequest.is_active == is_active)
    return session.exec(statement.offset(offset).limit(limit)).all()

def get_not_accepted_delivery_requests(session: Session, user_id: int, offset: int, limit: int) -> list[DeliveryRequest]:
    driver_db = driver_logic.get_driver_by_user_id(session, user_id)
    
    return session.exec(
        select(DeliveryRequest)
        .where(
            DeliveryRequest.is_active == True,
            DeliveryRequest.driver_id == None,
            DeliveryRequest.branch_id == driver_db.branch_id
        )
        .offset(offset).limit(limit)
    ).all()

def accept_delivery_request(session: Session, id: int, user_id: int) -> DeliveryRequest:
    dr_db = get_dr_by_id(session, id)

    if dr_db.driver_id is not None:
        raise HTTPException(
            status_code=403, 
            detail="This delivery request is assigned/accepted by another driver"
        )

    driver_db = driver_logic.get_driver_by_user_id(session, user_id)

    dr_db.driver_id = driver_db.id
    dr_db.accepted_at = datetime.now()
    session.add(dr_db)
    session.commit()
    session.refresh(dr_db)
    return dr_db

def delivering_delivery_request(session: Session, id: int, user_id: int) -> DeliveryRequest:
    dr_db = get_dr_by_id(session, id)

    driver_db = driver_logic.get_driver_by_user_id(session, user_id)

    if dr_db.driver_id != driver_db.id:
        raise HTTPException(status_code=403, detail="Driver does not belong to this delivery request")
    
    dr_db.status = DeliveryRequestStatus.delivering
    dr_db.picked_up_at = datetime.now()

    session.add(dr_db)
    session.commit()
    session.refresh(dr_db)
    return dr_db

async def delivered_delivery_request(session: Session, id: int, user_id: int) -> DeliveryRequest:
    dr_db = get_dr_by_id(session, id)

    driver_db = driver_logic.get_driver_by_user_id(session, user_id)

    if dr_db.driver_id != driver_db.id:
        raise HTTPException(status_code=403, detail="Driver does not belong to this delivery request")
    
    dr_db.delivered_at = datetime.now()
    dr_db.is_confirmed_by_driver = True

    session.add(dr_db)

    # Notify customer that the order is delivered
    await manager.send_to_user(
        user_id=dr_db.customer_id,
        message={
            "event": "delivery_request_delivered",
            "data": dr_db.model_dump(mode="json")
        }
    )

    session.commit()
    session.refresh(dr_db)

    return dr_db

def customer_confirmed(session: Session, id: int, customer_id: int) -> DeliveryRequest:
    dr_db = get_dr_by_id(session, id)

    if dr_db.customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Customer does not belong to this delivery request")
    
    dr_db.is_confirmed_by_customer = True
    if dr_db.is_confirmed_by_driver and dr_db.is_confirmed_by_driver:
        dr_db.status = DeliveryRequestStatus.delivered

    session.add(dr_db)
    session.commit()
    session.refresh(dr_db)
    return dr_db
    
def get_delivery_requests_for_customer(
    session: Session, customer_id: int, offset: int, limit: int
) -> list[DeliveryRequestForCustomer]:
    stmt = (
        select(DeliveryRequest)
        .where(
            DeliveryRequest.customer_id == customer_id,
            DeliveryRequest.is_active == True)
        .offset(offset).limit(limit)
    )

    drs = session.exec(stmt).all()
    return [
        DeliveryRequestForCustomer(
            id=dr.id,
            order_id=dr.order_id,
            branch_id=dr.branch_id,
            customer_id=dr.customer_id,
            driver_id=dr.driver_id,
            status=dr.status,
            dropoff_lon=dr.dropoff_lon,
            dropoff_lat=dr.dropoff_lat,
            created_at=dr.created_at,
            assigned_at=dr.assigned_at,
            accepted_at=dr.accepted_at,
            picked_up_at=dr.picked_up_at,
            delivered_at=dr.delivered_at,
            is_confirmed_by_customer=dr.is_confirmed_by_customer
        )
        for dr in drs]

def get_delivery_requests_for_driver(
    session: Session, driver_id: int, offset: int, limit: int
) -> list[DeliveryRequestPublic]:
    stmt = (
        select(DeliveryRequest)
        .where(
            DeliveryRequest.driver_id == driver_id,
            DeliveryRequest.is_active == True)
        .offset(offset).limit(limit)
    )
    return session.exec(stmt).all()

def get_delivery_request_for_actor(
    session: Session, actor: User, offset: int, limit: int
):
    
    if actor.role == UserRole.customer:
        return get_delivery_requests_for_customer(
            session, actor.id, offset, limit
        )
    elif actor.role == UserRole.driver:
        driver_db = driver_logic.get_driver_by_user_id(session, actor.id)
        return get_delivery_requests_for_driver(
            session, driver_db.id, offset, limit
        )
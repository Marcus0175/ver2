from fastapi import HTTPException
from sqlmodel import Session, select, func
from datetime import datetime

from ..logics import user_logic, branch_logic
from ..models.users import User, UserRole
from ..models.delivery_requests import DeliveryRequest
from ..models.drivers import DriverCreate, Driver
from ..websocket.connection_manager import manager


def assign_driver_to_branch(session: Session, cur_act_user: User, driver: DriverCreate) -> Driver:
    
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])

    user_db: User = user_logic.get_user_by_id(session, driver.user_id)
    if user_db.role is not UserRole.driver:
        raise HTTPException(status_code=400, detail="User's role is not driver")
    branch_logic.get_branch_by_id(session, driver.branch_id)

    driver_db = session.exec(
        select(Driver)
        .where(Driver.user_id == driver.user_id, Driver.branch_id == driver.branch_id)
    ).first()

    if driver_db:
        raise HTTPException(status_code=400, detail="Assignment of driver already existed")
    
    driver_db = Driver.model_validate(driver)
    session.add(driver_db)
    session.commit()
    session.refresh(driver_db)
    return driver_db

def get_driver_by_id(session: Session, id: int) -> Driver:
    driver_db = session.get(Driver, id)
    if not driver_db:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver_db

def get_driver_by_user_id(session: Session, user_id: int) -> Driver:
    driver_db = session.exec(select(Driver).where(Driver.user_id == user_id)).first()
    if not driver_db:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver_db

def toggle_active_driver(
    session: Session,
    cur_act_user: User,
    id: int,
    is_active: bool = True
) -> Driver:
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])

    driver_db = get_driver_by_id(session, id)

    driver_db.is_active = is_active
    session.add(driver_db)
    session.commit()
    session.refresh(driver_db)
    return driver_db

def get_drivers_by_branch_id(session: Session, branch_id: int, is_active: bool) -> list[Driver]:
    statement = select(Driver).where(Driver.branch_id == branch_id)
    if is_active is not None:
        statement = statement.where(Driver.is_active == is_active)
    drivers_db = session.exec(statement).all()
    return drivers_db

def get_driver_ids_for_branch(session: Session, branch_id: int):
    drivers = get_drivers_by_branch_id(session, branch_id, is_active=True)
    return [driver.user_id for driver in drivers]

def count_drs_for_driver(session: Session, driver_id: int) -> int:
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())

    stmt = (
        select(func.count(DeliveryRequest.id))
        .where(
            DeliveryRequest.driver_id == driver_id,
            DeliveryRequest.created_at >= start_of_day,
        )
    )
    return session.exec(stmt).one()

def get_least_busy_driver(session: Session, branch_id: int) -> Driver:
    drivers_db = get_drivers_by_branch_id(session, branch_id, True)

    if not drivers_db:
        raise HTTPException(status_code=404, detail="There are not active drivers")

    driver_load = [
        (driver, count_drs_for_driver(session, driver.id))
        for driver in drivers_db
    ]
    return min(driver_load, key=lambda x: x[1])[0]

async def assign_driver_to_dr(
    session: Session, branch_id: int, dr_db: DeliveryRequest
) ->DeliveryRequest:
    
    # This function will be triggered by system
    least_busy_driver = get_least_busy_driver(session, branch_id)

    # Fill ks_id of order_item
    dr_db.driver_id = least_busy_driver.id
    dr_db.is_forced_assignment = True
    dr_db.assigned_at = datetime.now()

    session.add(dr_db)

    # Notify to driver through user_id
    await manager.send_to_user(
        user_id=least_busy_driver.user_id,
        message={
            "event": "delivery_request_assigned",
            "data": dr_db.model_dump(mode="json")
        }
    )
    session.commit()
    session.refresh(dr_db)
    return dr_db
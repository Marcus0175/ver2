import asyncio
from sqlmodel import Session

from .models.delivery_requests import DeliveryRequest
from .logics import driver_logic, dr_logic
from .config import get_settings
from .database import engine

ACCEPT_DR_TIMEOUT = get_settings().ACCEPT_DR_TIMEOUT

async def force_assign_driver_if_unclaimed(dr_id: int, timeout: int = ACCEPT_DR_TIMEOUT):
    await asyncio.sleep(timeout)

    with Session(engine) as session:
        dr_db = dr_logic.get_dr_by_id(session, dr_id)

        if dr_db.driver_id is not None:
            print(f"TASK:\tDeliveryRequest {dr_db.id} already claimed by Driver {dr_db.driver_id}")
            return
    
        dr_db = await driver_logic.assign_driver_to_dr(
            session, dr_db.branch_id, dr_db
        )
        print(f"TASK:\tDeliveryRequest {dr_db.id} has been force-assigned to Driver {dr_db.id}")

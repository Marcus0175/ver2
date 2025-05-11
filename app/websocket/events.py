from sqlmodel import Session

from ..database import engine
from ..logics import driver_logic
from .connection_manager import manager

async def broadcast_to_drivers_for_branch(branch_id: int, message: dict):
    with Session(engine) as session:
        driver_ids = driver_logic.get_driver_ids_for_branch(session, branch_id)
        for driver_id in driver_ids:
            if driver_id in manager.active_connections:
                await manager.send_to_user(driver_id, message)

from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import user_logic, driver_logic
from ..models.users import User, UserRole
from ..models.drivers import DriverCreate, DriverPublic
from ..database import get_session

router = APIRouter()

@router.post("/assign", response_model=DriverPublic)
async def assign_driver(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    driver: DriverCreate = Body()
):
    """
    Assign an specific account with role `Driver` (entity in DB, not role) to a `Branch`.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return driver_logic.assign_driver_to_branch(session, cur_act_user, driver)

@router.patch("/{id}/active", response_model=DriverPublic)
async def active_driver(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Activate `Driver` (entity in DB, not role).

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return driver_logic.toggle_active_driver(session, cur_act_user, id)

@router.patch("/{id}/deactive", response_model=DriverPublic)
async def deactive_driver(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Deactivate `Driver` (entity in DB, not role).

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return driver_logic.toggle_active_driver(session, cur_act_user, id, False)

@router.get("/by-branch/{branch_id}", response_model=list[DriverPublic])
async def read_drivers_by_branch(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch_id: int = Path(),
    is_active: bool = Query(default=None)
):
    """
    View list of `Driver` (entity in DB, not role) in a specific `Branch`.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])
    return driver_logic.get_drivers_by_branch_id(session, branch_id, is_active)
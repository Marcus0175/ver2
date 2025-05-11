from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import ks_logic, user_logic
from ..models.users import User, UserRole
from ..models.kitchen_staffs import KitchenStaffCreate, KitchenStaffPublic
from ..database import get_session

router = APIRouter()

@router.post("/assign", response_model=KitchenStaffPublic)
async def assign_kitchen_staff(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    kitchen_staff: KitchenStaffCreate = Body()
):
    """
    Assign an specific account with role `KitchenStaff` (entity in DB, not role) to a `Branch`.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return ks_logic.assign_ks_to_branch(session, cur_act_user, kitchen_staff)

@router.patch("/{id}/active", response_model=KitchenStaffPublic)
async def active_kitchen_staff(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Activate `KitchenStaff` (entity in DB, not role).

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return ks_logic.toggle_active_ks(session, cur_act_user, id)

@router.patch("/{id}/deactive", response_model=KitchenStaffPublic)
async def deactive_kitchen_staff(
    session: Session = Depends(get_session), 
    cur_act_user: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Deactivate `KitchenStaff` (entity in DB, not role).

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    return ks_logic.toggle_active_ks(session, cur_act_user, id, False)

@router.get("/by-branch/{branch_id}", response_model=list[KitchenStaffPublic])
async def read_kitchen_staffs_by_branch(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch_id: int = Path(),
    is_active: bool = Query(default=None)
):
    """
    View list of `KitchenStaff` (entity in DB, not role) in a specific `Branch`.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])
    return ks_logic.get_kss_by_branch_id(session, branch_id, is_active)
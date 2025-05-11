from fastapi import Path, Depends, Body, Query, HTTPException, status
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import user_logic
from ..models.users import User, UserCreate, UserPublic, UserRole
from ..database import get_session

router = APIRouter()

@router.post("/register", response_model=UserPublic)
async def create_staff_account(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    user: UserCreate = Body()
):
    """
    Create account for staffs.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin, UserRole.owner])
    return user_logic.create_user(session, user)

@router.patch("/{user_id}/active", response_model=UserPublic)
async def active_account(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    user_id: int = Path()
):
    """
    Activate an account includes: customer account, staff account.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin])
    return user_logic.toggle_active_account(session, user_id)
    
    
@router.patch("/{user_id}/deactive", response_model=UserPublic)
async def deactive_account(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    user_id: int = Path()
): 
    """
    Deactivate an account includes: customer account, staff account.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin])
    return user_logic.toggle_active_account(session, user_id, is_active=False)


@router.get("/", response_model=list[UserPublic])
async def read_users(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of accounts.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`
    """
    user_logic.require_role(cur_act_user, [UserRole.admin])
    return user_logic.get_users(session, offset, limit)
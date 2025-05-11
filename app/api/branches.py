from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import branch_logic, menu_item_logic, user_logic
from ..models.users import User, UserRole
from ..models.branches import BranchCreate, BranchUpdate, BranchPublic
from ..models.menu_items import MenuItemCreate, MenuItemPublic
from ..models.orders import OrderPublic
from ..models.order_items import OrderItemPublicV2
from ..models.delivery_requests import DeliveryRequestPublic
from ..database import get_session

router = APIRouter()

@router.post("/", response_model=BranchPublic)
async def create_new_branch(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch: BranchCreate = Body()
):
    """
    Create a `Branch`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return branch_logic.create_branch(session, cur_act_user, branch)


@router.get("/", 
    dependencies=[Depends(get_current_active_user)], 
    response_model=list[BranchPublic]
)
async def read_branches(
    session: Session = Depends(get_session),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of `Branch`es in Restaurant chain.

    🔐 **Access Control**:
    - Allowed Roles: `All`
    """
    return branch_logic.get_branches(session, offset, limit)

@router.get("/{branch_id}", 
    dependencies=[Depends(get_current_active_user)], 
    response_model=BranchPublic
)
async def read_branch(
    session: Session = Depends(get_session),
    branch_id: int = Path()
):
    """
    View a specific `Branch` by `branch_id`.

    🔐 **Access Control**:
    - Allowed Roles: `All`
    """
    return branch_logic.get_branch_by_id(session, branch_id)

@router.put("/{branch_id}", response_model=BranchPublic)
async def update_branch(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch_id: int = Path(),
    branch: BranchUpdate = Body()
):
    """
    Update information of a specific `Branch` by `branch_id`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return branch_logic.update_branch_by_id(
        session, cur_act_user, branch_id, branch)

@router.delete("/{branch_id}")
async def update_branch(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch_id: int = Path()
):
    """
    Delete a specific `Branch` by `branch_id`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return branch_logic.delete_branch_by_id(
        session, cur_act_user, branch_id)

@router.post("/{branch_id}/menu-items", response_model=MenuItemPublic)
async def create_new_menu_item(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    branch_id: int = Path(),
    menu_item: MenuItemCreate = Body()
):
    """
    Create a `MenuItem` for a specific `Branch` by `branch_id`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return menu_item_logic.create_menu_item(
        session, cur_act_user, branch_id, menu_item)

@router.get("/{branch_id}/menu-items", response_model=list[MenuItemPublic])
async def read_menu_items(
    session: Session = Depends(get_session),
    branch_id: int = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of `MenuItem`s for a specific `Branch` by `branch_id`.

    🔐 **Access Control**:
    - Allowed Roles: `All`
    """
    return menu_item_logic.get_menu_items_by_branch_id(
        session, branch_id, offset, limit)

# @router.get("/{branch_id}/orders", response_model=list[OrderPublic])
# @router.get("/{branch_id}/order-items", response_model=list[OrderItemPublicV2])
# @router.get("/{branch_id}/delivery-requests", response_model=list[DeliveryRequestPublic])
# async def read_delivery_requests_for_branch(
#     session: Session = Depends(get_session),
#     cur_act_user: User = Depends(get_current_active_user),
#     branch_id: int = Path(),
#     offset: int = Query(default=0),
#     limit: int = Query(default=100)
# ):
#     user_logic.require_role(cur_act_user, [UserRole.owner, UserRole.driver])
#     return branch_logic.get_delivery_requests_for_branch(session, branch_id, offset, limit)
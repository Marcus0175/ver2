from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import menu_item_logic
from ..models.users import User
from ..models.menu_items import MenuItemUpdate, MenuItemPublic
from ..database import get_session

router = APIRouter()

@router.put("/{menu_item_id}", response_model=MenuItemPublic)
async def update_menu_item(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    menu_item_id: int = Path(),
    menu_item: MenuItemUpdate = Body()
):
    """
    Updating information of a specific `MenuItem`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return menu_item_logic.update_menu_item_by_id(
        session, cur_act_user, menu_item_id, menu_item)

@router.delete("/{menu_item_id}")
async def delete_menu_item(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    menu_item_id: int = Path()
):
    """
    Deleting a specific `MenuItem`.

    🔐 **Access Control**:
    - Allowed Roles: `Owner`
    """
    return menu_item_logic.delete_menu_item_by_id(
        session, cur_act_user, menu_item_id)
from fastapi import HTTPException, status
from sqlmodel import Session, select, col
from datetime import datetime

from ..logics import user_logic, branch_logic
from ..models.users import User, UserRole
from ..models.menu_items import MenuItemCreate, MenuItemUpdate, MenuItem

def create_menu_item(
    session: Session, 
    cur_act_user: User, 
    branch_id: int, 
    menu_item: MenuItemCreate
) -> MenuItem:
    
    user_logic.require_role(cur_act_user, [UserRole.owner])

    branch_logic.get_branch_by_id(session, branch_id)

    menu_item_db = MenuItem.model_validate(menu_item, update={"branch_id": branch_id})
    session.add(menu_item_db)
    session.commit()
    session.refresh(menu_item_db)
    
    return menu_item_db

def get_menu_items_by_branch_id(session: Session, branch_id: int, offset: int, limit: int) -> MenuItem:
    branch_logic.get_branch_by_id(session, branch_id)

    return session.exec(
        select(MenuItem)
        .where(MenuItem.branch_id == branch_id).offset(offset).limit(limit)
    ).all()

def get_menu_item_by_id(session: Session, menu_item_id: int) -> MenuItem:
    menu_item_db = session.get(MenuItem, menu_item_id)
    if not menu_item_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item_db

def get_menu_item_prices_by_ids(session: Session, ids: list[int]) -> list[MenuItem]:
    menu_item_prices_db = session.exec(
        select(col(MenuItem.price)).where(col(MenuItem.id).in_(ids))
    ).all()

    if not menu_item_prices_db:
        raise HTTPException(status_code=404, detail="Menu item prices not found")

    return menu_item_prices_db
    

def update_menu_item_by_id(
    session: Session, 
    cur_act_user: User, 
    menu_item_id: int, 
    menu_item: MenuItemUpdate
) -> MenuItem:
    user_logic.require_role(cur_act_user, [UserRole.owner])
    menu_item_db = get_menu_item_by_id(session, menu_item_id)
    menu_item_data = menu_item.model_dump(exclude_unset=True)
    menu_item_db.sqlmodel_update(menu_item_data, update={"updated_at": datetime.now()})
    session.add(menu_item_db)
    session.commit()
    session.refresh(menu_item_db)
    return menu_item_db

def delete_menu_item_by_id(session: Session, cur_act_user: User, menu_item_id: int) -> dict[str, str]:
    user_logic.require_role(cur_act_user, [UserRole.owner])
    menu_item_db = get_menu_item_by_id(session, menu_item_id)
    session.delete(menu_item_db)
    session.commit()
    return {"msg": "Menu item deleted successfully"}
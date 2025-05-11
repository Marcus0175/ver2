from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import order_logic, user_logic
from ..models.users import User, UserRole
from ..models.orders import OrderCreate, OrderPublic, OrderPublicForCustomer
from ..database import get_session

router = APIRouter()

@router.post("/", response_model=OrderPublic)
async def create_new_order(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    order: OrderCreate = Body()
):
    """
    Create new `Order`.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    return await order_logic.create_new_order(session, cur_act_user, order)


@router.get("/mine", response_model=list[OrderPublicForCustomer])
async def read_my_orders(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=1000)
):
    """
    View list of `Order`s of current `Customer`.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    user_logic.require_role(cur_act_user, [UserRole.customer])
    return order_logic.get_enrich_orders_by_customer_id(session, cur_act_user.id, offset, limit)

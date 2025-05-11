from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import order_item_logic, user_logic
from ..models.users import User, UserRole
from ..models.order_items import OrderItemPublicV2
from ..database import get_session

router = APIRouter()

@router.get("/mine", response_model=list[OrderItemPublicV2])
async def read_order_items_need_to_cook(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user)
):
    """
    View list of `preparing OrderItem`s that assigned to current kitchen staff need to be cooked <br> <br>

    **Note**: Only `Kichen Staff` who assigned to these `OrderItem`s by the system could see them.

    🔐 **Access Control**:
    - Allowed Roles: `Kitchen Staff`

    """
    user_logic.require_role(cur_act_user, [UserRole.kitchen_staff])
    return order_item_logic.get_order_items_for_ks(
        session, cur_act_user.id
    )

@router.patch("/{id}/ready", response_model=OrderItemPublicV2)
async def ready_order_item(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Change a specific `OrderItem` status from `preparing` to `ready` <br><br>

    **Note**: Only `Kichen Staff` who assigned to this `OrderItem` by the system could do. 
    If all `OrderItem`s of `Order` are `ready`, the system will change `Order` status from `preparing`
    to `ready_for_delivery` and the `is_active` field of `DeliveryRequest` turns to `True`, so `Driver`, now,
    could accept that `DeliveryRequest` until *timeout*. <br>

    **Note**: Notifying to all `Driver`s in `Branch` (WebSocket Broadcast).<br>

    **Note**: If there is no `Driver` accepts `DeliveryRequest` - *timeout*. The system also does 
    assign automatically that `DeliveryRequest` to specific `Driver` and notify that `Driver`.

    **Note**: Notifying to a specific `Driver` in `Branch` (WebSocket Unicast). <br><br>

    🔐 **Access Control**:
    - Allowed Roles: `Kitchen Staff`

    """
    user_logic.require_role(cur_act_user, [UserRole.kitchen_staff])
    return await order_item_logic.ready_order_item(session, id, cur_act_user.id)
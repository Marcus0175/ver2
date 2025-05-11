from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import user_logic, dr_logic
from ..models.users import User, UserRole
from ..models.delivery_requests import DeliveryRequestPublic
from ..database import get_session

router = APIRouter()

@router.get("/", response_model=list[DeliveryRequestPublic])
async def read_delivery_requests(
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=100),
    is_active: int = Query(default=None)
):
    """
    View list of `DeliveryRequest`s of all `Branch`es.

    🔐 **Access Control**:
    - Allowed Roles: `Admin`, `Owner`
    """
    user_logic.require_role(cur_user_active, [UserRole.admin, UserRole.owner])
    return dr_logic.get_delivery_requests(session, offset, limit, is_active)

@router.get("/not-accepted", response_model=list[DeliveryRequestPublic])
async def read_not_accepted_delivery_requests(
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of `DeliveryRequest`s which are not accepted by any `Driver`.

    🔐 **Access Control**:
    - Allowed Roles: `Driver`
    """
    user_logic.require_role(cur_user_active, [UserRole.driver])
    return dr_logic.get_not_accepted_delivery_requests(session, cur_user_active.id, offset, limit)

@router.patch("/{id}/accept", response_model=DeliveryRequestPublic)
async def accept_delivery_request(
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Accept a specific `DeliveryRequest` which is not accepted by any `Driver`. <br> <br>
    **Note**: if timeout, the `DeliveryRequest` is still not accepted by any `Driver`. The system will do auto-assignment `DeliveryRequest` to a specific `Driver`, the criterion bases on number of `DeliveryRequests` that a `Driver` accepted/assigned on current day.

    🔐 **Access Control**:
    - Allowed Roles: `Driver`
    """
    user_logic.require_role(cur_user_active, [UserRole.driver])
    return dr_logic.accept_delivery_request(session, id, cur_user_active.id)

@router.patch("/{id}/delivering", response_model=DeliveryRequestPublic)
async def delivering_delivery_request(
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Change `status` of `DeliveryRequest` from `pending` to `delivering`.

    🔐 **Access Control**:
    - Allowed Roles: `Driver`
    """
    user_logic.require_role(cur_user_active, [UserRole.driver])
    return dr_logic.delivering_delivery_request(
        session, id, cur_user_active.id
    )

@router.patch("/{id}/delivered", response_model=DeliveryRequestPublic)
async def delivered_delivery_request(
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Confirm that this `DeliveryRequest` is delivered by `Driver`. <br> <br>
    **Note**: Only both `Customer` and `Driver` confirmed this `DeliveryRequest` is delivered, its `status` is changed from `delivering` to `delivered`.

    🔐 **Access Control**:
    - Allowed Roles: `Driver`
    """
    user_logic.require_role(cur_user_active, [UserRole.driver])
    return await dr_logic.delivered_delivery_request(
        session, id, cur_user_active.id
    )

@router.patch("/{id}/customer-confirmed", response_model=DeliveryRequestPublic)
async def customer_confirmed(    
    session: Session = Depends(get_session),
    cur_user_active: User = Depends(get_current_active_user),
    id: int = Path()
):
    """
    Confirm that this `DeliveryRequest` is delivered by `Customer`. <br> <br>
    **Note**: Only both `Customer` and `Driver` confirmed this `DeliveryRequest` is delivered, its `status` is changed from `delivering` to `delivered`.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    user_logic.require_role(cur_user_active, [UserRole.customer])
    return dr_logic.customer_confirmed(
        session, id, cur_user_active.id
    )

@router.get("/mine")
async def read_my_delivery_requests(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of `DeliveryRequest`s of current `Customer`.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    user_logic.require_role(cur_act_user, ["driver", "customer"])
    return dr_logic.get_delivery_request_for_actor(
        session, cur_act_user, offset, limit
    )
from fastapi import Path, Body, Query, Depends, status, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import payment_logic, user_logic
from ..models.users import User, UserRole
from ..models.payments import PaymentPublic, PaymentMethod
from ..database import get_session

router = APIRouter()

@router.get("/mine", response_model=list[PaymentPublic])
async def read_my_payments(
    session: Session = Depends(get_session),
    curr_act_user: User = Depends(get_current_active_user),
    offset: int = Query(default=0),
    limit: int = Query(default=100)
):
    """
    View list of `Payment`s of current `Customer`

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    user_logic.require_role(curr_act_user, [UserRole.customer])
    return payment_logic.get_payments_for_customer(session, curr_act_user, offset, limit)


@router.patch("/{payment_id}/checkout", response_model=PaymentPublic)
async def checkout(
    session: Session = Depends(get_session),
    cur_act_user: User = Depends(get_current_active_user),
    payment_id: int = Path(),
    payment_method: PaymentMethod = Body(embed=True)
):
    """
    Checkout an specific `Payment` of current `Customer`.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    user_logic.require_role(cur_act_user, [UserRole.customer])
    return await payment_logic.checkout_payment(session, cur_act_user, payment_id, payment_method)
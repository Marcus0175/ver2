from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import datetime

from . import order_logic, ks_logic
from ..models.users import User, UserRole
from ..models.payments import Payment, PaymentStatus, PaymentMethod

def create_payment(
    session: Session,
    payment_db: Payment
):
    # This function is triggered by system, not any actor
    session.add(payment_db)
    session.commit()

def get_payment_by_id(session: Session, payment_id: int) -> Payment:
    payment_db = session.get(Payment, payment_id)
    if not payment_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment_db
    
def check_payment_belongs_to_customer(user_id: int, payment_db: Payment):
    if payment_db.customer_id != user_id:
        raise HTTPException(status_code=403, detail="Payment does not belong to customer")
    
def get_payments_for_customer(session: Session, cur_act_user: User, offset: int, limit: int) -> list[Payment]:
    return session.exec(
        select(Payment).where(Payment.customer_id == cur_act_user.id)
        .offset(offset).limit(limit)
    ).all()

async def checkout_payment(session: Session, curr_act_user: User, payment_id: int, payment_method: PaymentMethod) -> Payment:

    payment_db = get_payment_by_id(session, payment_id)

    check_payment_belongs_to_customer(curr_act_user.id, payment_db)

    payment_db.method = payment_method
    payment_db.status = PaymentStatus.paid
    payment_db.updated_at = datetime.now()
    session.add(payment_db)
    session.commit()

    order_db = order_logic.preparing_order(session, payment_db.order_id)
    await ks_logic.assign_kss_to_order_items(session, order_db.branch_id, order_db.order_items)

    session.refresh(payment_db)
    return payment_db
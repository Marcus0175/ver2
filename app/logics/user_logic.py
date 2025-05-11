from fastapi import HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta, datetime

from ..helpers import get_password_hash, verify_password, create_access_token
from ..models.users import User, UserCreate, UserRole
from ..models.tokens import Token
from ..config import Settings

def get_user_by_username(session: Session, username: str) -> User:
    try:
        user = session.exec(
            select(User)
            .where(User.username == username)
        ).one()
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def get_user_by_id(session: Session, user_id: int) -> User:
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    return user_db

def verify_username_pw(session: Session, username: str, password: str) -> User:
    user: User = get_user_by_username(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def require_role(user: User, allowed_roles: list[UserRole]) -> User:
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action." + 
                    f" Allowed roles: {', '.join(allowed_roles)}"
        )
    
def create_user(session: Session, user: UserCreate, current_user: User | None = None) -> User:

    # print(f"CURRENT USER ROLE: {current_user}, REGISTER USER ROLE: {user.role}")
    cond1 = bool(current_user is not None and user.role not in [UserRole.kitchen_staff, UserRole.driver])
    cond2 = bool(current_user is None and user.role is not UserRole.customer)
    print(f"DEBUGGG: {cond1, cond2}")
    
    if cond1 and cond2:
        raise HTTPException(
            status_code=400,
            detail="You are not allowed to create account with this role"
        )
        
    hashed_password = get_password_hash(user.password)
    extra_data = {"hashed_password": hashed_password}
    user_db = User.model_validate(user, update=extra_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db

def authenticate_user(
    session: Session, settings: Settings, 
    username: str, password: str
) -> Token:
    user = verify_username_pw(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    
    access_token = create_access_token(
        data={
            "sub": str(user.username)
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")

def toggle_active_account(session: Session, user_id: int, is_active: bool = True) -> User:
    user_db = get_user_by_id(session, user_id)

    user_db.is_active = is_active
    user_db.updated_at = datetime.now()

    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

def get_users(session: Session, offset: int, limit: int) -> User:

    users_db = session.exec(
        select(User).offset(offset).limit(limit)
    ).all()
    return users_db
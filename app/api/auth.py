from fastapi import Path, Depends, Body, Query, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from sqlmodel import Session

from ..dependencies import get_current_active_user
from ..logics import user_logic
from ..models.users import User, UserCreate, UserPublic
from ..models.tokens import Token
from ..config import Settings, get_settings
from ..database import get_session

router = APIRouter()

@router.post("/register", response_model=UserPublic)
async def create_new_user(
    session: Session = Depends(get_session),
    user: UserCreate = Body()
):
    """
    Customers register.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    return user_logic.create_user(session, user, None)
    
@router.post("/login", response_model=Token)
async def login(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Customers login.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    return user_logic.authenticate_user(
        session, settings, form_data.username, form_data.password)

@router.get("/me", response_model=UserPublic)
async def read_me(current_user: User = Depends(get_current_active_user)):
    """
    Customers see their account information.

    🔐 **Access Control**:
    - Allowed Roles: `Customer`
    """
    return current_user
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session


from .logics import user_logic
from .config import Settings, get_settings
from .models.users import User
from .database import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
    token: OAuth2PasswordBearer = Depends(oauth2_scheme),
) -> User:
    if token is None:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = user_logic.get_user_by_username(session=session, username=username)
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User | None:
    if current_user and not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user
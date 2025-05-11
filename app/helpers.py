from typing import Callable, Any
from httpx import AsyncClient, RequestError, HTTPStatusError, Response
from fastapi import HTTPException
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from .config import get_settings

settings = get_settings()

def get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, 
                                    salt=salt)
    return hashed_password

def verify_password(plain_password, hashed_password):
    password_bytes_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=password_bytes_enc, 
                    hashed_password=hashed_password_bytes)

async def http_call(
    method: Callable[..., Any],
    *args, 
    **kwargs
) -> Response:
    try:
        async with AsyncClient() as client:
            response: Response = await method(client, *args, **kwargs)
            response.raise_for_status()
            return response.json()
    except RequestError as exc:
        # For resquest
        raise HTTPException(
            status_code=500,
            detail=f"Request error while calling {exc.request.url!r}"
        )
    except HTTPStatusError as exc:
        # For response
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.json().get("detail", "Unknown error")
        )
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # if there is no expires_delta, just set expire time is 15 mins
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
                    to_encode, 
                    settings.SECRET_KEY, 
                    algorithm=settings.ALGORITHM
                )
    return encode_jwt

async def calculate_distance_km(
    pickup_lon: Decimal, pickup_lat: Decimal, 
    dropoff_lon: Decimal, dropoff_lat: Decimal
) -> float:
    
    async def call(client: AsyncClient):
        return await client.get(
                f"{settings.ORS_URL}/directions/driving-car",
                params={
                    "api_key": settings.ORS_API_KEY, 
                    "start": f"{pickup_lon},{pickup_lat}",
                    "end": f"{dropoff_lon},{dropoff_lat}",
                }
            )
    
    geo_data = await http_call(call)
    distance_m = geo_data["features"][0]["properties"]["summary"]["distance"]
    distance_km = distance_m / 1000
    return distance_km

def calculate_shipping_fee(distance_km):
    return settings.BASE_FEE + (distance_km * settings.RATE_PER_KM)
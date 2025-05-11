from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .api import (
    auth, users, branches, 
    kitchen_staffs, drivers, menu_items, 
    orders, order_items, delivery_requests, payments
)
from .websocket.endpoints import router as websocket_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("START: FOOD DELIVERY")
    create_db_and_tables()
    yield
    print("STOP: FOOD DELIVERY")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(kitchen_staffs.router, prefix="/kitchen-staffs", tags=["Kitchen Staffs"])
app.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
app.include_router(branches.router, prefix="/branches", tags=["Branches"])
app.include_router(menu_items.router, prefix="/menu-items", tags=["Menu Items"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(order_items.router, prefix="/order-items", tags=["Order Items"])
app.include_router(delivery_requests.router, prefix="/delivery-requests", tags=["Delivery Requests"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(websocket_router)

# app.include_router(auth.router, prefix="/auth")
# app.include_router(users.router, prefix="/users")
# app.include_router(kitchen_staffs.router, prefix="/kitchen-staffs")
# app.include_router(drivers.router, prefix="/drivers")
# app.include_router(branches.router, prefix="/branches")
# app.include_router(menu_items.router, prefix="/menu-items")
# app.include_router(orders.router, prefix="/orders")
# app.include_router(delivery_requests.router, prefix="/delivery-requests")
# app.include_router(payments.router, prefix="/payments")
# app.include_router(websocket_router)
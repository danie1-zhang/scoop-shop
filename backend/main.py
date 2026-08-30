from fastapi import FastAPI

from .routers import auth, cart, flavors, health, orders


app = FastAPI()

app.include_router(health.router)
app.include_router(flavors.router)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(orders.router)

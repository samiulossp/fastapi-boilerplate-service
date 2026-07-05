from fastapi import FastAPI
import uvicorn
from app.core.database import Base, engine
from app.models.refresh_token import RefreshToken
from app.models.blog import Blog
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.routers.auth import router as auth_router
from app.routers.blogs import router as blogs_router
from app.routers.cart import router as cart_router
from app.routers.categories import router as categories_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(blogs_router)
app.include_router(users_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Boilerplate Services !"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8809, reload=True)
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://erp_user:erp_local_password@localhost:5433/erp_interview",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="confirmed")


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sku: str = Field(min_length=1, max_length=64)
    stock: int = 0


class OrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="ERP/CRM Interview API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    # Candidate should assess whether this is a meaningful connectivity check.
    db.execute(select(1))
    return {"database": "connected"}


@app.post("/customers", status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(name=payload.name, email=payload.email)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return {"id": customer.id, "name": customer.name, "email": customer.email}


@app.post("/products", status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(name=payload.name, sku=payload.sku, stock=payload.stock)
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"id": product.id, "name": product.name, "sku": product.sku, "stock": product.stock}


@app.get("/products")
def list_products(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    rows = db.scalars(select(Product).offset(offset).limit(limit)).all()
    return {
        "items": [{"id": p.id, "name": p.name, "sku": p.sku, "stock": p.stock} for p in rows],
        "count": db.scalar(select(Product).count()) if False else len(rows),
    }


@app.post("/orders", status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    customer = db.get(Customer, payload.customer_id)
    product = db.get(Product, payload.product_id)

    if customer is None or product is None:
        raise HTTPException(status_code=404, detail="Customer or product not found")

    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Intentional issue: read/check/update is not concurrency-safe.
    product.stock -= payload.quantity
    order = SalesOrder(
        customer_id=payload.customer_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        status="confirmed",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": order.status,
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(SalesOrder, order_id)
    if order is None:
        return {"error": "Order not found"}
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": order.status,
    }

import os
import time
import redis
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="Ecommerce API")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/ecommerce")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=3)

PRODUCTS = [
    {"id": 1, "name": "Wireless Mouse", "price": 19.99},
    {"id": 2, "name": "Mechanical Keyboard", "price": 89.99},
    {"id": 3, "name": "USB-C Hub", "price": 34.99},
]


@app.get("/")
def root():
    return {"status": "ok", "service": "ecommerce-api"}


@app.get("/health")
def health():
    """Liveness check - does the process respond at all"""
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    """Readiness check - can we actually reach our dependencies"""
    checks = {"database": False, "redis": False}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database_error"] = str(e)

    try:
        redis_client.ping()
        checks["redis"] = True
    except Exception as e:
        checks["redis_error"] = str(e)

    if not (checks["database"] and checks["redis"]):
        raise HTTPException(status_code=503, detail=checks)

    return checks


@app.get("/products")
def list_products():
    cache_key = "products:all"
    cached = redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "products": eval(cached)}

    redis_client.setex(cache_key, 30, str(PRODUCTS))
    return {"source": "db", "products": PRODUCTS}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/orders")
def create_order(product_id: int, quantity: int = 1):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    order = {
        "product_id": product_id,
        "quantity": quantity,
        "total": round(product["price"] * quantity, 2),
        "created_at": time.time(),
    }
    return {"order": order, "status": "created"}

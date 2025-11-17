import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Pizza, Order, OrderItem

app = FastAPI(title="Pizza Restaurant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreatePizza(BaseModel):
    name: str
    description: str | None = None
    price: float
    image: str | None = None
    vegetarian: bool = False
    spicy: bool = False


class CreateOrderItem(BaseModel):
    pizza_id: str
    quantity: int


class CreateOrder(BaseModel):
    customer_name: str
    phone: str
    address: str
    items: List[CreateOrderItem]
    notes: str | None = None


@app.get("/")
def read_root():
    return {"message": "Pizza API is running"}


@app.get("/api/menu", response_model=List[Pizza])
def get_menu():
    docs = get_documents("pizza")
    # Coerce _id to string
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@app.post("/api/menu")
def add_pizza(pizza: CreatePizza):
    pid = create_document("pizza", pizza.dict())
    return {"id": pid}


@app.post("/api/orders")
def create_order(payload: CreateOrder):
    # Fetch pizzas to compute totals and store name/price snapshot
    items: List[OrderItem] = []
    total = 0.0
    for it in payload.items:
        try:
            oid = ObjectId(it.pizza_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid pizza_id: {it.pizza_id}")
        doc = db["pizza"].find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail=f"Pizza not found: {it.pizza_id}")
        name = doc.get("name")
        price = float(doc.get("price", 0))
        qty = max(1, int(it.quantity))
        total += price * qty
        items.append(OrderItem(pizza_id=it.pizza_id, name=name, price=price, quantity=qty))

    order = Order(
        customer_name=payload.customer_name,
        phone=payload.phone,
        address=payload.address,
        items=items,
        notes=payload.notes,
        total=round(total, 2),
        status="received",
    )
    order_id = create_document("order", order)
    return {"id": order_id, "total": order.total}


@app.get("/api/orders")
def list_orders():
    docs = get_documents("order")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

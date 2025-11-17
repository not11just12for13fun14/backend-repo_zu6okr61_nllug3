"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Pizza restaurant schemas
class Pizza(BaseModel):
    """
    Pizza menu items
    Collection name: "pizza"
    """
    name: str = Field(..., description="Pizza name")
    description: Optional[str] = Field(None, description="Short description of the pizza")
    price: float = Field(..., ge=0, description="Price in dollars")
    image: Optional[str] = Field(None, description="Public image URL")
    vegetarian: bool = Field(False, description="Is vegetarian friendly")
    spicy: bool = Field(False, description="Is spicy")

class OrderItem(BaseModel):
    pizza_id: str = Field(..., description="ID of the pizza")
    name: str = Field(..., description="Name snapshot at time of order")
    price: float = Field(..., ge=0, description="Unit price at time of order")
    quantity: int = Field(..., ge=1, description="Quantity ordered")

class Order(BaseModel):
    """
    Customer orders
    Collection name: "order"
    """
    customer_name: str = Field(...)
    phone: str = Field(...)
    address: str = Field(...)
    items: List[OrderItem] = Field(...)
    notes: Optional[str] = Field(None)
    total: float = Field(..., ge=0)
    status: str = Field("received", description="received | preparing | ready | delivered")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!

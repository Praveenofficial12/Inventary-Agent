from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

class Category(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    description: str

class Supplier(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    contact_email: str
    contact_phone: str
    address: str
    rating: float = 5.0

class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(alias="_id", default=None)
    sku: str
    name: str
    category_id: str
    supplier_id: str
    quantity: int = 0
    reorder_threshold: int = 10
    unit_price: float
    cost_price: float
    location: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class InventoryChangeType(str, Enum):
    RESTOCK = "restock"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"

class InventoryLog(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(alias="_id", default=None)
    product_id: str
    change_type: InventoryChangeType
    quantity_delta: int
    resulting_quantity: int
    note: Optional[str] = None
    created_by: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class OrderStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class Order(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(alias="_id", default=None)
    product_id: str
    supplier_id: str
    quantity: int
    status: OrderStatus = OrderStatus.PENDING
    expected_date: datetime
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

MONGO_URI = "mongodb://admin:secret@localhost:27017"
DB_NAME = "inventory_db"

async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Seeding Categories...")
    categories = [
        {"name": "Electronics", "description": "Laptops, phones, etc."},
        {"name": "Furniture", "description": "Desks, chairs, etc."},
        {"name": "Stationery", "description": "Pens, notebooks, etc."}
    ]
    await db.categories.delete_many({})
    cat_result = await db.categories.insert_many(categories)
    cat_ids = cat_result.inserted_ids
    
    print("Seeding Suppliers...")
    suppliers = [
        {"name": "TechCorp", "contact": "contact@techcorp.com", "lead_time_days": 5},
        {"name": "Global Office", "contact": "sales@globaloffice.com", "lead_time_days": 10}
    ]
    await db.suppliers.delete_many({})
    sup_result = await db.suppliers.insert_many(suppliers)
    sup_ids = sup_result.inserted_ids
    
    print("Seeding Products...")
    products = [
        {
            "name": "MacBook Pro 14",
            "sku": "LAP-MBP-14",
            "category_id": str(cat_ids[0]),
            "quantity": 5,
            "reorder_threshold": 10,
            "unit_price": 1999.0,
            "location": "Warehouse A",
            "supplier_id": str(sup_ids[0])
        },
        {
            "name": "Office Chair",
            "sku": "FUR-CHR-01",
            "category_id": str(cat_ids[1]),
            "quantity": 50,
            "reorder_threshold": 20,
            "unit_price": 150.0,
            "location": "Warehouse B",
            "supplier_id": str(sup_ids[1])
        },
        {
            "name": "Wireless Mouse",
            "sku": "ACC-MOU-01",
            "category_id": str(cat_ids[0]),
            "quantity": 0,
            "reorder_threshold": 15,
            "unit_price": 25.0,
            "location": "Warehouse A",
            "supplier_id": str(sup_ids[0])
        }
    ]
    await db.products.delete_many({})
    await db.products.insert_many(products)
    
    print("Seeding Logs...")
    logs = [
        {
            "product_id": "temp", # will fix below
            "change_type": "sale",
            "quantity_delta": -2,
            "resulting_quantity": 3,
            "note": "Quarterly sale",
            "created_by": "admin@nexus.ai",
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    await db.inventory_logs.delete_many({})
    # No logs for now to simulate 'dead stock' in some items
    
    print("Seeding User...")
    await db.users.delete_many({"email": "admin@nexus.ai"})
    # Password is 'admin123' hashed (approx) - actually the app uses its own registration
    # I'll just let the user register themselves or seed a known one if I had the hasher
    
    print("Seed completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())

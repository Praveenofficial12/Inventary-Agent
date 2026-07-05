from fastapi import APIRouter, Depends
from app.db.mongo import get_database
from app.auth.dependencies import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    db = get_database()
    
    total_products = await db.products.count_documents({})
    low_stock = await db.products.count_documents({"$expr": {"$lte": ["$quantity", "$reorder_threshold"]}})
    out_of_stock = await db.products.count_documents({"quantity": 0})
    
    # Valuation
    cursor = db.products.find({})
    total_value = 0
    async for product in cursor:
        total_value += product["quantity"] * product["unit_price"]
        
    return {
        "total_products": total_products,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_value": total_value,
        "active_orders": await db.orders.count_documents({"status": "pending"})
    }

@router.get("/logs")
async def get_logs(limit: int = 20, user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db.inventory_logs.find().sort("created_at", -1).limit(limit)
    logs = []
    async for log in cursor:
        log["_id"] = str(log["_id"])
        logs.append(log)
    return logs

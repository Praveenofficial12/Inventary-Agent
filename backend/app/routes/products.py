from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.inventory import Product, InventoryLog, InventoryChangeType
from app.db.mongo import get_database
from app.auth.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[Product])
async def get_products(
    search: str = Query(None),
    category_id: str = Query(None),
    user: dict = Depends(get_current_user)
):
    db = get_database()
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"sku": {"$regex": search, "$options": "i"}}
        ]
    if category_id:
        query["category_id"] = category_id
    
    cursor = db.products.find(query)
    products = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        products.append(doc)
    return products

@router.post("/", response_model=Product)
async def create_product(product: Product, user: dict = Depends(get_current_user)):
    db = get_database()
    # Check SKU
    existing = await db.products.find_one({"sku": product.sku})
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    prod_dict = product.dict(exclude={"id"})
    prod_dict["created_at"] = datetime.utcnow()
    prod_dict["updated_at"] = datetime.utcnow()
    
    result = await db.products.insert_one(prod_dict)
    prod_dict["_id"] = str(result.inserted_id)
    return prod_dict

@router.put("/{id}", response_model=Product)
async def update_product(id: str, product: Product, user: dict = Depends(get_current_user)):
    db = get_database()
    prod_dict = product.dict(exclude={"id", "created_at"})
    prod_dict["updated_at"] = datetime.utcnow()
    
    await db.products.update_one({"_id": ObjectId(id)}, {"$set": prod_dict})
    prod_dict["_id"] = id
    return prod_dict

@router.post("/{id}/stock", response_model=Product)
async def update_stock(id: str, delta: int, change_type: InventoryChangeType, note: str = None, user: dict = Depends(get_current_user)):
    db = get_database()
    product = await db.products.find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_quantity = product["quantity"] + delta
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Update product
    await db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.utcnow()}}
    )
    
    # Create log
    log = InventoryLog(
        product_id=id,
        change_type=change_type,
        quantity_delta=delta,
        resulting_quantity=new_quantity,
        note=note,
        created_by=user["email"]
    )
    await db.inventory_logs.insert_one(log.dict(exclude={"id"}))
    
    updated_product = await db.products.find_one({"_id": ObjectId(id)})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product

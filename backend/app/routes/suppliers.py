from fastapi import APIRouter, Depends, HTTPException, status
from app.models.inventory import Supplier
from app.db.mongo import get_database
from app.auth.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.get("/", response_model=list[Supplier])
async def get_suppliers(user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db.suppliers.find()
    suppliers = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        suppliers.append(doc)
    return suppliers

@router.post("/", response_model=Supplier)
async def create_supplier(supplier: Supplier, user: dict = Depends(get_current_user)):
    db = get_database()
    sup_dict = supplier.dict(exclude={"id"})
    result = await db.suppliers.insert_one(sup_dict)
    sup_dict["_id"] = str(result.inserted_id)
    return sup_dict

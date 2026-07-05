from fastapi import APIRouter, Depends, HTTPException, status
from app.models.inventory import Category
from app.db.mongo import get_database
from app.auth.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=list[Category])
async def get_categories(user: dict = Depends(get_current_user)):
    db = get_database()
    cursor = db.categories.find()
    categories = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        categories.append(doc)
    return categories

@router.post("/", response_model=Category)
async def create_category(category: Category, user: dict = Depends(get_current_user)):
    db = get_database()
    cat_dict = category.dict(exclude={"id"})
    result = await db.categories.insert_one(cat_dict)
    cat_dict["_id"] = str(result.inserted_id)
    return cat_dict

@router.delete("/{id}")
async def delete_category(id: str, user: dict = Depends(get_current_user)):
    db = get_database()
    await db.categories.delete_one({"_id": ObjectId(id)})
    return {"message": "Category deleted"}

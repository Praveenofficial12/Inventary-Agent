from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.models.user import UserCreate, UserLogin, UserOut, Token, UserInDB
from app.auth.password import get_password_hash, verify_password
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.db.mongo import get_database
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    db = get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_dict = user_in.dict()
    password = user_dict.pop("password")
    user_dict["password_hash"] = get_password_hash(password)
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    
    return user_dict

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    db = get_database()
    user = await db.users.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role", "employee")})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "full_name": user.get("full_name", user.get("name", "")),
            "email": user["email"],
            "role": user.get("role", "employee"),
        }
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(payload: RefreshTokenRequest):
    decoded_payload = decode_token(payload.refresh_token)
    if decoded_payload is None or decoded_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = decoded_payload.get("sub")
    db = get_database()
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(data={"sub": user["email"], "role": user.get("role", "employee")})
    new_refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": {
            "full_name": user.get("full_name", user.get("name", "")),
            "email": user["email"],
            "role": user.get("role", "employee"),
        }
    }

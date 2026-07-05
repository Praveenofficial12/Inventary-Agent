from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from app.auth.jwt_handler import decode_token
from app.db.mongo import get_database
from app.models.user import TokenData, UserRole
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    
    email: str = payload.get("sub")
    role: str = payload.get("role")
    if email is None:
        raise credentials_exception
    
    token_data = TokenData(email=email, role=role)
    
    db = get_database()
    user = await db.users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    # Convert _id to id for convenience
    user["id"] = str(user["_id"])
    return user

def require_role(roles: list[UserRole]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this action"
            )
        return current_user
    return role_checker

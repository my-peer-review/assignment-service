from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

from app.core.config import settings
from app.schemas.context import UserContext

# HTTP Bearer token extraction
security = HTTPBearer()

JWT_ALGORITHM = settings.jwt_algorithm
PUBLIC_KEY = settings.jwt_public_key

async def get_current_user(credentials=Depends(security)) -> UserContext:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return UserContext(user_id=user_id, role=role)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

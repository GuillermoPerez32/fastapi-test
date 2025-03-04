from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.env import SECRET_KEY, ALGORITHM
import jwt
from pydantic import BaseModel
from app.database import User
from sqlalchemy.sql import select

class TokenData(BaseModel):
    username: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(db: Session, username: str):
    return (await db.execute(select(User).filter(User.username == username))).scalars().first()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
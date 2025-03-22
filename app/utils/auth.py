# app/utils/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.models import User, Token, get_db
from app.config import settings
from passlib.context import CryptContext

# Xác thực với OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Mã hóa password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(db: Session, user_id: int, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRES_MINUTES))

    # Tạo payload JWT
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    # Lưu token vào database
    db_token = Token(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_at=expire,
        user_id=user_id
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "expires_at": expire
    }


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Giải mã JWT
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Kiểm tra token trong database
        db_token = db.query(Token).filter(
            Token.access_token == token,
            Token.expires_at > datetime.utcnow(),
            Token.is_revoked == False
        ).first()

        if not db_token:
            raise credentials_exception

        # Lấy user từ database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def revoke_token(db: Session, token: str):
    """Thu hồi token"""
    db_token = db.query(Token).filter(Token.access_token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
        return True
    return False
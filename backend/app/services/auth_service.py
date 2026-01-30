from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_or_create_user(db: Session, google_id: str, email: str, name: str, profile_picture: str) -> User:
    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        user.name = name
        user.email = email
        user.profile_picture = profile_picture
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            profile_picture=profile_picture
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

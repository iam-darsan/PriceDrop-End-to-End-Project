from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    name = Column(String(500))
    current_price = Column(DECIMAL(10, 2))
    currency = Column(String(10), default="USD")
    image_url = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    check_interval_minutes = Column(Integer, default=60)
    last_checked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="products")
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

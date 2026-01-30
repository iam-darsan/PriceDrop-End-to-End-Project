from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    product = relationship("Product", back_populates="price_history")
    
    __table_args__ = (
        Index('idx_product_recorded', 'product_id', 'recorded_at'),
    )

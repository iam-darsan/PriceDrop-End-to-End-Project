from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.schemas.alert import PriceHistoryResponse

router = APIRouter(prefix="/products/{product_id}/history", tags=["history"])

@router.get("", response_model=List[PriceHistoryResponse])
async def get_price_history(
    product_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    query = db.query(PriceHistory).filter(PriceHistory.product_id == product_id)
    
    if start_date:
        query = query.filter(PriceHistory.recorded_at >= start_date)
    if end_date:
        query = query.filter(PriceHistory.recorded_at <= end_date)
    
    history = query.order_by(PriceHistory.recorded_at.desc()).limit(limit).all()
    
    return history

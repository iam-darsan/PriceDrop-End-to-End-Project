from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.price_alert import PriceAlert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter(prefix="/products/{product_id}/alerts", tags=["alerts"])

@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    product_id: int,
    alert_data: AlertCreate,
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
    
    alert = PriceAlert(
        product_id=product_id,
        target_price=alert_data.target_price
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    return alert

@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    product_id: int,
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
    
    alerts = db.query(PriceAlert).filter(PriceAlert.product_id == product_id).all()
    return alerts

router_alerts = APIRouter(prefix="/alerts", tags=["alerts"])

@router_alerts.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(PriceAlert).join(Product).filter(
        PriceAlert.id == alert_id,
        Product.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert_data.target_price is not None:
        alert.target_price = alert_data.target_price
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
    
    db.commit()
    db.refresh(alert)
    
    return alert

@router_alerts.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(PriceAlert).join(Product).filter(
        PriceAlert.id == alert_id,
        Product.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return None

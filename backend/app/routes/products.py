from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.price_alert import PriceAlert
from app.models.price_history import PriceHistory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithAlerts
from app.services.scraper_service import scraper_service

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scraped_data = None
    use_manual = False
    
    try:
        scraped_data = scraper_service.scrape_product(product_data.url)
    except Exception as e:
        if product_data.manual_price is not None:
            use_manual = True
            scraped_data = {
                'price': product_data.manual_price,
                'name': product_data.manual_name or 'Product',
                'currency': product_data.manual_currency or 'USD',
                'image_url': None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to scrape product: {str(e)}. Please provide manual_price, manual_name, and manual_currency as fallback."
            )
    
    product = Product(
        user_id=current_user.id,
        url=product_data.url,
        name=scraped_data['name'],
        current_price=scraped_data['price'],
        currency=scraped_data['currency'],
        image_url=scraped_data['image_url'],
        check_interval_minutes=product_data.check_interval_minutes,
        last_checked_at=datetime.utcnow() if not use_manual else None
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    alert = PriceAlert(
        product_id=product.id,
        target_price=product_data.target_price
    )
    db.add(alert)
    
    history = PriceHistory(
        product_id=product.id,
        price=scraped_data['price'],
        recorded_at=datetime.utcnow()
    )
    db.add(history)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.get("", response_model=List[ProductWithAlerts])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    products = db.query(Product).filter(Product.user_id == current_user.id).offset(skip).limit(limit).all()
    
    result = []
    for product in products:
        alert_count = db.query(func.count(PriceAlert.id)).filter(
            PriceAlert.product_id == product.id,
            PriceAlert.is_active == True
        ).scalar()
        
        product_dict = ProductWithAlerts.model_validate(product)
        product_dict.alert_count = alert_count
        result.append(product_dict)
    
    return result

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
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
    
    return product

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
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
    
    if product_data.check_interval_minutes is not None:
        product.check_interval_minutes = product_data.check_interval_minutes
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
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
    
    db.delete(product)
    db.commit()
    
    return None

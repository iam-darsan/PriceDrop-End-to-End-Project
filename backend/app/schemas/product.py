from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

class ProductCreate(BaseModel):
    url: str
    target_price: Decimal
    check_interval_minutes: int = 60
    manual_price: Optional[Decimal] = None
    manual_name: Optional[str] = None
    manual_currency: Optional[str] = None
    
    @field_validator('check_interval_minutes')
    @classmethod
    def validate_interval(cls, v):
        if v < 15:
            raise ValueError('Check interval must be at least 15 minutes')
        return v
    
    @field_validator('target_price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Target price must be positive')
        return v
    
    @field_validator('manual_price')
    @classmethod
    def validate_manual_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Manual price must be positive')
        return v

class ProductUpdate(BaseModel):
    check_interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    
    @field_validator('check_interval_minutes')
    @classmethod
    def validate_interval(cls, v):
        if v is not None and v < 15:
            raise ValueError('Check interval must be at least 15 minutes')
        return v

class ProductResponse(BaseModel):
    id: int
    user_id: int
    url: str
    name: Optional[str]
    current_price: Optional[Decimal]
    currency: Optional[str]
    image_url: Optional[str]
    is_active: bool
    check_interval_minutes: int
    last_checked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductWithAlerts(ProductResponse):
    alert_count: int = 0

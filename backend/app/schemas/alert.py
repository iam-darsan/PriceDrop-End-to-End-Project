from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

class AlertCreate(BaseModel):
    target_price: Decimal
    
    @field_validator('target_price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Target price must be positive')
        return v

class AlertUpdate(BaseModel):
    target_price: Optional[Decimal] = None
    is_active: Optional[bool] = None
    
    @field_validator('target_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Target price must be positive')
        return v

class AlertResponse(BaseModel):
    id: int
    product_id: int
    target_price: Decimal
    is_active: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: Decimal
    recorded_at: datetime
    
    class Config:
        from_attributes = True

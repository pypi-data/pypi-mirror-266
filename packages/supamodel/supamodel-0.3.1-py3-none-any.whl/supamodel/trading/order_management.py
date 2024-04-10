from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from supamodel._core import BaseModel
from supamodel.enums import OrderSide, OrderStatus, OrderType


class Trade(BaseModel):
    id: Optional[UUID] = Field(description="Unique identifier of the trade")
    position_id: UUID = Field(description="ID of the associated position")
    order_id: UUID = Field(description="ID of the associated order")
    quantity: float = Field(description="Quantity of the asset traded")
    price: float = Field(description="Price at which the trade occurred")
    fee: float = Field(description="Fee charged for the trade")
    timestamp: datetime = Field(description="Timestamp of when the trade occurred")
    created_at: Optional[datetime] = Field(
        description="Timestamp of when the trade record was created"
    )


class Order(BaseModel):
    id: Optional[UUID] = Field(description="Unique identifier of the order")
    portfolio_id: UUID = Field(description="ID of the associated portfolio")
    asset_id: UUID = Field(description="ID of the associated asset")
    exchange_id: UUID = Field(description="ID of the associated exchange")
    order_type: OrderType = Field(description="Type of the order (e.g., limit, market)")
    side: OrderSide = Field(description="Side of the order (buy or sell)")
    quantity: float = Field(description="Quantity of the asset to be traded")
    price: Optional[float] = Field(
        description="Price at which the order should be executed (for limit orders)"
    )
    status: OrderStatus = Field(description="Current status of the order")
    created_at: Optional[datetime] = Field(
        description="Timestamp of when the order was created"
    )
    updated_at: Optional[datetime] = Field(
        description="Timestamp of when the order was last updated"
    )

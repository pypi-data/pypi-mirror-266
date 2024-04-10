from typing import Optional
from uuid import UUID, uuid4

from pendulum import DateTime
from pydantic import Field

from supamodel._core import BaseModel


class Portfolio(BaseModel):
    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier of the portfolio"
    )
    user_id: Optional[UUID] = Field(
        description="ID of the user associated with the portfolio"
    )
    name: str = Field(description="Name of the portfolio")
    exchange_id: Optional[UUID] = Field(
        description="ID of the exchange associated with the portfolio"
    )
    base_currency_id: Optional[UUID] = Field(
        description="ID of the base currency of the portfolio"
    )
    created_at: DateTime | None = Field(
        default_factory=DateTime.now,
        description="Timestamp of when the portfolio was created",
    )
    updated_at: DateTime | None = Field(
        default_factory=DateTime.now,
        description="Timestamp of when the portfolio was last updated",
    )
    balance: float = Field(
        default=0.0, description="The total balance of the portfolio"
    )


class Position(BaseModel):
    id: Optional[UUID] = Field(description="Unique identifier of the position")
    portfolio_id: UUID = Field(description="ID of the associated portfolio")
    asset_id: UUID = Field(description="ID of the associated asset")
    quantity: float = Field(
        description="Quantity of the asset held in the position", alias="amount"
    )
    average_price: float = Field(
        alias="value", description="Average price of the asset in the position"
    )
    created_at: Optional[DateTime] = Field(
        description="Timestamp of when the position was created"
    )
    updated_at: Optional[DateTime] = Field(
        description="Timestamp of when the position was last updated"
    )

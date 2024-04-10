from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import pendulum as pdm
from galapy.models.core import BaseModel, CamelModel, Data
from microbots.birdeye.enums import TimeIntSQL
from pydantic import Field, model_validator


def now_utc():
    return pdm.now("UTC")


class PriceBar(CamelModel):
    address: str | None = Field(None, repr=False)
    interval: TimeIntSQL = Field(..., alias="type")
    close: float = Field(..., alias="c")
    high: float = Field(..., alias="h")
    low: float = Field(..., alias="l")
    open: float = Field(..., alias="o")
    volume: int = Field(..., alias="v")
    timestamp: datetime = Field(..., alias="unixTime")


class Price(Data):
    address: str = Field(..., exclude=True, repr=False)
    price: float
    timestamp: datetime


class PriceBarInput(BaseModel):
    asset_id: Optional[UUID] = None
    prices: list[PriceBar] | PriceBar | None = None

    @model_validator(mode="after")
    def convert_price_list(self) -> Any:
        if self.prices is None:
            return self

        if self.asset_id is None:
            raise ValueError("Asset ID is required")
        if isinstance(self.prices, list):
            return self
        if isinstance(self.prices, PriceBar):
            self.prices = [self.prices]

            return self
        return self

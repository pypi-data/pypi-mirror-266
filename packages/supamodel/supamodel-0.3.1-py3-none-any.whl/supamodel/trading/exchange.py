import abc
from typing import Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import UUID4, ConfigDict, Field, computed_field

from supamodel._abc import BaseModel, IgnoreModel
from supamodel._types import CapitalStr
from supamodel.enums import Chain

DataT = TypeVar("DataT")


class ExchangeBase(BaseModel):
    name: str = Field(description="Name of the exchange")
    description: Optional[str] = None
    maker_fee: float = 0.0001
    taker_fee: float = 0.0001
    url: str | None = None


class Currency(IgnoreModel):
    code: str
    name: str


class BaseAsset(abc.ABC, BaseModel):
    id: UUID | None = None
    # name: str
    name: CapitalStr
    base: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Base currency name used to find base currency ID. Hidden from model_dump",
        repr=False,
    )
    trade: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Trade currency name used to find trade currency ID. Hidden from model_dump",
        repr=False,
    )
    exchange: Optional[CapitalStr] = Field(
        default=None,
        exclude=True,
        description="Exchange name used to find exchange ID. Hidden from model_dump",
        repr=False,
    )
    base_currency_id: Optional[UUID] = Field(None, description="Base currency ID")
    trade_currency_id: Optional[UUID] = Field(None, description="Trade currency ID")
    exchange_id: Optional[UUID] = Field(None, description="Exchange ID")

    # decimals: Optional[int] = Field(6, description="The number of integers to measure everything by.")
    # @computed_field
    @property
    def is_defi(self) -> bool:
        return False

    # @computed_field
    @property
    def is_wrapped(self) -> bool:
        return False


class ExchangeID(IgnoreModel):
    exchange_id: str
    name: str


class ChainDefaults(BaseModel):
    exchanges: Optional[list[CapitalStr]] = []
    currencies: Optional[list[Currency]] = []
    default_exchange: Optional[CapitalStr] = None
    default_currency: Optional[str] = None


class CurrencyID(Currency):
    currency_id: str

    @staticmethod
    def from_base(self, currency: Currency, currency_id: str) -> "CurrencyID":
        return CurrencyID(currency_id=currency_id, **currency.model_dump())


class ExchangeCreate(ExchangeBase):
    pass


class Exchange(ExchangeBase):
    id: UUID4 = Field(
        default_factory=uuid4,
        alias="exchange_id",
        description="Unique identifier of the exchange",
    )

    model_config = ConfigDict(from_attributes=True)


class Asset(BaseAsset):
    @computed_field
    def is_wrapped(self) -> bool:
        return False

    @computed_field
    def is_defi(self) -> bool:
        return False


class ChainAsset(BaseAsset):
    chain: Chain
    symbol: str
    decimals: Optional[int] = Field(
        6, description="The number of integers to measure everything by."
    )
    address: Optional[str] = Field(
        description="If the asset is a defi token, it'll have an address representing mint location."
    )
    is_meme: Optional[bool] = Field(False, description="Is the asset a meme token?")

    @computed_field
    def is_wrapped(self) -> bool:
        lower_name = self.name.lower()
        return "wrapped" in lower_name or "wrap" in lower_name

    @computed_field
    def is_defi(self) -> bool:
        return bool(self.address) and bool(self.chain)

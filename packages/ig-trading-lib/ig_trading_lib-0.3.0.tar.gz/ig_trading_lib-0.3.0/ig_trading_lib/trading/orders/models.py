from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal, Any

from pydantic import (
    BaseModel,
    condecimal,
    field_validator,
    constr,
    model_validator,
    field_serializer,
)
from ..models import InstrumentType, Direction


OrderType = Literal["LIMIT", "STOP"]


TimeInForce = Literal["GOOD_TILL_CANCELLED", "GOOD_TILL_DATE"]


MarketStatus = Literal[
    "CLOSED",
    "EDITS_ONLY",
    "OFFLINE",
    "ON_AUCTION",
    "ON_AUCTION_NO_EDITS",
    "SUSPENDED",
    "TRADEABLE",
]


class MarketData(BaseModel):
    instrumentName: str
    exchangeId: str
    expiry: str
    marketStatus: MarketStatus
    epic: str
    instrumentType: InstrumentType
    lotSize: condecimal(decimal_places=2)
    high: condecimal(decimal_places=2)
    low: condecimal(decimal_places=2)
    percentageChange: condecimal(decimal_places=2)
    netChange: condecimal(decimal_places=2)
    bid: condecimal(decimal_places=2)
    offer: condecimal(decimal_places=2)
    updateTime: str
    updateTimeUTC: str
    delayTime: int
    streamingPricesAvailable: bool
    scalingFactor: int


class WorkingOrderData(BaseModel):
    dealId: str
    direction: Direction
    epic: str
    orderSize: condecimal(decimal_places=2)
    orderLevel: condecimal(decimal_places=2)
    timeInForce: TimeInForce
    goodTillDate: Optional[datetime] = None
    goodTillDateISO: Optional[datetime] = None
    createdDate: datetime
    createdDateUTC: datetime
    guaranteedStop: bool
    orderType: OrderType
    stopDistance: Optional[condecimal(decimal_places=2)] = None
    limitDistance: Optional[condecimal(decimal_places=2)] = None
    currencyCode: str
    dma: Optional[bool] = None
    limitedRiskPremium: Optional[condecimal(decimal_places=2)] = None

    @field_validator("goodTillDate", mode="before")
    @classmethod
    def parse_good_till_date(cls, v: Optional[str]) -> Optional[datetime]:
        if v is not None:
            try:
                return datetime.strptime(v, "%Y/%m/%d %H:%M")
            except ValueError:
                raise ValueError(f"Invalid datetime format for goodTillDate value {v}")

    @field_validator("createdDate", mode="before")
    @classmethod
    def parse_created_date(cls, v: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.strptime(v, "%Y/%m/%d %H:%M:%S:%f")
        except ValueError:
            raise ValueError(f"Invalid datetime format for createdDate value {v}")


class WorkingOrder(BaseModel):
    workingOrderData: WorkingOrderData
    marketData: MarketData


class WorkingOrders(BaseModel):
    workingOrders: List[WorkingOrder]


class CreateWorkingOrder(BaseModel):
    currencyCode: constr(pattern="[A-Z]{3}")
    direction: Direction
    epic: str
    expiry: constr(pattern="(\\d{2}-)?[A-Z]{3}-\\d{2}|-|DFB")
    forceOpen: bool = False
    goodTillDate: constr(pattern="(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2}:\\d{2}|\\d*)")
    level: condecimal(decimal_places=2)
    size: condecimal(decimal_places=12)
    type: OrderType
    guaranteedStop: bool = False
    timeInForce: TimeInForce = "GOOD_TILL_CANCELLED"
    dealReference: Optional[str] = None
    limitDistance: Optional[condecimal(decimal_places=2)] = None
    limitLevel: Optional[condecimal(decimal_places=2)] = None
    stopDistance: Optional[condecimal(decimal_places=2)] = None
    stopLevel: Optional[condecimal(decimal_places=2)] = None

    @field_serializer(
        "level",
        "size",
        "limitDistance",
        "limitLevel",
        "stopDistance",
        "stopLevel",
        mode="plain",
    )
    def serialize_decimal(self, v: Optional[Decimal], _info) -> float:
        if v is not None:
            return float(v)

    @model_validator(mode="before")
    @classmethod
    def check_unique_constraints(cls, data: Any):
        """[Constraint: Set only one of {limitLevel,limitDistance}]
        [Constraint: Set only one of {stopLevel,stopDistance}]"""
        if data.get("limitLevel") is not None and data.get("limitDistance") is not None:
            raise ValueError("Set only one of limitLevel or limitDistance.")
        if data.get("stopLevel") is not None and data.get("stopDistance") is not None:
            raise ValueError("Set only one of stopLevel or stopDistance.")
        return data

    @model_validator(mode="before")
    @classmethod
    def validate_good_till_date(self, data: Any):
        if (
            data.get("timeInForce") == "GOOD_TILL_DATE"
            and data.get("goodTillDate") is None
        ):
            raise ValueError(
                "timeInForce GOOD_TILL_DATE requires a goodTillDate value."
            )
        return data

    @model_validator(mode="before")
    @classmethod
    def check_guaranteed_stop_constraints(cls, data: Any):
        if data.get("guaranteedStop") and not (
            bool(data.get("stopLevel")) ^ bool(data.get("stopDistance"))
        ):
            raise ValueError(
                "When guaranteedStop is true, specify exactly one of stopLevel or stopDistance."
            )
        return data

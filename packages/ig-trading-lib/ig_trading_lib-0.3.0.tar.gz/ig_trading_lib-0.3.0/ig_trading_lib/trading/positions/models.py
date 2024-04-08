from decimal import Decimal
from typing import List, Any, Literal, Optional

from pydantic import (
    BaseModel,
    constr,
    condecimal,
    conint,
    model_validator,
    field_serializer,
)
from ..models import InstrumentType, Direction


MarketStatusType = Literal[
    "TRADEABLE",
    "CLOSED",
    "EDITS_ONLY",
    "OFFLINE",
    "ON_AUCTION",
    "ON_AUCTION_NO_EDITS",
    "SUSPENDED",
]

OrderType = Literal["LIMIT", "MARKET", "QUOTE"]

TimeInForce = Literal["EXECUTE_AND_ELIMINATE", "FILL_OR_KILL"]


class Market(BaseModel):
    instrumentName: str
    expiry: str
    epic: str
    instrumentType: InstrumentType
    lotSize: float
    high: float
    low: float
    percentageChange: float
    netChange: float
    bid: float
    offer: float
    updateTime: str
    updateTimeUTC: str
    delayTime: int
    streamingPricesAvailable: bool
    marketStatus: MarketStatusType
    scalingFactor: int


class Position(BaseModel):
    contractSize: condecimal(decimal_places=2)
    controlledRisk: bool
    createdDate: str
    createdDateUTC: str
    currency: str
    dealId: str
    dealReference: str
    direction: Direction
    level: condecimal(decimal_places=2)
    limitLevel: Optional[condecimal(decimal_places=2)] = None
    limitedRiskPremium: Optional[condecimal(decimal_places=2)] = None
    size: condecimal(decimal_places=2)
    stopLevel: Optional[condecimal(decimal_places=2)] = None
    trailingStep: Optional[conint(ge=0)] = None
    trailingStopDistance: Optional[condecimal(decimal_places=2)] = None


class OpenPosition(BaseModel):
    position: Position
    market: Market


class OpenPositions(BaseModel):
    positions: List[OpenPosition]


class CreatePosition(BaseModel):
    currencyCode: constr(pattern=r"^[A-Z]{3}$")
    direction: Direction
    epic: constr(pattern=r"^[A-Za-z0-9._]{6,30}$")
    expiry: constr(pattern=r"^(\d{2}-)?[A-Z]{3}-\d{2}|-|DFB$")
    forceOpen: bool
    guaranteedStop: bool
    orderType: OrderType
    timeInForce: TimeInForce
    trailingStop: bool
    dealReference: Optional[constr(pattern=r"^[A-Za-z0-9_\-.]{1,30}$")] = None
    level: Optional[condecimal(decimal_places=12)] = None
    limitDistance: Optional[condecimal(decimal_places=2)] = None
    limitLevel: Optional[condecimal(decimal_places=2)] = None
    quoteId: Optional[constr(pattern=r"^[A-Za-z0-9]+$")] = None
    size: condecimal(decimal_places=2, gt=0)
    stopDistance: Optional[condecimal(decimal_places=2)] = None
    stopLevel: Optional[condecimal(decimal_places=2)] = None
    trailingStopIncrement: Optional[condecimal(decimal_places=2)] = None

    @field_serializer(
        "level",
        "limitDistance",
        "limitLevel",
        "size",
        "stopDistance",
        "stopLevel",
        "trailingStopIncrement",
        mode="plain",
    )
    def serialize_decimal(self, v: Optional[Decimal], _info) -> float:
        if v is not None:
            return float(v)

    @model_validator(mode="before")
    @classmethod
    def check_unique_constraints(cls, data: Any):
        if data.get("limitLevel") is not None and data.get("limitDistance") is not None:
            raise ValueError("Set only one of limitLevel or limitDistance.")
        if data.get("stopLevel") is not None and data.get("stopDistance") is not None:
            raise ValueError("Set only one of stopLevel or stopDistance.")
        return data

    @model_validator(mode="before")
    @classmethod
    def check_force_open_constraints(cls, data: Any):
        if not data.get("forceOpen") and any(
            [
                data.get("limitDistance") is not None,
                data.get("limitLevel") is not None,
                data.get("stopDistance") is not None,
                data.get("stopLevel") is not None,
            ]
        ):
            raise ValueError(
                "forceOpen must be true if limit or stop constraints are set."
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

    @model_validator(mode="before")
    @classmethod
    def check_order_type_constraints(cls, data: Any):
        order_type = data.get("orderType")
        if order_type == "LIMIT":
            if data.get("quoteId") is not None:
                raise ValueError("Do not set quoteId when orderType is LIMIT.")
            if data.get("level") is None:
                raise ValueError("Set level when orderType is LIMIT.")
        elif order_type == "MARKET":
            if any([data.get("level") is not None, data.get("quoteId") is not None]):
                raise ValueError(
                    "Do not set level or quoteId when orderType is MARKET."
                )
        elif order_type == "QUOTE":
            if not all(
                [data.get("level") is not None, data.get("quoteId") is not None]
            ):
                raise ValueError("Set both level and quoteId when orderType is QUOTE.")
        return data

    @model_validator(mode="before")
    @classmethod
    def check_trailing_stop_constraints(cls, data: Any):
        if data.get("trailingStop"):
            if data.get("stopLevel") is not None:
                raise ValueError("Do not set stopLevel when trailingStop is true.")
            if data.get("guaranteedStop"):
                raise ValueError(
                    "guaranteedStop must be false when trailingStop is true."
                )
            if not all(
                [
                    data.get("stopDistance") is not None,
                    data.get("trailingStopIncrement") is not None,
                ]
            ):
                raise ValueError(
                    "Set both stopDistance and trailingStopIncrement when trailingStop is true."
                )
        return data


class ClosePosition(BaseModel):
    direction: Direction
    orderType: OrderType
    size: condecimal(gt=0, decimal_places=2)
    timeInForce: TimeInForce
    quoteId: Optional[str] = None
    dealId: Optional[constr(pattern=".{1,30}")] = None
    epic: Optional[constr(pattern="[A-Za-z0-9._]{6,30}")] = None
    expiry: Optional[constr(pattern="(\\d{2}-)?[A-Z]{3}-\\d{2}|-|DFB")] = None
    level: Optional[condecimal(decimal_places=12)] = None

    @field_serializer("level", "size", mode="plain")
    def serialize_decimal(self, v: Optional[Decimal], _info) -> Optional[float]:
        if v is not None:
            return float(v)

    @model_validator(mode="before")
    @classmethod
    def check_order_type(cls, data: Any):
        if data.get("orderType") == "QUOTE" and (
            data.get("quoteId") is None or data.get("level") is None
        ):
            raise ValueError("quoteId is required when orderType is QUOTE.")

        if (
            data.get("orderType") == "MARKET"
            and (data.get("level") is not None or data.get("quoteId")) is not None
        ):
            raise ValueError(
                "level and quoteId are not allowed when orderType is MARKET."
            )

        if data.get("orderType") == "LIMIT" and data.get("quoteId") is not None:
            raise ValueError("quoteId is not allowed when orderType is LIMIT.")

        if data.get("orderType") == "LIMIT" and data.get("level") is None:
            raise ValueError("level is required when orderType is LIMIT.")

        return data

    @model_validator(mode="before")
    @classmethod
    def check_unique_constraints(cls, data: Any):
        if data.get("dealId") is not None and data.get("epic") is not None:
            raise ValueError("Set only one of dealId or epic.")
        if data.get("dealId") is None and data.get("epic") is None:
            raise ValueError("Set one of dealId or epic.")
        return data

    @classmethod
    def from_create(cls, position: CreatePosition):
        """Create a ClosePosition from a CreatePosition.
        :param position: CreatePosition. The position to close.
        :return: ClosePosition. The position to close.
        """
        return cls(
            direction="BUY" if position.direction == "SELL" else "SELL",
            orderType=position.orderType,
            size=position.size,
            timeInForce=position.timeInForce,
            epic=position.epic,
            expiry=position.expiry,
            level=position.level,
        )


class UpdatePosition(BaseModel):
    guaranteedStop: Optional[bool] = None
    limitLevel: Optional[condecimal(decimal_places=2)] = None
    stopLevel: Optional[condecimal(decimal_places=2)] = None
    trailingStop: Optional[bool] = None
    trailingStopDistance: Optional[condecimal(decimal_places=2)] = None
    trailingStopIncrement: Optional[condecimal(decimal_places=2)] = None

    @field_serializer(
        "limitLevel",
        "stopLevel",
        "trailingStopDistance",
        "trailingStopIncrement",
        mode="plain",
    )
    @classmethod
    def serialize_decimal(cls, v: Optional[Decimal], _info) -> Optional[float]:
        if v is not None:
            return float(v)

    @model_validator(mode="before")
    @classmethod
    def validate_trailing_stop_constraints(cls, data: dict):
        if data.get("trailingStop"):
            cls._validate_trailing_stop_true(data)
        elif data.get("trailingStop") == False:
            cls._validate_trailing_stop_false(data)
        return data

    @model_validator(mode="before")
    @classmethod
    def validate_guaranteed_stop_constraints(cls, data: dict):
        if data.get("guaranteedStop"):
            cls._validate_guaranteed_stop_true(data)
        return data

    @classmethod
    def _validate_trailing_stop_true(cls, data: dict):
        if data.get("guaranteedStop"):
            raise ValueError(
                "If trailingStop is true, then guaranteedStop must be false."
            )
        if any(
            data.get(field) is None
            for field in ["trailingStopDistance", "trailingStopIncrement", "stopLevel"]
        ):
            raise ValueError(
                "If trailingStop is true, then trailingStopDistance, trailingStopIncrement, and stopLevel must be set."
            )

    @classmethod
    def _validate_trailing_stop_false(cls, data: dict):
        if any(
            data.get(field) is not None
            for field in ["trailingStopDistance", "trailingStopIncrement"]
        ):
            raise ValueError(
                "If trailingStop is false, then DO NOT set trailingStopDistance or trailingStopIncrement."
            )

    @classmethod
    def _validate_guaranteed_stop_true(cls, data: dict):
        if data.get("stopLevel") is None:
            raise ValueError("If guaranteedStop is true, then stopLevel must be set.")
        if data.get("trailingStop"):
            raise ValueError("guaranteedStop and trailingStop cannot both be true.")

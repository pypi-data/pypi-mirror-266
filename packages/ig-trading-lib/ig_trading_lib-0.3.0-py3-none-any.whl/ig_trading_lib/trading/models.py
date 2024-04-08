from typing import Literal
from pydantic import BaseModel


class DealReference(BaseModel):
    dealReference: str


InstrumentType = Literal[
    "SHARES",
    "BINARY",
    "BUNGEE_CAPPED",
    "BUNGEE_COMMODITIES",
    "BUNGEE_CURRENCIES",
    "BUNGEE_INDICES",
    "COMMODITIES",
    "CURRENCIES",
    "INDICES",
    "KNOCKOUTS_COMMODITIES",
    "KNOCKOUTS_CURRENCIES",
    "KNOCKOUTS_INDICES",
    "KNOCKOUTS_SHARES",
    "OPT_COMMODITIES",
    "OPT_CURRENCIES",
    "OPT_INDICES",
    "OPT_RATES",
    "OPT_SHARES",
    "RATES",
    "SECTORS",
    "SPRINT_MARKET",
    "TEST_MARKET",
    "UNKNOWN",
]


Direction = Literal["BUY", "SELL"]
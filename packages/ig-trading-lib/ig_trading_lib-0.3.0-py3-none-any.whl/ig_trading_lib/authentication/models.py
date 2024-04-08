from collections import namedtuple
from typing import List, Optional

from pydantic import BaseModel


Tokens = namedtuple("Tokens", ["cst_token", "x_security_token"])


class AccountFinancials(BaseModel):
    balance: float
    deposit: float
    profitLoss: float
    available: float


class AccountSummary(BaseModel):
    accountId: str
    accountName: str
    preferred: bool
    accountType: str


class AccountInfo(BaseModel):
    accountType: str
    accountInfo: AccountFinancials
    currencyIsoCode: str
    currencySymbol: str
    currentAccountId: str
    lightstreamerEndpoint: str
    accounts: List[AccountSummary]
    clientId: str
    timezoneOffset: int
    hasActiveDemoAccounts: bool
    hasActiveLiveAccounts: bool
    trailingStopsEnabled: bool
    reroutingEnvironment: Optional[str] = None
    dealingEnabled: bool


class AuthenticationResponse(BaseModel):
    cst_token: str
    x_security_token: str
    expiry: Optional[int] = None
    account_info: Optional[AccountInfo] = None

    @property
    def tokens(self) -> Tokens:
        return Tokens(self.cst_token, self.x_security_token)

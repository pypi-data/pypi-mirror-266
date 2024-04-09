from enum import Enum
from typing import Optional

STATUS = "status"  # type: str
ERROR_CODE = "errorCode"  # type: str
ERROR_MESSAGE = "message"  # type: str
ERROR = "error"  # type: str


# class ErrorCode(Enum):
#     BAD_REQUEST_ERROR = "BadRequestError"
#     INTERNAL_SERVER_ERROR = "InternalServerError"
#     NETWORK_ERROR = "NetworkError"
#     NOT_FOUND_ERROR = "NotFoundError"
#     SOMETHING_WENT_WRONG_ERROR = "SomethingWrongError"
#     TOO_MANY_REQUESTS_ERROR = "TooManyRequests"
#     INTERNAL_ERROR = "InternalError"

class BaseEnum(Enum):
    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class Routes:
    _home_url = "https://app.tiqs.in/app/login"
    _root_url = "https://api.tiqs.trading"

    def __init__(self, root_url: Optional[str] = None) -> None:
        if root_url:
            self._root_url = root_url.strip()

    def get_home_url(self) -> str:
        return self._home_url

    def __getattr__(self, name: str) -> str:
        if name in _PATHS.__members__:
            endpoint_path = _PATHS[name].value
            return "{root_url}{endpoint_path}".format(root_url=self._root_url, endpoint_path=endpoint_path)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class _PATHS(BaseEnum):
    WEB_LOGIN_URL = ""

    AUTHENTICATE_TOKEN = "/auth/app/authenticate-token"
    ALL_INSTRUMENTS = "/all"
    ORDER_MARGIN = "/margin/order"
    BASKET_ORDER_MARGIN = "/margin/basket"
    USER_DETAILS = "/user/details"
    HOLIDAYS_LIST = "/info/holidays"
    INDEX_LIST = "/info/index-list"
    OPTION_CHAIN = "/info/option-chain"
    GET_ORDER_BY_ID = "/order/{order_id}"
    GET_USER_ORDERS = "/user/orders"
    GET_USER_TRADES = "/user/trades"
    GET_USER_LIMITS = "/user/limits"
    GET_USER_POSITIONS = "/user/positions"
    PLACE_ORDER = "/order/{variety}"
    UPDATE_ORDER_BY_ID = "/order/regular/{order_id}"
    DELETE_ORDER = "/order/regular/{order_id}"
    GET_HISTORICAL_DATA = "/candle/{exchange}/{token}/{interval}"


class Variety(BaseEnum):
    REGULAR = "regular"
    COVER = "cover"


class Exchange(BaseEnum):
    NSE = "NSE"
    NFO = "NFO"


class TransactionType(BaseEnum):
    BUY = "B"
    SELL = "S"


class OrderType(BaseEnum):
    MARKET = "MKT"
    LIMIT = "LMT"
    STOP_LOSS_LIMIT = "SL-LMT"
    STOP_LOSS_MARKET = "SL-MKT"


class Retention(BaseEnum):
    DAY = "DAY"
    IOC = "IOC"


class ProductType(BaseEnum):
    MIS = "I"
    CNC = "C"
    NRML = "M"

import csv
import datetime
import json
import logging
import traceback

import dateutil.parser
import requests
import urllib3
import hashlib
import tiqs.exceptions as ex

import tiqs.constants as constants
from tiqs.constants import Variety, Exchange, ProductType, TransactionType, OrderType, Retention

from typing import Dict, Any, Optional, List, Union
from six import StringIO, PY2
from tiqs.__version__ import __version__, __title__

log = logging.getLogger(__name__)


class Tiqs(object):
    _default_timeout = 5  # type: int
    _token = None

    def __init__(
            self, app_id: str,
            timeout: Optional[int] = None,
            debug: bool = False,
            root_url: Optional[str] = None,
            pool: Optional[Dict[str, Any]] = None
    ) -> None:
        self.app_id = app_id
        self.debug = debug
        self.disable_ssl = False
        self.timeout = timeout or self._default_timeout
        self.proxies = {}  # type: Dict[str, str]
        self._routes = constants.Routes(root_url)

        # Create requests session by default
        self.req_session = requests.Session()  # type: requests.Session
        if pool:
            req_adapter = requests.adapters.HTTPAdapter(**pool)
            self.req_session.mount("https://", req_adapter)

        # disable requests SSL warning
        urllib3.disable_warnings()

    def login_url(self) -> str:
        return "%s?appId=%s" % (self._routes.get_home_url(), self.app_id)

    def generate_session(self, request_token: str, api_secret: str) -> None:
        checksum_formula = "{app_id}:{api_secret}:{request_token}".format(app_id=self.app_id, api_secret=api_secret,
                                                                          request_token=request_token)
        checksum = hashlib.sha256(checksum_formula.encode("utf-8")).hexdigest()

        resp = self._post(self._routes.AUTHENTICATE_TOKEN, params={
            "appId": self.app_id,
            "token": request_token,
            "checkSum": checksum
        })  # type: Dict[str, str]

        if "token" in resp:
            if self.debug:
                log.debug("token received from generate_session: " + resp["token"])
            self.set_token(resp["token"])

    def set_token(self, value: str) -> None:
        self._token = value

    def invalidate_session(self) -> None:
        self._token = None

    def get_instruments(self) -> Any:
        return self._parse_instrument(self._get(self._routes.ALL_INSTRUMENTS))

    def user_details(self) -> Dict[str, Any]:
        return self._get(self._routes.USER_DETAILS)

    def user_limits(self) -> List[Dict[str, Any]]:
        return self._parse_user_limits(self._get(self._routes.GET_USER_LIMITS))

    def holidays(self) -> Dict[str, Any]:
        return self._get(self._routes.HOLIDAYS_LIST)

    def index_list(self) -> List[Dict[str, str]]:
        return self._get(self._routes.INDEX_LIST)

    def historical_data(self,
                        exchange: str,
                        instrument_token: str,
                        from_time: datetime.datetime,
                        to_time: datetime.datetime,
                        interval: str,
                        ) -> List[Any]:
        from_string = from_time.strftime('%Y-%m-%dT%H:%M:%S')
        to_string = to_time.strftime('%Y-%m-%dT%H:%M:%S')
        data = self._get(
            self._routes.GET_HISTORICAL_DATA,
            url_args={"exchange": exchange, "token": instrument_token, "interval": interval},
            params={"from": from_string, "to": to_string}
        )
        return self._parse_historical_data(data)

    def option_chain(self, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        :param params: {
            "token": "26009",
            "exchange": "INDEX",
            "count": "20"
            "expiry": "10-APR-2024"
        }
        :return:
        """
        return self._parse_option_chain(self._post(self._routes.OPTION_CHAIN, params=params))

    def order_margin(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate margins for requested order considering the existing positions and open orders
        """
        return self._post(self._routes.ORDER_MARGIN, params=params)

    def basket_order_margin(self, params: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Calculate the margin required for a basket
        """
        return self._post(self._routes.BASKET_ORDER_MARGIN, params=params)

    def get_order(self, order_id: str) -> List[Dict[str, Any]]:
        """
        The Order Details endpoint gives the details for a particular order placed.
        :param order_id: str
        :return:
        """
        return self._format_order_by_id_response(
            self._get(self._routes.GET_ORDER_BY_ID, url_args={"order_id": order_id}))

    def get_user_orders(self) -> List[Dict[str, Any]]:
        """
        The Order Book allows the user to fetch all the orders for the current trading day
        """
        return self._format_user_orders_response(self._get(self._routes.GET_USER_ORDERS))

    def get_user_trades(self) -> List[Dict[str, Any]]:
        """
        The Order Book allows the user to fetch all the orders for the current trading day
        """
        return self._format_user_trades_response(self._get(self._routes.GET_USER_TRADES))

    def get_positions(self) -> List[Dict[str, Any]]:
        return self._get(self._routes.GET_USER_POSITIONS)

    def place_order(
            self,
            exchange: Exchange,
            token: str,
            qty: int,
            disclosed_qty: int,
            product: ProductType,
            symbol: str,
            transaction_type: TransactionType,
            order_type: OrderType,
            variety: Variety,
            price: float,
            validity: Retention,
            tags: Optional[str] = None,
            amo: bool = False,
            trigger_price: Optional[float] = None
    ) -> str:
        params = dict(
            exchange=str(exchange),
            token=token,
            quantity="{qty}".format(qty=qty),
            disclosedQty="{disclosed_qty}".format(disclosed_qty=disclosed_qty),
            product=str(product),
            symbol=symbol,
            transactionType=str(transaction_type),
            order=str(order_type),
            price="{price}".format(price=price),
            validity=str(validity),
            tags=tags or "",
            amo=amo,
            triggerPrice="{trigger_price}".format(trigger_price=trigger_price or "")
        )  # type: Dict[str, Any]
        return self._post(
            self._routes.PLACE_ORDER,
            url_args={"variety": str(variety)},
            params=params
        )["orderNo"]

    def modify_order_by_id(
            self,
            order_id: str,
            exchange: Exchange,
            token: str,
            qty: int,
            disclosed_qty: int,
            product: ProductType,
            transaction_type: TransactionType,
            order_type: OrderType,
            price: float,
            validity: Retention,
            amo: bool = False,
            trigger_price: Optional[float] = None,
            tags: Optional[str] = None,
            book_loss_price: Optional[float] = None,
            book_profit_price: Optional[float] = None
    ) -> str:
        params = dict(
            exchange=str(exchange),
            token=token,
            quantity="{qty}".format(qty=qty),
            disclosedQty="{disclosed_qty}".format(disclosed_qty=disclosed_qty),
            product=str(product),
            transactionType=str(transaction_type),
            order=str(order_type),
            price="{price}".format(price=price),
            validity=str(validity),
            tags=tags or "",
            amo=amo,
            triggerPrice="{trigger_price}".format(trigger_price=trigger_price or "0"),
            bookLossPrice="{book_loss_price}".format(book_loss_price=book_loss_price or ""),
            bookProfitPrice="{book_profit_price}".format(book_profit_price=book_profit_price or "")
        )  # type: Dict[str, Any]
        return self._patch(
            self._routes.UPDATE_ORDER_BY_ID,
            url_args={"order_id": order_id},
            params=params
        )["message"]

    def delete_order(self, order_id: str) -> str:
        return self._delete(self._routes.DELETE_ORDER, url_args={"order_id": order_id})["message"]

    def _parse_instrument(self, data: Any) -> Any:
        d = data
        if not PY2 and isinstance(d, bytes):
            d = data.decode("utf-8").strip()  # Decode unicode data

        records = []
        reader = csv.DictReader(StringIO(d))
        for row in reader:
            try:
                if row["LotSize"]:
                    row["LotSize"] = int(row["LotSize"])
                if row["TickSize"]:
                    row["TickSize"] = int(row["TickSize"])
                if row["PricePrecision"]:
                    row["PricePrecision"] = int(row["PricePrecision"])
                if row["Multiplier"]:
                    row["Multiplier"] = int(row["Multiplier"])
                if row["PriceMultiplier"]:
                    row["PriceMultiplier"] = float(row["PriceMultiplier"])
                if row["StrikePrice"]:
                    row["StrikePrice"] = float(row["StrikePrice"])
                records.append(row)
            except ValueError:
                if self.debug:
                    log.error(json.dumps(row), traceback.format_exc())
        return records

    def _get(self, route: str, url_args: Optional[Dict[str, str]] = None, params: Any = None) -> Any:
        return self._request(route, "GET", url_args=url_args, params=params)

    def _post(self,
              route: str,
              url_args: Optional[Dict[str, Any]] = None,
              params: Any = None,
              query_params: Any = None) -> Any:
        return self._request(route, "POST", url_args=url_args, params=params, query_params=query_params)

    def _patch(self,
               route: str,
               url_args: Optional[Dict[str, Any]] = None,
               params: Any = None,
               query_params: Any = None) -> Any:
        return self._request(route, "PATCH", url_args=url_args, params=params,
                             query_params=query_params)

    def _delete(self, route: str, url_args: Optional[Dict[str, str]] = None, params: Any = None,
                is_json: bool = False) -> Any:
        return self._request(route, "DELETE", url_args=url_args, params=params)

    def _request(self, route: str,
                 method: str,
                 url_args: Optional[Dict[str, str]] = None,
                 params: Any = None,
                 query_params: Any = None) -> Any:
        if url_args:
            uri = route.format(**url_args)
        else:
            uri = route

        url = uri

        headers = {
            "User-Agent": self._user_agent(),
            "appId": self.app_id
        }

        if self.token:
            headers["token"] = self.token

        if self.debug:
            log.debug(f"Request: {method} {url} {json.dumps(params)} {json.dumps(headers)}")

        if params is not None and method in ["GET", "DELETE"]:
            query_params = params

        try:
            r = self.req_session.request(method,
                                         url,
                                         json=params if (method in ["POST", "PUT", "PATCH"]) else None,
                                         data=None,
                                         params=query_params,
                                         headers=headers,
                                         verify=not self.disable_ssl,
                                         allow_redirects=True,
                                         timeout=self.timeout,
                                         proxies=self.proxies)
        except Exception as e:
            raise e

        if self.debug:
            log.debug('response: ' + method + " " + url + " " + f"\n{r.content[:1000]!r}")
        if "json" in r.headers["content-type"]:
            try:
                data = r.json()
            except ValueError:
                raise ex.DataException(f"Couldn't parse the JSON response received from the server: {r.content!r}")

            # historical data is in list format, so we need to return list data as it is
            if data and isinstance(data, dict):
                if data.get(constants.STATUS) == constants.ERROR or data.get(constants.ERROR_CODE):
                    if r.status_code == 403:
                        # TODO: expire session
                        pass

                    # if data.message does not exist, this will create general exception
                    exp = getattr(ex, str(data.get(constants.ERROR_CODE)), ex.GeneralException)
                    raise exp(data[constants.ERROR_MESSAGE], code=r.status_code)
                return data["data"]
            return data
        elif "octet-stream" in r.headers["content-type"]:
            return r.content
        else:
            raise ex.DataException(
                f"Unknown Content-Type ({r.headers['content-type']}) with response: ({r.content[:1000]!r})")

    @staticmethod
    def _user_agent() -> str:
        return (__title__ + "-python/") + __version__

    @staticmethod
    def _parse_user_limits(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        time_format = "%H:%M:%S %d-%m-%Y"
        records = []  # type: List[Dict[str, Any]]
        for record in data:
            rec = dict(record.items())
            if rec["cash"]:
                rec["cash"] = float(rec["cash"])
            if rec["dayCash"]:
                rec["dayCash"] = float(rec["dayCash"])
            if rec["blockedAmount"]:
                rec["blockedAmount"] = float(rec["blockedAmount"])
            if rec["unClearedCash"]:
                rec["unClearedCash"] = float(rec["unClearedCash"])
            if rec["brokerCollateralAmount"]:
                rec["brokerCollateralAmount"] = float(rec["brokerCollateralAmount"])
            if rec["payIn"]:
                rec["payIn"] = float(rec["payIn"])
            if rec["payOut"]:
                rec["payOut"] = float(rec["payOut"])
            if rec["marginUsed"]:
                rec["marginUsed"] = float(rec["marginUsed"])
            if rec["requestTime"]:
                rec["requestTime"] = dateutil.parser.parse(rec["requestTime"])
            records.append(rec)
        return records

    @staticmethod
    def _parse_option_chain(data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        records = []  # type: List[Dict[str, Any]]
        for row in data:
            rec = dict(row.items())  # type: Dict[str, Any]
            if rec["lotSize"]:
                rec["lotSize"] = int(rec["lotSize"])
            if rec["tickSize"]:
                rec["tickSize"] = float(rec["tickSize"])
            if rec["pricePrecision"]:
                rec["pricePrecision"] = int(rec["pricePrecision"])
            records.append(rec)
        return records

    @staticmethod
    def _parse_historical_data(data: List[Any]) -> List[Dict[str, Any]]:
        records = []
        for row in data:
            if len(row) < 6:
                continue
            record = {
                "time": dateutil.parser.parse(row[0]),  # 2024-03-22T09:15:00+0530
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5]
            }  # type: Dict[str, Any]
            records.append(record)
        return records

    @staticmethod
    def _format_order_by_id_response(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        _list = []
        if isinstance(data, list):
            _list = data
        elif isinstance(data, dict):
            _list = [data]

        for item in _list:
            # convert date time string to
            for field in ["timeStamp", "exchangeUpdateTime", "requestTime"]:
                if item.get(field) and len(item[field]) == 19:
                    item[field] = dateutil.parser.parse(item[field])

            # convert epoch time to int
            if item.get("orderTime"):
                item["orderTime"] = int(item["orderTime"])
        return _list

    @staticmethod
    def _format_user_orders_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        _list = data
        for item in data:
            # convert date time string to
            for field in ["timeStamp", "exchangeUpdateTime"]:
                if item.get(field) and len(item[field]) == 19:
                    item[field] = dateutil.parser.parse(item[field])

            # convert epoch time to int
            if item.get("orderTime"):
                item["orderTime"] = int(item["orderTime"])
        return data

    @staticmethod
    def _format_user_trades_response(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        _list = data
        for item in data:
            # convert date time string to
            for field in ["fillTime", "timeStamp", "exchangeUpdateTime", "requestTime"]:
                if item.get(field) and len(item[field]) == 19:
                    item[field] = dateutil.parser.parse(item[field])
        return data

    @property
    def token(self) -> str:
        return self._token or ""

    @token.setter
    def token(self, value: str) -> None:
        raise AttributeError("Cannot set my_var directly. Use set_my_var method instead.")

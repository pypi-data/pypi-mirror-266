import traceback

import numpy as np
import pandas as pd
import upstox_client
import asyncio
import threading
import ssl
import json
import websockets
from quantplay.exception.exceptions import (
    InvalidArgumentException,
    RetryableException,
    TokenException,
    retry_exception,
)
from retrying import retry
from upstox_client.rest import ApiException

from quantplay.broker.generics.broker import Broker
from quantplay.broker.uplink.uplink_utils import UplinkUtils
from quantplay.exception.exceptions import (
    InvalidArgumentException,
    QuantplayOrderPlacementException,
)
from quantplay.utils.constant import Constants, timeit


class Upstox(Broker):
    exchange_code_map = {
        "NFO": "NSE_FO",
        "CDS": "NSECD",
        "BFO": "BSEFO",
        "NSE": "NSE_EQ",
    }

    @timeit(MetricName="Upstox:__init__")
    def __init__(
        self,
        access_token=None,
        user_id=None,
        api_key=None,
        api_secret=None,
        totp=None,
        mobile_number=None,
        account_pin=None,
        redirect_url=None,
        load_instrument=True,
    ):
        try:
            if access_token:
                self.set_access_token(access_token)
                self.user_id = user_id
            else:
                access_token = self.generate_token(
                    api_key, api_secret, totp, mobile_number, account_pin, redirect_url
                )
                self.set_access_token(access_token)

                self.configuration = upstox_client.Configuration()
                self.configuration.access_token = self.access_token
                self.profile()
        except Exception as e:
            raise e

        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = self.access_token
        if load_instrument:
            self.load_instrument()
        super(Upstox, self).__init__()

    def load_instrument(self):
        super().load_instrument("upstox_instruments")

    def handle_exception(self, e):
        if "Unauthorized" in e.reason:
            raise TokenException("Token Expired")
        raise RetryableException(e.reason)

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_product(self, product):
        if product == "NRML":
            return "D"
        elif product == "CNC":
            return "D"
        elif product == "MIS":
            return "I"
        return product

    def get_exchange(self, exchange):
        if exchange in Upstox.exchange_code_map:
            return Upstox.exchange_code_map[exchange]

        return exchange

    def get_quantplay_exchange(self, exchange):
        exchange_map = {
            "NSE_FO": "NFO",
            "NSECD": "CDS",
            "BSEFO": "BFO",
            "NSE_EQ": "NSE",
        }
        if exchange in exchange_map:
            return exchange_map[exchange]
        return exchange

    def get_quantplay_symbol(self, symbol):
        return symbol

    def get_lot_size(self, exchange, tradingsymbol):
        return int(
            self.symbol_data["{}:{}".format(exchange, tradingsymbol)]["lot_size"]
        )

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:get_ltp")
    def get_ltp(self, exchange=None, tradingsymbol=None):
        # create an instance of the API class
        api_instance = upstox_client.MarketQuoteApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header

        try:
            symbol_info = self.symbol_data[f"{exchange}:{tradingsymbol}"]
            # Market quotes and instruments - LTP quotes.
            api_response = api_instance.ltp(symbol_info["instrument_key"], api_version)

            return api_response.data[
                f"{self.get_exchange(symbol_info['exchange'])}:{tradingsymbol}"
            ].last_price
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling MarketQuoteApi->ltp: %s\n" % e
            )
            self.handle_exception(e)

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:modify_order")
    def modify_order(self, data):
        if "trigger_price" not in data or data["trigger_price"] is None:
            data["trigger_price"] = 0
        # create an instance of the API class
        api_instance = upstox_client.OrderApi(
            upstox_client.ApiClient(self.configuration)
        )
        body = upstox_client.ModifyOrderRequest(
            validity="DAY",
            price=data["price"],
            order_id=data["order_id"],
            order_type=data["order_type"],
            trigger_price=data["trigger_price"],
        )
        api_version = "2.0"  # str | API Version Header

        try:
            # Modify order
            api_response = api_instance.modify_order(body, api_version)
            return api_response.status
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling OrderApi->modify_order: %s\n" % e
            )

            Constants.logger.info(
                "Modifying order [{}] new price [{}]".format(
                    data["order_id"], data["price"]
                )
            )
            self.handle_exception(e)

    @timeit(MetricName="Upstox:cancel_order")
    def cancel_order(self, order_id, variety="regular"):
        # create an instance of the API class
        api_instance = upstox_client.OrderApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header

        try:
            # Cancel order
            api_response = api_instance.cancel_order(order_id, api_version)
            return api_response.status
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling OrderApi->cancel_order: %s\n" % e
            )
            self.handle_exception(e)

    @timeit(MetricName="Upstox:place_order")
    def place_order(
        self,
        tradingsymbol=None,
        exchange=None,
        quantity=None,
        order_type=None,
        transaction_type=None,
        tag=None,
        product=None,
        price=None,
        trigger_price=None,
    ):
        exchange = self.get_quantplay_exchange(exchange)
        try:
            Constants.logger.info(
                f"[PLACING_ORDER] {tradingsymbol} {exchange} {quantity} {tag} {product}"
            )
            product = self.get_product(product)
            symbol_data = self.symbol_data[
                f"{exchange}:{self.get_symbol(tradingsymbol)}"
            ]
            if trigger_price is None:
                trigger_price = 0

            # create an instance of the API class
            api_instance = upstox_client.OrderApi(
                upstox_client.ApiClient(self.configuration)
            )
            body = upstox_client.PlaceOrderRequest(
                quantity=quantity,
                product=product,
                validity="DAY",
                price=price,
                instrument_token=f"{symbol_data['instrument_key']}",
                order_type=order_type,
                transaction_type=transaction_type,
                disclosed_quantity=0,
                trigger_price=trigger_price,
                is_amo=False,
            )
            api_version = "2.0"  # str | API Version Header
            api_response = api_instance.place_order(body, api_version)
            return api_response.data.order_id
        except Exception as e:
            raise QuantplayOrderPlacementException(str(e))

    def generate_token(
        self, api_key, api_secret, totp, mobile_number, account_pin, redirect_url
    ):
        try:
            code = UplinkUtils.get_request_token(
                api_key,
                redirect_url,
                totp,
                mobile_number,
                account_pin,
            )
            response = UplinkUtils.generate_access_token(
                code,
                api_key,
                api_secret,
                redirect_url,
            )

            return response["access_token"]
        except TokenException as e:
            message = str(e)
            if "Invalid" in message and "checksum" in message:
                raise InvalidArgumentException("Invalid API secret")
            raise
        except Exception as e:
            traceback.print_exc()
            Constants.logger.error(f"Failed to generate upstox token {e}")
            raise e

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:profile")
    def profile(self):
        # create an instance of the API class
        api_instance = upstox_client.UserApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header

        try:
            # Get profile
            api_response = api_instance.get_profile(api_version)
            profile_data = api_response.data
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling UserApi->get_profile: %s\n" % e
            )
            self.handle_exception(e)

        response = {
            "user_id": profile_data.user_id,
            "full_name": profile_data.user_name,
            "exchanges": profile_data.exchanges,
            "email": profile_data.email,
        }
        self.email = response["email"]
        self.enabled_exchanges = response["exchanges"]
        self.user_id = response["user_id"]

        return response

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:positions")
    def positions(self, drop_cnc=True):
        # create an instance of the API class
        api_instance = upstox_client.PortfolioApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header

        try:
            # Get Positions
            api_response = api_instance.get_positions(api_version)
            positions = [position.to_dict() for position in api_response.data]
            positions = pd.DataFrame(positions)
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling PortfolioApi->get_positions: %s\n" % e
            )
            self.handle_exception(e)

        if len(positions) == 0:
            return pd.DataFrame(columns=self.positions_column_list)

        positions.rename(columns={"last_price": "ltp"}, inplace=True)

        positions["pnl"] = positions.sell_value - positions.buy_value
        positions["pnl"] += (positions.quantity) * positions.ltp

        positions.loc[:, "option_type"] = np.where(
            "PE" == positions.tradingsymbol.str[-2:], "PE", "CE"
        )
        positions["option_type"] = np.where(
            positions.exchange.isin(["NFO", "BFO"]), positions.option_type, None
        )
        positions["token"] = positions.instrument_token.apply(lambda x: x.split("|")[1])
        positions["buy_quantity"] = (
            positions.overnight_buy_quantity + positions.day_buy_quantity
        )
        positions["sell_quantity"] = (
            positions.overnight_buy_quantity + positions.day_sell_quantity
        )

        positions["product"] = positions["product"].replace(
            ["I", "C", "D"], ["MIS", "CNC", "NRML"]
        )

        if drop_cnc:
            positions = positions[positions["product"] != "CNC"]
        return positions[self.positions_column_list]

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:orders")
    def orders(self, tag=None, add_ltp=True):
        # create an instance of the API class
        api_instance = upstox_client.OrderApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header

        try:
            # Get order book
            api_response = api_instance.get_order_book(api_version)
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling OrderApi->get_order_book: %s\n" % e
            )
            self.handle_exception(e)

        orders = [order.to_dict() for order in api_response.data]
        orders = pd.DataFrame(orders)
        if len(orders) == 0:
            return pd.DataFrame(columns=self.orders_column_list)

        positions = self.positions()
        positions = positions.sort_values("product").groupby(["tradingsymbol"]).head(1)
        orders = pd.merge(
            orders,
            positions[["tradingsymbol", "ltp"]],
            how="left",
            left_on=["tradingsymbol"],
            right_on=["tradingsymbol"],
        )
        orders.rename(columns={"placed_by": "user_id"}, inplace=True)

        existing_columns = list(orders.columns)
        columns_to_keep = list(
            set(self.orders_column_list).intersection(set(existing_columns))
        )
        orders = orders[columns_to_keep]

        orders.loc[:, "pnl"] = (
            orders.ltp * orders.filled_quantity
            - orders.average_price * orders.filled_quantity
        )
        orders.loc[:, "pnl"] = np.where(
            orders.transaction_type == "SELL", -orders.pnl, orders.pnl
        )

        if tag:
            orders = orders[orders.tag == tag]

        orders["tradingsymbol"] = np.where(
            orders.exchange == "NSE",
            orders.tradingsymbol.str.replace("-EQ", ""),
            orders.tradingsymbol,
        )
        orders["token"] = orders.apply(
            lambda x: self.symbol_data[f"{x['exchange']}:{x['tradingsymbol']}"][
                "token"
            ],
            axis=1,
        )
        orders["update_timestamp"] = orders.order_timestamp
        orders.status = orders.status.replace(
            ["open", "cancelled", "trigger pending", "complete", "rejected"],
            ["OPEN", "CANCELLED", "TRIGGER PENDING", "COMPLETE", "REJECTED"],
        )
        orders["product"] = orders["product"].replace(["D", "I"], ["CNC", "MIS"])
        orders["product"] = np.where(
            ((orders["product"] == "CNC") & (orders["exchange"].isin(["NFO", "BFO"]))),
            "NRML",
            orders["product"],
        )

        return orders

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    @timeit(MetricName="Upstox:margins")
    def margins(self):
        api_instance = upstox_client.UserApi(
            upstox_client.ApiClient(self.configuration)
        )
        api_version = "2.0"  # str | API Version Header
        segment = "SEC"  # str |  (optional)

        try:
            # Get User Fund And Margin
            api_response = api_instance.get_user_fund_margin(
                api_version, segment=segment
            )
        except ApiException as e:
            Constants.logger.error(
                "Exception when calling UserApi->get_user_fund_margin: %s\n" % e
            )
            self.handle_exception(e)

        margins = {
            "margin_used": float(api_response.data["equity"].used_margin),
            "margin_available": float(api_response.data["equity"].available_margin),
        }
        return margins

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    @timeit(MetricName="Upstox:account_summary")
    def account_summary(self):
        margins = self.margins()
        response = {
            "margin_used": margins["margin_used"],
            "margin_available": margins["margin_available"],
            "pnl": float(self.positions().pnl.sum()),
        }
        return response

    def stream_order_data(self):
        th = threading.Thread(target=self.between_callback, daemon=True)
        th.start()

    def between_callback(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.fetch_order_updates())
        loop.close()

    async def fetch_order_updates(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Configure OAuth2 access token for authorization: OAUTH2
        configuration = upstox_client.Configuration()

        api_version = "2.0"
        configuration.access_token = self.access_token

        # Get portfolio stream feed authorize
        response = self.get_portfolio_stream_feed_authorize(api_version, configuration)

        async with websockets.connect(
            response.data.authorized_redirect_uri, ssl=ssl_context
        ) as websocket:
            print("Connection established")

            # Perform WebSocket operations
            while True:
                message = await websocket.recv()
                self.order_event_handler(json.dumps(message))

    def get_portfolio_stream_feed_authorize(self, api_version, configuration):
        api_instance = upstox_client.WebsocketApi(
            upstox_client.ApiClient(configuration)
        )
        api_response = api_instance.get_portfolio_stream_feed_authorize(api_version)
        return api_response

    def get_quantplay_product(self, exchange, product):
        product_map = {"D": "CNC", "I": "MIS"}
        if product in product_map:
            product = product_map[product]
        if product == "CNC" and exchange in ["NFO", "BFO"]:
            product = "NRML"

        return product

    def order_event_handler(self, order):
        order = json.loads(json.loads(order))

        try:
            order["status"] = order["status"].upper()
            if order["exchange"] in ["NSE", "BSE"]:
                order["tradingsymbol"] = order["tradingsymbol"].replace("-EQ", "")
            order["product"] = self.get_quantplay_product(
                order["exchange"], order["product"]
            )
            Constants.logger.info("[UPDATE_RECEIVED] {}".format(order))
            self.order_updates.put(order)
        except Exception as e:
            traceback.print_exc()
            Constants.logger.error("[ORDER_UPDATE_PROCESSING_FAILED] {}".format(e))

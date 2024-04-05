import json
import traceback

import numpy as np
import pandas as pd
from retrying import retry

from quantplay.broker.generics.broker import Broker
from quantplay.exception.exceptions import (
    InvalidArgumentException,
    RetryableException,
    TokenException,
    retry_exception,
)
from quantplay.utils.constant import Constants, OrderType, timeit
from quantplay.utils.pickle_utils import InstrumentData
from quantplay.wrapper.aws.s3 import S3Utils
from datetime import datetime, timedelta

logger = Constants.logger


class Noren(Broker):
    def __init__(
        self,
        load_instrument=True,
        order_updates=None,
    ):
        super(Noren, self).__init__()

        self.order_updates = order_updates

        if load_instrument:
            self.load_instrument()

        self.order_type_sl = "SL-LMT"
        self.trigger_pending_status = "TRIGGER_PENDING"

    def set_attributes(self, response):
        self.email = response["email"]
        self.user_id = response["actid"]
        self.full_name = response["uname"]
        self.user_token = response["susertoken"]

    def load_instrument(self):
        try:
            self.symbol_data = InstrumentData.get_instance().load_data(
                "shoonya_instruments"
            )
            Constants.logger.info("[LOADING_INSTRUMENTS] loading data from cache")
        except Exception as e:
            self.instrument_data = S3Utils.read_csv(
                "quantplay-market-data",
                "symbol_data/shoonya_instruments.csv",
                read_from_local=False,
            )
            self.initialize_symbol_data(save_as="shoonya_instruments")

        self.initialize_broker_symbol_map()

    def get_symbol(self, symbol, exchange=None):
        if symbol not in self.quantplay_symbol_map:
            return symbol
        return self.quantplay_symbol_map[symbol]

    def get_transaction_type(self, transaction_type):
        if transaction_type == "BUY":
            return "B"
        elif transaction_type == "SELL":
            return "S"

        raise InvalidArgumentException(
            "transaction type {} not supported for trading".format(transaction_type)
        )

    def get_order_type(self, order_type):
        if order_type == OrderType.market:
            return "MKT"
        elif order_type == OrderType.sl:
            return "SL-LMT"
        elif order_type == OrderType.slm:
            return "SL-MKT"
        elif order_type == OrderType.limit:
            return "LMT"

        return order_type

    def get_product(self, product):
        if product == "NRML":
            return "M"
        elif product == "CNC":
            return "C"
        elif product == "MIS":
            return "I"
        elif product in ["M", "C", "I"]:
            return product

        raise InvalidArgumentException(
            "Product {} not supported for trading".format(product)
        )

    def event_handler_order_update(self, order):
        try:
            order["placed_by"] = order["actid"]
            order["tag"] = order["actid"]
            order["order_id"] = order["norenordno"]
            order["exchange_order_id"] = order["exchordid"]
            order["exchange"] = order["exch"]

            # TODO translate symbol
            # -EQ should be removed
            # F&O symbol translation
            order["tradingsymbol"] = order["tsym"]

            if order["exchange"] == "NSE":
                order["tradingsymbol"] = order["tradingsymbol"].replace("-EQ", "")
            elif order["exchange"] in ["NFO", "MCX"]:
                order["tradingsymbol"] = self.broker_symbol_map[order["tradingsymbol"]]

            order["order_type"] = order["prctyp"]
            if order["order_type"] == "LMT":
                order["order_type"] = "LIMIT"
            elif order["order_type"] == "MKT":
                order["order_type"] = "MARKET"
            elif order["order_type"] == "SL-LMT":
                order["order_type"] = "SL"

            if order["pcode"] == "M":
                order["product"] = "NRML"
            elif order["pcode"] == "C":
                order["product"] = "CNC"
            elif order["pcode"] == "I":
                order["product"] = "MIS"

            if order["trantype"] == "S":
                order["transaction_type"] = "SELL"
            elif order["trantype"] == "B":
                order["transaction_type"] = "BUY"
            else:
                logger.error(
                    "[UNKNOW_VALUE] finvasia transaction type {} not supported".format(
                        order["trantype"]
                    )
                )

            order["quantity"] = int(order["qty"])

            if "trgprc" in order:
                order["trigger_price"] = float(order["trgprc"])
            else:
                order["trigger_price"] = None

            order["price"] = float(order["prc"])

            if order["status"] == "TRIGGER_PENDING":
                order["status"] = "TRIGGER PENDING"
            elif order["status"] == "CANCELED":
                order["status"] = "CANCELLED"

            print(f"order feed {order}")
            self.order_updates.put(order)
        except Exception as e:
            logger.error("[ORDER_UPDATE_PROCESSING_FAILED] {}".format(e))

    @timeit(MetricName="Finvasia:place_order")
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
        try:
            if trigger_price == 0:
                trigger_price = None

            transaction_type = self.get_transaction_type(transaction_type)
            order_type = self.get_order_type(order_type)
            product = self.get_product(product)
            tradingsymbol = self.get_symbol(tradingsymbol)

            data = {
                "product_type": product,
                "buy_or_sell": transaction_type,
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "quantity": quantity,
                "price_type": order_type,
                "price": price,
                "trigger_price": trigger_price,
                "remarks": tag,
            }
            Constants.logger.info("[PLACING_ORDER] {}".format(json.dumps(data)))
            response = self.api.place_order(
                buy_or_sell=transaction_type,
                product_type=product,
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                quantity=quantity,
                discloseqty=0,
                price_type=order_type,
                price=price,
                trigger_price=trigger_price,
                retention="DAY",
                remarks=tag,
            )

            Constants.logger.info(
                "[PLACE_ORDER_RESPONSE] {} input {}".format(response, json.dumps(data))
            )
            if "norenordno" in response:
                return response["norenordno"]
            else:
                raise Exception(response)
        except Exception as e:
            traceback.print_exc()
            exception_message = "Order placement failed with error [{}]".format(str(e))
            logger.error(f"[PLACE_ORDER_FAILED] {exception_message}")

    def get_orders(self):
        return self.api.get_order_book()

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    @timeit(MetricName="Noren:get_ltp")
    def get_ltp(self, exchange, tradingsymbol):
        tradingsymbol = self.get_symbol(tradingsymbol)

        token = self.symbol_data["{}:{}".format(exchange, tradingsymbol)]["token"]
        return float(self.api.get_quotes(exchange, str(token))["lp"])

    def live_data(self, exchange, tradingsymbol):
        tradingsymbol = self.get_symbol(tradingsymbol)
        token = self.symbol_data["{}:{}".format(exchange, tradingsymbol)]["token"]
        data = self.api.get_quotes(exchange, str(token))
        return {
            "ltp": float(data["lp"]),
            "upper_circuit": float(data["uc"]),
            "lower_circuit": float(data["lc"]),
        }

    def order_history(self, order_id):
        order_history = self.api.single_order_history(order_id)
        order_details = order_history[0]

        data = {}
        data["order_id"] = order_id
        data["order_type"] = order_details["prctyp"]
        data["exchange"] = order_details["exch"]
        data["quantity"] = order_details["qty"]
        data["tradingsymbol"] = order_details["tsym"]

        return data

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    @timeit(MetricName="Finvasia:modify_order")
    def modify_order(self, data):
        order_id = data["order_id"]
        data["order_type"] = self.get_order_type(data["order_type"])
        existing_details = self.order_history(order_id)

        if "trigger_price" not in data:
            data["trigger_price"] = None

        if "order_type" not in data:
            data["order_type"] = existing_details["order_type"]
        if "quantity" not in data:
            data["quantity"] = existing_details["quantity"]

        try:
            logger.info(f"[MODIFYING_ORDER] {data}")
            response = self.api.modify_order(
                orderno=order_id,
                exchange=existing_details["exchange"],
                tradingsymbol=existing_details["tradingsymbol"],
                newprice_type=data["order_type"],
                newquantity=data["quantity"],
                newprice=data["price"],
                newtrigger_price=data["trigger_price"],
            )
            logger.info(
                "[MODIFY_ORDER_RESPONSE] order id [{}] response [{}]".format(
                    data["order_id"], response
                )
            )
            return response
        except Exception as e:
            exception_message = (
                "OrderModificationFailed for {} failed with exception {}".format(
                    data["order_id"], e
                )
            )
            Constants.logger.error("{}".format(exception_message))
            raise e

    @timeit(MetricName="Finvasia:cancel_order")
    def cancel_order(self, order_id):
        self.api.cancel_order(order_id)

    def stream_order_data(self):
        self.api.start_websocket(order_update_callback=self.event_handler_order_update)

    @timeit(MetricName="Finvasia:profile")
    def profile(self):
        response = {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
        }

        return response

    @timeit(MetricName="Noren:holdings")
    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def holdings(self):
        holdings = self.api.get_holdings()
        if holdings is None or len(holdings) == 0:
            return pd.DataFrame(columns=self.holdings_column_list)

        holdings = [
            {
                "exchange": h["exch_tsym"][0]["exch"],
                "token": h["exch_tsym"][0]["token"],
                "tradingsymbol": h["exch_tsym"][0]["tsym"],
                "isin": h["exch_tsym"][0]["isin"],
                "quantity": int(h["holdqty"])
                + int(h.get("npoadqty", 0))
                + int(h.get("brkcolqty", 0)),
                "pledged_quantity": int(h.get("brkcolqty", 0)),
                "average_price": float(h.get("upldprc", 0)),
            }
            for h in holdings
        ]
        holdings = pd.DataFrame(holdings)
        holdings["price"] = holdings.apply(
            lambda x: self.get_ltp(x["exchange"], x["tradingsymbol"]), axis=1
        )
        holdings["value"] = holdings.quantity * holdings.price
        return holdings[self.holdings_column_list]

    @timeit(MetricName="Finvasia:positions")
    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
    )
    def positions(self):
        positions = self.api.get_positions()

        if positions is None or len(positions) == 0:
            return pd.DataFrame(columns=self.positions_column_list)

        positions = pd.DataFrame(positions)

        positions.loc[:, "tradingsymbol"] = positions.tsym
        positions.loc[:, "ltp"] = positions.lp.astype(float)
        positions.loc[:, "pnl"] = positions.rpnl.astype(
            float
        ) + positions.urmtom.astype(float)

        if "dname" not in positions.columns:
            positions.loc[:, "dname"] = None
        positions.loc[:, "dname"] = np.where(
            positions.exch == "BFO", positions.tsym.str[-2:], positions.dname
        )

        positions.loc[:, "dname"] = positions.dname.str.strip()
        positions.loc[:, "dname"] = positions.dname.str.strip()
        positions.loc[:, "option_type"] = np.where(
            "PE" == positions.dname.str[-2:], "PE", np.nan
        )
        positions.loc[:, "option_type"] = np.where(
            "CE" == positions.dname.str[-2:], "CE", positions.option_type
        )
        positions.loc[:, "option_type"] = np.where(
            positions.exch.isin(["NFO", "BFO"]), positions.option_type, None
        )

        positions.rename(
            columns={
                "prd": "product",
                "exch": "exchange",
            },
            inplace=True,
        )

        mandatory_columns = ["daybuyqty", "daysellqty", "cfbuyqty", "cfsellqty"]
        for mad_c in mandatory_columns:
            if mad_c not in positions.columns:
                positions.loc[:, mad_c] = 0

        positions.loc[:, "buy_quantity"] = positions.daybuyqty.astype(
            int
        ) + positions.cfbuyqty.astype(int)
        positions.loc[:, "sell_quantity"] = positions.daysellqty.astype(
            int
        ) + positions.cfsellqty.astype(int)
        positions.loc[:, "quantity"] = positions.buy_quantity - positions.sell_quantity

        positions["product"] = positions["product"].replace(
            ["I", "C", "M"], ["MIS", "CNC", "NRML"]
        )

        positions.rename(
            columns={
                "totsellamt": "sell_value",
                "totbuyamt": "buy_value",
            },
            inplace=True,
        )

        return positions[self.positions_column_list]

    def add_transaction_charges(self, orders):
        return super(Noren, self).add_transaction_charges(
            orders, cm_charges=0, fo_charges=0
        )

    @timeit(MetricName="Finvasia:orders")
    def orders(self, tag=None, status=None, add_ltp=True):
        orders = pd.DataFrame(self.api.get_order_book())
        positions = self.positions()
        if len(orders) == 0:
            return pd.DataFrame(columns=self.orders_column_list)

        orders.loc[:, "tradingsymbol"] = orders.tsym
        orders = pd.merge(
            orders,
            positions[["tradingsymbol", "ltp"]],
            how="left",
            left_on=["tradingsymbol"],
            right_on=["tradingsymbol"],
        )

        orders.rename(
            columns={
                "norenordno": "order_id",
                "uid": "user_id",
                "exch": "exchange",
                "remarks": "tag",
                "avgprc": "average_price",
                "prd": "product",
                "trantype": "transaction_type",
                "qty": "quantity",
                "trgprc": "trigger_price",
                "prc": "price",
                "prctyp": "order_type",
                "fillshares": "filled_quantity",
                "rorgqty": "pending_quantity",
                "norentm": "order_timestamp",
                "rejreason": "status_message",
            },
            inplace=True,
        )

        existing_columns = list(orders.columns)
        columns_to_keep = list(
            set(self.orders_column_list).intersection(set(existing_columns))
        )
        orders = orders[columns_to_keep]

        if "filled_quantity" not in orders.columns:
            orders.loc[:, "filled_quantity"] = 0
        if "average_price" not in orders.columns:
            orders.loc[:, "average_price"] = 0
        orders.loc[:, "filled_quantity"] = orders.filled_quantity.astype(float)
        orders.loc[:, "average_price"] = orders.average_price.astype(float)
        orders.loc[:, "pnl"] = (
            orders.ltp * orders.filled_quantity
            - orders.average_price * orders.filled_quantity
        )
        orders.loc[:, "pnl"] = np.where(
            orders.transaction_type == "S", -orders.pnl, orders.pnl
        )
        orders.loc[:, "order_timestamp"] = pd.to_datetime(
            orders.order_timestamp, format="%H:%M:%S %d-%m-%Y"
        )

        orders = self.filter_orders(orders, status=status, tag=tag)

        orders.transaction_type = orders.transaction_type.replace(
            ["S", "B"], ["SELL", "BUY"]
        )

        orders.status = orders.status.replace(
            ["TRIGGER_PENDING", "CANCELED"], ["TRIGGER PENDING", "CANCELLED"]
        )

        orders["product"] = orders["product"].replace(
            ["I", "C", "M"], ["MIS", "CNC", "NRML"]
        )
        orders["order_type"] = orders["order_type"].replace(
            ["MKT", "LMT", "SL-LMT", "SL-MKT"], ["MARKET", "LIMIT", "SL", "SL-M"]
        )

        return orders

    @timeit(MetricName="Finvasia:positions")
    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def margins(self):
        api_margins = self.api.get_limits()
        if "stat" in api_margins and "not_ok" == api_margins["stat"].lower():
            raise TokenException(api_margins["emsg"])

        try:
            collateral = 0
            if "collateral" in api_margins:
                collateral = api_margins["collateral"]

            if "marginused" not in api_margins:
                api_margins["margin_used"] = 0
            else:
                api_margins["margin_used"] = api_margins["marginused"]
            if "payin" not in api_margins:
                api_margins["payin"] = 0
            margin_available = (
                float(api_margins["cash"])
                + float(collateral)
                + float(api_margins["payin"])
                - float(api_margins["margin_used"])
            )

            margins = {}
            margins["margin_used"] = api_margins["margin_used"]
            margins["margin_available"] = margin_available
            margins["total_balance"] = float(api_margins["cash"]) + float(collateral)

            return margins
        except Exception as e:
            logger.error(f"[NOREN_MARGIN_ERROR] {e}")
            RetryableException("[NOREN] Failed to fetch account margin")

    @timeit(MetricName="Finvasia:account_summary")
    def account_summary(self):
        margins = self.margins()
        pnl = 0
        positions = self.positions()
        if len(positions) > 0:
            pnl = positions.pnl.sum()

        response = {
            "margin_used": margins["margin_used"],
            "total_balance": margins["total_balance"],
            "margin_available": margins["margin_available"],
            "pnl": pnl,
        }
        return response

    def historical_data(
        self,
        exchange=None,
        token=None,
        tradingsymbol=None,
        interval=None,
        start_time=None,
        end_time=datetime.now(),
        days=None,
    ):
        self.validate_exchange(exchange)
        if tradingsymbol:
            tradingsymbol = self.get_symbol(tradingsymbol, exchange=exchange)
            token = self.symbol_data[f"{exchange}:{tradingsymbol}"]["token"]
            self.validate_existance(token, "Invalid trading symbol")
        self.validate_existance(token, "Invalid token")

        if days:
            start_time = datetime.now() - timedelta(days=days)
            end_time = datetime.now()

        if interval == "day":
            data = self.api.get_daily_price_series(
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                startdate=start_time.timestamp(),
                enddate=end_time.timestamp(),
            )
            data = [json.loads(a) for a in data]
        else:
            interval_map = {"minute": 1, "5minute": 5}
            interval = interval_map[interval]

            data = self.api.get_time_price_series(
                exchange=exchange,
                token=str(token),
                starttime=start_time.timestamp(),
                endtime=end_time.timestamp(),
                interval=interval,
            )
        data = pd.DataFrame(data)
        data.rename(
            columns={
                "time": "date",
                "into": "open",
                "inth": "high",
                "intl": "low",
                "intc": "close",
                "intvwap": "vwap",
                "intv": "volume",
            },
            inplace=True,
        )

        if interval == "day":
            data["date"] = pd.to_datetime(data["date"], format="%d-%b-%Y")
        else:
            data["date"] = pd.to_datetime(data["date"], format="%d-%m-%Y %H:%M:%S")
        columns_to_return = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "vwap",
            "volume",
            "oi",
        ]
        data = data[list(set(columns_to_return).intersection(set(data.columns)))]
        return data.sort_values("date").reset_index(drop=True)

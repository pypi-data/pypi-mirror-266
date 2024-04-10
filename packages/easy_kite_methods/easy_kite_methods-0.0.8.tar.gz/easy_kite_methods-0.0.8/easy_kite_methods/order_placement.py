import pandas as pd
from time import sleep

from requests import ReadTimeout
from requests.exceptions import (ConnectionError)
from urllib3.exceptions import (ConnectTimeoutError)
from kiteconnect.exceptions import (NetworkException, DataException)

from easy_kite_methods.kite_login import kite

RETRY_THRESHOLD = 3
WAIT_BEFORE_RETRY = 1


def get_stock_price(stock_name) -> str:
    """
    name -> This is the name of the stock
    """
    value = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            stock_name.upper()
            value = kite.quote("NSE:"+stock_name)
            stock_name = "NSE:"+stock_name
            if (value[stock_name]['last_price'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return value[stock_name]['last_price']


def get_stock_instrument_token(stock_name: str):
    """
    name -> This is the name of the stock
    """
    value = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            stock_name.upper()
            value = kite.quote("NSE:" + stock_name)
            stock_name = "NSE:"+stock_name
            if (value[stock_name]['instrument_token'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return value[stock_name]['instrument_token']


def get_fno_price(fno_name: str):
    """
    name -> This is the name of the option instrument
    It can be either futures / options
    """
    value = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            fno_name.upper()
            value = kite.quote("NFO:" + fno_name)
            fno_name = "NFO:"+fno_name
            if (value[fno_name]['last_price'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return value[fno_name]['last_price']


def get_fno_instrument_token(fno_name: str):
    """
    name -> This is the name of the option instrument
    It can be either futures / options
    """
    value = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            fno_name.upper()
            value = kite.quote("NFO:" + fno_name)
            fno_name = "NFO:"+fno_name
            if (value[fno_name]['instrument_token'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return value[fno_name]['instrument_token']


def buy_intraday_normal_order(stock_name: str, quantity: int):
    order_id = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=quantity, product=kite.PRODUCT_MIS,
                                        order_type=kite.ORDER_TYPE_MARKET)
            break
        except:
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def sell_intraday_normal_order(stock_name: str, quantity: int):
    order_id = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=quantity, product=kite.PRODUCT_MIS,
                                        order_type=kite.ORDER_TYPE_MARKET)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def buy_intraday_limit_order(stock_name, quantity, price):
    order_id = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_BUY,
                                        quantity=quantity, product=kite.PRODUCT_MIS, price=price,
                                        order_type=kite.ORDER_TYPE_LIMIT)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def sell_intraday_limit_order(stock_name, quantity, price):
    order_id = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=quantity, product=kite.PRODUCT_MIS, price=price,
                                        order_type=kite.ORDER_TYPE_LIMIT)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def place_slm_order(stock_name, quantity, order_type, price):
    order_id = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_CO, exchange=kite.EXCHANGE_NSE,
                                        tradingsymbol=stock_name, transaction_type=order_type,
                                        quantity=quantity, product=kite.PRODUCT_MIS, trigger_price=price-4, trailing_stoploss=4,
                                        order_type=kite.ORDER_TYPE_MARKET)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def modify_order_quantity(variety: str, order_id: str, quantity):
    """
    order_id : This is the id of order executed
    variety : Variety can be [AMO ,REGULAR , BO,CO]
    quantity : Total number of orders
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            if variety.upper() is "REGULAR":
                order_id = kite.modify_order(variety=kite.VARIETY_REGULAR, order_id=order_id,
                                             quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)

            if variety.upper() is "CO":
                order_id = kite.modify_order(variety=kite.VARIETY_CO, order_id=order_id,
                                             quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)

            if variety.upper() is "AMO":
                order_id = kite.modify_order(variety=kite.VARIETY_AMO, order_id=order_id,
                                             quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def modify_order_price(variety: str, order_id: str, price):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO
                            VARIETY_REGULAR ]
    price : Modified price of order
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            if variety.upper() is "REGULAR":
                variety = kite.VARIETY_REGULAR

            if variety.upper() is "CO":
                variety = kite.VARIETY_CO

            if variety.upper() is "AMO":
                variety = kite.VARIETY_AMO

            order_id = kite.modify_order(variety=variety, order_id=order_id,
                                         price=price, order_type=kite.ORDER_TYPE_MARKET)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def modify_order_to_sell(variety: str, order_id: str):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            if variety.upper() is "REGULAR":
                variety = kite.VARIETY_REGULAR

            if variety.upper() is "CO":
                variety = kite.VARIETY_CO

            if variety.upper() is "AMO":
                variety = kite.VARIETY_AMO

            order_id = kite.modify_order(
                variety=variety, order_id=order_id, order_type=kite.TRANSACTION_TYPE_SELL)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def modify_order_to_buy(variety: str, order_id: str):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            if variety.upper() is "REGULAR":
                variety = kite.VARIETY_REGULAR

            if variety.upper() is "CO":
                variety = kite.VARIETY_CO

            if variety.upper() is "AMO":
                variety = kite.VARIETY_AMO

            order_id = kite.modify_order(
                variety=variety, order_id=order_id, order_type=kite.TRANSACTION_TYPE_BUY)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_id


def get_holdings():
    kite_holdings = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            kite_holdings = kite.holdings()
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return kite_holdings


def exit_orders(order_id: str):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    exit_order = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            exit_order = kite.exit_order(
                variety=kite.VARIETY_REGULAR, order_id=order_id)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return exit_order


def cancel_order(order_id: str):
    """
    order_id : This is the id of order executed                                     
    """
    cancel_order = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            cancel_order = kite.cancel_order(
                variety=kite.VARIETY_REGULAR, order_id=order_id)
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return cancel_order


def get_positions():
    kite_positions = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            kite_positions = kite.positions()
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return kite_positions


def get_order_history(order_id: str):
    order_history = None

    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_history = pd.DataFrame(kite.order_history(order_id=order_id))
            break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return order_history


def get_sl_order(order_id: str):
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_history = kite.orders()
            for order in order_history:
                sl_order = order['parent_order_id']
                if (sl_order is order_id):
                    return sl_order
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return False


def get_average_price_and_status(order_id: str):
    """
    Returns the status as {COMPLETED,ORDER_PENDING,REJECTED} &
    average price of the executed order
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_data = pd.DataFrame(kite.order_history(order_id))
            status = order_data['status'][len(order_data)-1]
            average_price = order_data['average_price'][len(order_data)-1]
            return status, average_price
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)
    return False


def get_status(order_id: str):
    """
    Returns the status as {COMPLETED,ORDER_PENDING,REJECTED} &
    """
    retry_threshold = RETRY_THRESHOLD
    tried = 0
    while tried < retry_threshold:
        try:
            order_data = pd.DataFrame(kite.order_history(order_id=order_id))
            status = order_data['status'][len(order_data)-1]
            return status
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            tried += 1
            sleep(WAIT_BEFORE_RETRY)

    return False

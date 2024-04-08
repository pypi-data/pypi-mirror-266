import pandas as pd

from requests import ReadTimeout
from requests.exceptions import (ConnectionError)
from urllib3.exceptions import (ConnectTimeoutError)
from kiteconnect.exceptions import (NetworkException, DataException)

from easy_kite_methods.kite_login import kite


def get_stock_price(name: str):
    """
    name -> This is the name of the stock
    """
    while True:
        try:
            name.upper()
            value = kite.quote("NSE:"+name)
            if (value[name]['last_price'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            pass
    return value


def get_stock_instrument_token(stock_name: str):
    """
    name -> This is the name of the stock
    """
    while True:
        try:
            stock_name.upper()
            value = kite.quote("NSE:" + stock_name)
            if (value[stock_name]['instrument_token'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            pass
    return value


def get_fno_price(fno_name: str):
    """
    name -> This is the name of the option instrument
    It can be either futures / options
    """
    while True:
        try:
            value = kite.quote("NSE:" + fno_name)
            if (value[fno_name]['last_price'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            pass
    return value


def get_fno_instrument_token(stock_name: str):
    """
    name -> This is the name of the option instrument
    It can be either futures / options
    """
    while True:
        try:
            value = kite.quote("NFO:" + stock_name)
            if (value[stock_name]['instrument_token'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            pass
    return value


def buy_intraday_normal_order(stock_name: str, quantity: int):
    try:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=quantity, product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_MARKET)

        return order_id
    except:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                    tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=quantity, product=kite.PRODUCT_MIS,
                                    order_type=kite.ORDER_TYPE_MARKET)

        return order_id


def sell_intraday_normal_order(stock_name: str, quantity: int):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_SELL,
                                quantity=quantity, product=kite.PRODUCT_MIS,
                                order_type=kite.ORDER_TYPE_MARKET)

    return order_id


def buy_intraday_limit_order(stock_name, quantity, price):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_BUY,
                                quantity=quantity, product=kite.PRODUCT_MIS, price=price,
                                order_type=kite.ORDER_TYPE_LIMIT)

    return order_id


def sell_intraday_limit_order(stock_name, quantity, price):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=kite.TRANSACTION_TYPE_SELL,
                                quantity=quantity, product=kite.PRODUCT_MIS, price=price,
                                order_type=kite.ORDER_TYPE_LIMIT)
    return order_id


def place_slm_order(stock_name, quantity, order_type, price):

    order_id = kite.place_order(variety=kite.VARIETY_CO, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS, trigger_price=price-4, trailing_stoploss=4,
                                order_type=kite.ORDER_TYPE_MARKET)
    return order_id


def modify_order_quantity(variety, order_id, quantity):
    """
    order_id : This is the id of order executed
    variety : Variety can be [AMO ,REGULAR , BO,CO]
    quantity : Total number of orders                        
    """

    if variety.upper() is "REGULAR" :
         order_id = kite.modify_order(variety=kite.VARIETY_REGULAR, order_id=order_id,
                                 quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)
    return order_id

    if variety.upper() is "CO" :
         order_id = kite.modify_order(variety=kite.VARIETY_CO, order_id=order_id,
                                 quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)
    return order_id

     if variety.upper() is "AMO" :
         order_id = kite.modify_order(variety=kite.VARIETY_AMO, order_id=order_id,
                                 quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)
    return order_id

     if variety.upper() is "BO" :
         order_id = kite.modify_order(variety=kite.VARIETY_BO, order_id=order_id,
                                 quantity=quantity, order_type=kite.ORDER_TYPE_MARKET)
    return order_id

      


def modify_order_price(variety, order_id, price):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]
    price : Modified price of order                      
    """
    if variety.upper() is "REGULAR" :
         variety = kite.VARIETY_REGULAR

    if variety.upper() is "CO" :
         variety = kite.VARIETY_CO
  
    if variety.upper() is "AMO" :
        variety = kite.VARIETY_AMO

     if variety.upper() is "BO" :
        variety = kite.VARIETY_BO
         
    order_id = kite.modify_order(variety=variety, order_id=order_id,
                                 price=price, order_type=kite.ORDER_TYPE_MARKET)
    return order_id


def modify_order_to_sell(variety, order_id):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    if variety.upper() is "REGULAR" :
         variety = kite.VARIETY_REGULAR

    if variety.upper() is "CO" :
         variety = kite.VARIETY_CO
  
    if variety.upper() is "AMO" :
        variety = kite.VARIETY_AMO

     if variety.upper() is "BO" :
        variety = kite.VARIETY_BO

    order_id = kite.modify_order(
        variety=variety, order_id=order_id, order_type=kite.TRANSACTION_TYPE_SELL)
    return order_id


def modify_order_to_buy(variety, order_id):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    if variety.upper() is "REGULAR" :
         variety = kite.VARIETY_REGULAR

    if variety.upper() is "CO" :
         variety = kite.VARIETY_CO
  
    if variety.upper() is "AMO" :
        variety = kite.VARIETY_AMO

     if variety.upper() is "BO" :
        variety = kite.VARIETY_BO

    order_id = kite.modify_order(
        variety=variety, order_id=order_id, order_type=kite.TRANSACTION_TYPE_BUY)
    return order_id


def get_holdings():
    return kite.holdings()


def exit_orders(order_id):
    """
    order_id : This is the id of order executed
    variety : Variety can be [VARIETY_AMO 
                            VARIETY_REGULAR ]                    
    """
    kite.exit_order(variety=kite.VARIETY_REGULAR, order_id=order_id)


def cancel_order(order_id):
    """
    order_id : This is the id of order executed                                     
    """
    kite.cancel_order(variety=kite.VARIETY_REGULAR, order_id=order_id)


def get_positions():
    return kite.positions()


def get_order_history(order_id):
    return pd.DataFrame(kite.order_history(order_id=order_id))


def get_sl_order(order_id):

    order_history = kite.orders()
    for order in order_history:
        sl_order = order['parent_order_id']
        if (sl_order is order_id):
            return sl_order
    return False


def get_average_price_and_status(order_id):
    """
    Returns the status as {COMPLETED,ORDER_PENDING,REJECTED} &
    average price of the executed order
    """
    order_data = pd.DataFrame(kite.order_history(order_id))
    status = order_data['status'][len(order_data)-1]
    average_price = order_data['average_price'][len(order_data)-1]
    return status, average_price


def get_status(order_id):
    """
    Returns the status as {COMPLETED,ORDER_PENDING,REJECTED} &
    """
    order_data = pd.DataFrame(kite.order_history(order_id=order_id))
    status = order_data['status'][len(order_data)-1]
    return status

import datetime
import pandas as pd
import dateutil as SY

from requests import ReadTimeout
from requests.exceptions import (ConnectionError)
from urllib3.exceptions import (ConnectTimeoutError)
from kiteconnect.exceptions import (NetworkException, DataException)

from just_design_phase.kite_login import kite


def place_normal_order(stock_name: str, quantity: int, order_type: str):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS,
                                order_type=kite.ORDER_TYPE_MARKET)

    return order_id


def place_normal_amo_order(stock_name, quantity, order_type):
    order_id = kite.place_order(variety=kite.VARIETY_AMO, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS,
                                order_type=kite.ORDER_TYPE_MARKET)

    return order_id


def place_limit_order(stock_name, quantity, price, order_type):
    order_id = kite.place_order(variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS, price=price,
                                order_type=kite.ORDER_TYPE_LIMIT)

    return order_id


def place_limit_cover_order(stock_name, quantity, order_type, trigger_price, price):
    order_id = kite.place_order(variety=kite.VARIETY_AMO, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS, trigger_price=trigger_price, price=price,
                                order_type=kite.ORDER_TYPE_LIMIT)
    return order_id


def place_market_cover_order(stock_name, quantity, order_type, trigger_price):

    order_id = kite.place_order(variety=kite.VARIETY_CO, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS, trigger_price=trigger_price,
                                order_type=kite.ORDER_TYPE_MARKET)

    return order_id


def place_slm_order(stock_name, quantity, order_type, price, range):

    order_id = kite.place_order(variety=kite.VARIETY_CO, exchange=kite.EXCHANGE_NSE,
                                tradingsymbol=stock_name, transaction_type=order_type,
                                quantity=quantity, product=kite.PRODUCT_MIS, trigger_price=price-4, trailing_stoploss=4,
                                order_type=kite.ORDER_TYPE_MARKET)
    return order_id


def modify_order(variety, orderId, quantity, price):

    order_id = kite.modify_order(variety=variety, order_id=orderId,
                                 quantity=quantity, price=price, order_type=kite.ORDER_TYPE_MARKET)
    return order_id


def modify_order_with_order_type(variety, orderId, quantity, order_type):

    order_id = kite.modify_order(
        variety=variety, order_id=orderId, quantity=quantity, order_type=order_type)
    return order_id


def modify_order_only_order_type(orderID, order_type):

    order_id = kite.modify_order(order_id=orderID,
                                 order_type=order_type)
    return order_id


def get_holdings():

    return kite.holdings()


def exit_orders(variety, order_id):
    kite.exit_order(variety=variety, order_id=order_id)


def cancel_order(variety, order_id):

    kite.cancel_order(variety=variety, order_id=order_id)


def get_positions():

    return kite.positions()


def get_order_history(order_id):

    return kite.order_history(order_id=order_id)


def get_sl_order(order_id):

    order_history = kite.orders()
    for order in order_history:
        sl_order = order['parent_order_id']
        if (sl_order is order_id):
            return sl_order

    return False


def get_average_price_and_status(order_id):

    order_data = pd.DataFrame(kite.order_history(order_id))
    status = order_data['status'][len(order_data)-1]
    average_price = order_data['average_price'][len(order_data)-1]
    return status, average_price


def get_value(name):
    while True:
        try:
            value = kite.quote(name)
            if (value[name]['last_price'] >= 0):
                break
        except (
                NetworkException, DataException, KeyError, ReadTimeout,
                ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, ConnectTimeoutError):
            pass
    return value


def get_instrument_value_options_with_call_type(tradingsymbol, startPrice, EndPrice, callTyp):

    instruments = kite.instruments("NFO")
    newDataBankNifty = pd.DataFrame(instruments)
    newData2 = newDataBankNifty[newDataBankNifty['tradingsymbol'].str.contains(
        tradingsymbol)]
    newData3 = newData2[newData2['tradingsymbol'].str.contains(callTyp)]
    newData1 = newData3[newData3['tradingsymbol'].str.contains(
        SY.getMonth(datetime.datetime.now().month))]
    newData = newData1.iloc[::-1]
    instrumentValue = 0
    for ind in newDataBankNifty.index-1:
        if SY.getMonth(datetime.datetime.now().month) in newData.iloc[ind]['tradingsymbol']:
            getValue = "NFO:" + newData.iloc[ind]['tradingsymbol']
            priceData = get_value(getValue)
            price = priceData[getValue]['last_price']
            if price > startPrice and price < EndPrice:
                instrumentValue = newData.iloc[ind]['tradingsymbol']
                break
    return instrumentValue


def get_status(order_id):

    order_data = pd.DataFrame(kite.order_history(order_id=order_id))
    status = order_data['status'][len(order_data)-1]
    return status

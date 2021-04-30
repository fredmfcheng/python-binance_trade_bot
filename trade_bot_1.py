import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

RSI_PERIOD = 14 # set RSI period
RSI_OVERBOUGHT = 70 # set RSI threshold
RSI_OVERSOLD = 30   # set RSI threshold
TRADE_SYMBOL = 'BTCUSD' # set coin type
TRADE_QUANTITY = 0.05

# socket for getting candle stick data
SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

closes = []   # a list for storing the close prices
in_position = False   # a variable for checking if in position

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)

    except Exception as e:
        print("An exception occured - {}".format(e))
        return False

    return True

def on_open(ws):
    print('*** opened connection ***')

def on_close(ws):
    print('*** closed connection ***')

def on_message(ws, message):
    global closes, in_position

    print('*** received message ***')
    json_message = json.loads(message)
    pprint.pprint(json_message)
    print("======================================")
    print()

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:     # taking only the closing candle stick for the period
        print("Candle Stick closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD: # checking if enough data for RSI computation
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("*** RSI calculated: ***")
            print(rsi)
            last_rsi = rsi[-1]
            print("Current RSI: {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT: # condition for SELL
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is OVERBOUGHT, but we don't hold anything at the moment.")

            if last_rsi < RSI_OVERSOLD: # condition for BUY
                if in_position:
                    print("It is OVERSOLD, but we are already in position.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

import cryptowatch as cw
from datetime import datetime, timedelta

# cryptowatch market data API: https://cryptowat.ch/products/cryptocurrency-market-data-api

#print(cw.markets.list()) # print all available markets

# Get all Kraken markets
kraken = cw.markets.list("kraken")
bittrex = cw.markets.list("bittrex")
binance_us = cw.markets.list("binance-us")
coinbase_pro = cw.markets.list("coinbase-pro")
cexio = cw.markets.list("cexio")
bitfinex = cw.markets.list("bitfinex")
poloniex = cw.markets.list("poloniex")
liquid = cw.markets.list("liquid")
gateio = cw.markets.list("gateio")
coinone = cw.markets.list("coinone")
okex = cw.markets.list("okex")
ftx = cw.markets.list("ftx")
binance = cw.markets.list("binance")
hitbtc = cw.markets.list("hitbtc")
bitstamp = cw.markets.list("bitstamp")
huobi = cw.markets.list("huobi")
bitz = cw.markets.list("bitz")


def get_top_performers(market_name):
    for market in kraken.markets:

        # Forge current market ticker, like KRAKEN:BTCUSD
        ticker = "{}:{}".format(market.exchange, market.pair).upper()
        # Request weekly candles for that market
        candles = cw.markets.get(ticker, ohlc=True, periods=["1w"])

        # Each candle is a list of [close_timestamp, open, high, low, close, volume, volume_quote]
        # Get close_timestamp, open and close from the most recent weekly candle
        close_ts, wkly_open, wkly_close = (
            candles.of_1w[-1][0],
            candles.of_1w[-1][1],
            candles.of_1w[-1][4],
        )

        # Compute market performance, skip if open was 0
        if wkly_open == 0:
            continue
        perf = (wkly_open - wkly_close) * 100 / wkly_open

        # If the market performance was 5% or more, print it
        if perf >= 5:
            open_ts = datetime.utcfromtimestamp(close_ts) - timedelta(days=7)
            print("{} gained {:.2f}% since {}".format(ticker, perf, open_ts))
    
    return

get_top_performers(kraken)

# For each Kraken market...
# for market in kraken.markets:

#     # Forge current market ticker, like KRAKEN:BTCUSD
#     ticker = "{}:{}".format(market.exchange, market.pair).upper()
#     # Request weekly candles for that market
#     candles = cw.markets.get(ticker, ohlc=True, periods=["1w"])

#     # Each candle is a list of [close_timestamp, open, high, low, close, volume, volume_quote]
#     # Get close_timestamp, open and close from the most recent weekly candle
#     close_ts, wkly_open, wkly_close = (
#         candles.of_1w[-1][0],
#         candles.of_1w[-1][1],
#         candles.of_1w[-1][4],
#     )

#     # Compute market performance, skip if open was 0
#     if wkly_open == 0:
#         continue
#     perf = (wkly_open - wkly_close) * 100 / wkly_open

#     # If the market performance was 5% or more, print it
#     if perf >= 5:
#         open_ts = datetime.utcfromtimestamp(close_ts) - timedelta(days=7)
#         print("{} gained {:.2f}% since {}".format(ticker, perf, open_ts))


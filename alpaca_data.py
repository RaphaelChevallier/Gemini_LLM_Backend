import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import pdfkit
import requests
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.historical import (CryptoHistoricalDataClient,
                                    StockHistoricalDataClient)
from alpaca.data.requests import (CryptoBarsRequest, StockBarsRequest,
                                  StockQuotesRequest, StockSnapshotRequest,
                                  StockTradesRequest)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, AssetStatus, TimeInForce
from alpaca.trading.requests import (GetAssetsRequest, GetOrdersRequest,
                                     LimitOrderRequest, OrderSide,
                                     QueryOrderStatus)
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv('.env')

def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date -= timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date

# no keys required.
crypto_client = CryptoHistoricalDataClient()

trading_client = TradingClient(os.getenv('APCA-API-KEY-ID'),  os.getenv('APCA-API-SECRET-KEY'), paper=True)

default_stocks=['MSFT',
'AAPL',
'NVDA',
'GOOG',
'GOOGL',
'AMZN',
'META',
'AVGO',
'TSLA',
'COST',
'AMD',
'NFLX',
'PEP',
'ADBE',
'LIN',
'CSCO',
'TMUS',
'QCOM',
'INTC',
'INTU',
'CMCSA',
'AMAT',
'TXN',
'AMGN',
'ISRG',
'HON',
'MU',
'LRCX',
'BKNG',
'VRTX',
'ABNB',
'REGN',
'SBUX',
'ADP',
'ADI',
'KLAC',
'MDLZ',
'PANW',
'GILD',
'SNPS',
'CDNS',
'EQIX',
'CRWD',
'CME',
'MAR',
'CSX',
'WDAY',
'PYPL',
'CTAS',
'ORLY']
# 'BRK/A',
# 'BRK/B',
# 'LLY',
# 'JPM',
# 'V',
# 'WMT',
# 'XOM',
# 'UNH',
# 'MA',
# 'PG',
# 'JNJ',
# 'HD',
# 'ORCL',
# 'MRK',
# 'ABBV',
# 'BAC',
# 'CVX',
# 'CRM',
# 'KO',
# 'DIS',
# 'CCZ',
# 'TMO',
# 'WFC',
# 'MCD',
# 'ABT',
# 'GE',
# 'DHR',
# 'CAT',
# 'IBM',
# 'TBC',
# 'TBB',
# 'AXP',
# 'UBER',
# 'PFE',
# 'NOW',
# 'MS',
# 'UNP',
# 'COP',
# 'LOW',
# 'NKE',
# 'PM',
# 'SYK',
# 'GS',
# 'SPGI',
# 'SCHW',
# 'NEE',
# 'RTX',
# 'UPS',
# 'T',
# 'BLK',

default_timeframe = TimeFrame.Week

default_history_bars = datetime.now(timezone.utc) - relativedelta(years=1)

default_history_quotes= date_by_adding_business_days(datetime.now(timezone.utc), 1)

default_history_trades = date_by_adding_business_days(datetime.now(timezone.utc), 1)

# keys required
stock_client = StockHistoricalDataClient(os.getenv('APCA-API-KEY-ID'),  os.getenv('APCA-API-SECRET-KEY'))

def getCurrentSnapshots(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks):
    multisymbol_request_params = StockSnapshotRequest(symbol_or_symbols=symbols)

    latest_multisymbol_snapshots = stock_client.get_stock_snapshot(multisymbol_request_params)

    return latest_multisymbol_snapshots

def createLimitOrder(symbol: str, price:float, qty:int, action: str, trading_client: TradingClient = trading_client):
    if action == "buy":
        limit_order_data = LimitOrderRequest(
                        symbol=symbol,
                        limit_price=price,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.FOK
                    )
    elif action == "sell":
        limit_order_data = LimitOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        limit_price=price,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.FOK
                    )
    
    # Limit order
    limit_order = trading_client.submit_order(
                    order_data=limit_order_data
                )
    print(limit_order)
    return limit_order

def getAccountDetails(trading_client: TradingClient = trading_client, symbols: list = default_stocks):
    account = trading_client.get_account()

    request_params = GetOrdersRequest(
                        status=QueryOrderStatus.OPEN,
                    )

    # orders that satisfy params
    orders = trading_client.get_orders(filter=request_params)

    positions = trading_client.get_all_positions()
    for position in positions:
        position = position.model_dump()
        position.pop('asset_id')
    for order in orders:
        order = order.model_dump()
    account = account.model_dump()
    return positions, orders, account['cash']

def getStockTrades(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=default_history_trades):
    multisymbol_request_params = StockTradesRequest(symbol_or_symbols=symbols, start=start)
    print(multisymbol_request_params)
    latest_multisymbol_trades = stock_client.get_stock_trades(multisymbol_request_params)
    dataframe = latest_multisymbol_trades.df
    dataframe.to_pickle("tradesHistory_df")

    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'tradesHistory.pdf')

def getStockQuotes(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=default_history_quotes):
    multisymbol_request_params = StockQuotesRequest(symbol_or_symbols=symbols, start=start)

    latest_multisymbol_quotes = stock_client.get_stock_quotes(multisymbol_request_params)
    dataframe = latest_multisymbol_quotes.df
    dataframe.to_pickle("quotesHistory_df")

    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'quotesHistory.pdf')

def getStockBarsForLastYear(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=default_history_bars, timeframe: TimeFrame = TimeFrame.Month):
    multisymbol_request_params = StockBarsRequest(symbol_or_symbols=symbols, start=start, timeframe=timeframe)

    latest_multisymbol_bars = stock_client.get_stock_bars(multisymbol_request_params)

    dataframe = latest_multisymbol_bars.df
    dataframe.to_pickle("barsHistoryLastYear_df")
    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'barsHistoryLastYear.pdf')

def getStockBarsForLastWeek(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=date_by_adding_business_days(datetime.now(timezone.utc), 5), timeframe: TimeFrame = TimeFrame.Day):
    multisymbol_request_params = StockBarsRequest(symbol_or_symbols=symbols, start=start, timeframe=timeframe)

    latest_multisymbol_bars = stock_client.get_stock_bars(multisymbol_request_params)

    dataframe = latest_multisymbol_bars.df
    dataframe.to_pickle("barsHistoryWeek_df")
    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'barsHistoryWeek.pdf')

def getStockBarsForLastMonth(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=date_by_adding_business_days(datetime.now(timezone.utc), 30), timeframe: TimeFrame = TimeFrame.Week):
    multisymbol_request_params = StockBarsRequest(symbol_or_symbols=symbols, start=start, timeframe=timeframe)

    latest_multisymbol_bars = stock_client.get_stock_bars(multisymbol_request_params)

    dataframe = latest_multisymbol_bars.df
    dataframe.to_pickle("barsHistoryMonth_df")
    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'barsHistoryMonth.pdf')

def getStockBarsForDay(stock_client: StockHistoricalDataClient = stock_client, symbols: list=default_stocks, start: datetime=date_by_adding_business_days(datetime.now(timezone.utc), 1), timeframe: TimeFrame = TimeFrame(amount=30, unit=TimeFrameUnit.Minute)):
    multisymbol_request_params = StockBarsRequest(symbol_or_symbols=symbols, start=start, timeframe=timeframe)

    latest_multisymbol_bars = stock_client.get_stock_bars(multisymbol_request_params)

    dataframe = latest_multisymbol_bars.df
    dataframe.to_pickle("barsHistoryDay_df")
    dataframe.to_html('output.html')

    pdfkit.from_file('output.html', 'barsHistoryDay.pdf')

if __name__ == "__main__":
    # getCurrentSnapshots()
    # getStockTrades(symbols=['AAPL', 'GOOG', 'AMZN', 'TSLA'], start=datetime.now(timezone.utc).replace(hour=16, minute=7, second=0, microsecond=0))
    # getStockQuotes()
    # getStockBarsForLastWeek()
    # getStockBarsForLastYear()
    # getStockBarsForDay()
    getAccountDetails()
import base64
import json
import os
from datetime import datetime, timezone
import sys

import pandas as pd
import vertexai
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai import generative_models
from vertexai.generative_models import Content, GenerativeModel, Part

from alpaca_data import (createLimitOrder, getAccountDetails,
                         getCurrentSnapshots, getStockBarsForDay,
                         getStockBarsForLastMonth, getStockBarsForLastWeek,
                         getStockBarsForLastYear, getStockQuotes,
                         getStockTrades)
from trading_llm_tools import createOrder, getSpecificTickerData

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
   credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)


AgentModel = GenerativeModel("gemini-1.0-pro-vision")
ChatAgentModel = GenerativeModel("gemini-1.0-pro", tools=[getSpecificTickerData])

def countTokens(input):
    return AgentModel.count_tokens(input)

def llm_year_analysis():
    f = open ('analysis.json', "r")
    data = json.loads(f.read())
    f.close()
    config = {"max_output_tokens": 800, "temperature": 0.2, "top_p": 1, "top_k": 32}
    getStockBarsForLastYear()
    lastYear = open('barsHistoryLastYear.pdf', 'rb')
    bs64LastYear = base64.b64encode(lastYear.read())
    lastYear.close()
    imageYear = generative_models.Part.from_data(data=base64.b64decode(bs64LastYear), mime_type="application/pdf")
    if data and 'yearAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here was your previous yearly analysis last month on the stock market: {data['yearAnalysisResponse']}. This table is the bar candle chart for the past year with a month long timeframe for each candle for all the stocks worth following. Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 20 respectively from the image table: ", imageYear]
    else:
        prompt = [f"You are an expert stock day trader. This table is the bar candle chart for the past year with a month long timeframe for each candle for all the stocks worth following . Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 20 respectively from the image table: ", imageYear]
    response = AgentModel.generate_content(prompt, generation_config=config)
    dictionary = {
        "yearAnalysisPrompt" : prompt[0] + 'barsHistoryLastYear.pdf',
        "yearAnalysisResponse": response.text,
        "yearAnalysisDatetime" : datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") 
    }

    with open("analysis.json", "r+") as outfile:
        file_data = json.load(outfile)
        file_data.update(dictionary)
        outfile.seek(0)
        json.dump(file_data, outfile, indent = 4)

def llm_month_analysis():
    f = open ('analysis.json', "r")
    data = json.loads(f.read())
    f.close()
    config = {"max_output_tokens": 800, "temperature": 0.1, "top_p": 1, "top_k": 32}
    getStockBarsForLastMonth()
    lastMonth = open('barsHistoryMonth.pdf', 'rb')
    bs64LastMonth = base64.b64encode(lastMonth.read())
    lastMonth.close()
    imageMonth = generative_models.Part.from_data(data=base64.b64decode(bs64LastMonth), mime_type="application/pdf")
    if data and 'yearAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your previous month analysis from last week on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageMonth]
    if data and 'monthAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your previous month analysis from last week on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageMonth]
    if data and 'yearAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageMonth]
    else:
        prompt = [f"You are an expert stock day trader. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageMonth]
    response = AgentModel.generate_content(prompt, generation_config=config)
    dictionary = {
        "monthAnalysisPrompt" : prompt[0] + 'barsHistoryLastMonth.pdf',
        "monthAnalysisResponse": response.text,
        "monthAnalysisDatetime" : datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") 
    }

    with open("analysis.json", "r+") as outfile:
        file_data = json.load(outfile)
        file_data.update(dictionary)
        outfile.seek(0)
        json.dump(file_data, outfile, indent = 4)

def llm_week_analysis():
    f = open ('analysis.json', "r")
    data = json.loads(f.read())
    f.close()
    config = {"max_output_tokens": 800, "temperature": 0, "top_p": 1, "top_k": 32}
    getStockBarsForLastWeek()
    lastWeek = open('barsHistoryWeek.pdf', 'rb')
    bs64LastWeek = base64.b64encode(lastWeek.read())
    lastWeek.close()
    imageWeek = generative_models.Part.from_data(data=base64.b64decode(bs64LastWeek), mime_type="application/pdf")
    if data and 'yearAnalysisResponse' in data and 'weekAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageWeek]
    elif data and 'weekAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageWeek]
    elif data and 'yearAnalysisResponse' in data and 'weekAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these all stocks and use multiple algorithms as well as compare the performance to the week long table from before: ", imageWeek]
    elif data and 'yearAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these all stocks and use multiple algorithms as well as compare the performance to the week long table from before: ", imageWeek]
    elif data and 'weekAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageWeek]
    else:
        prompt = [f"You are an expert stock day trader. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following .  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 15 respectively from the image table: ", imageWeek]
    response = AgentModel.generate_content(prompt, generation_config=config)
    dictionary = {
        "weekAnalysisPrompt" : prompt[0] + 'barsHistoryLastWeek.pdf',
        "weekAnalysisResponse": response.text,
        "weekAnalysisDatetime" : datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") 
    }
    with open("analysis.json", "r+") as outfile:
        file_data = json.load(outfile)
        file_data.update(dictionary)
        outfile.seek(0)
        json.dump(file_data, outfile, indent = 4)

def llm_current_analysis():
    f = open ('analysis.json', "r")
    data = json.loads(f.read())
    f.close()
    config = {"max_output_tokens": 800, "temperature": 0, "top_p": 1, "top_k": 32}
    getStockBarsForDay()
    current = open('barsHistoryDay.pdf', 'rb')
    bs64Current = base64.b64encode(current.read())
    current.close()
    imageCurrent = generative_models.Part.from_data(data=base64.b64decode(bs64Current), mime_type="application/pdf")
    if data and 'yearAnalysisResponse' in data and 'weekAnalysisResponse' in data and 'monthAnalysisResponse' in data and 'currentAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Your current year analysis for the lastest year on the stock market: {data['yearAnalysisResponse']}. Your current month analysis for the latest month on the stock market: {data['monthAnalysisResponse']}. Your week-long analysis from yesterday for the latest week on the stock market: {data['weekAnalysisResponse']}. Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}.  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. I want 10 for downtrends and uptrends respectively: ", imageCurrent]
    elif data and 'weekAnalysisResponse' in data and 'monthAnalysisResponse' in data and 'currentAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}.  Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on all these stocks as well as compare the performance to the day long table from before. Please make analysises on these stocks as well as compare the performance to the day long table from before: ", imageCurrent]
    elif data and 'yearAnalysisResponse' in data and 'weekAnalysisResponse' in data and 'currentAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}.  Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on all these stocks as well as compare the performance to the day long table from before. Please make analysises on these stocks as well as compare the performance to the day long table from before: ", imageCurrent]
    elif data and 'yearAnalysisResponse' in data and 'monthAnalysisResponse' in data and 'currentAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}.  Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on all these stocks as well as compare the performance to the day long table from before. Please make analysises on these stocks as well as compare the performance to the day long table from before: ", imageCurrent]
    elif data and 'weekAnalysisResponse' in data and 'currentAnalysisResponse' in data:
        prompt = [f"You are an expert stock day trader. Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}.  Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on all these stocks as well as compare the performance to the day long table from before. Please make analysises on these stocks as well as compare the performance to the day long table from before: ", imageCurrent]
    elif 'currentAnalysisResponse' in data :
        prompt = [f" Your previous day bar chart analysis 30 mins ago: {data['currentAnalysisResponse']}. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on these stocks as well as compare the performance to the day long table from before.  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 10 respectively from the image table: ", imageCurrent]
    else:
        prompt = [f"You are an expert stock day trader. This table is the bar candle chart for today with a 30 minute long timeframe for each candle for all the stocks worth following. Please make analysises on these stocks as well as compare the performance to the day long table from before.  Please make analysises on all these stocks with technical analysis techniques and be specific with which stocks to prioritize for both downtrend and uptrend. I want at least 10 respectively from the image table: ", imageCurrent]
    response = AgentModel.generate_content(prompt, generation_config=config)
    if len(response.text) > 10:
        dictionary = {
            "currentAnalysisPrompt" : prompt[0] + 'barsHistoryDay.pdf',
            "currentAnalysisResponse": response.text,
            "currentAnalysisDatetime" : datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") 
        }
        config = {"max_output_tokens": 800, "temperature": 0, "top_p": 1, "top_k": 32} 
        with open("analysis.json", "r+") as outfile:
            file_data = json.load(outfile)
            file_data.update(dictionary)
            outfile.seek(0)
            json.dump(file_data, outfile, indent = 4)
        try:
            f = open ('analysis.json', "r")
            json.loads(f.read())
        except:
            with open("analysis.json", "r+") as outfile:
                outfile.seek(0)
                json.dump(data, outfile, indent = 4)
        finally:
            f.close()
        

def createPlan():
    chat = ChatAgentModel.start_chat()
    f = open ('analysis.json', "r")
    data = json.loads(f.read())
    f.close()
    config = {"max_output_tokens": 800, "temperature": 0, "top_p": 1, "top_k": 32}
    portfolioState, orderState, buyingPower = getAccountDetails()
    if 'yearAnalysisResponse' in data:
        chat.history.append(Content(role='user', parts=[Part.from_text(data['yearAnalysisPrompt'])]))
        chat.history.append(Content(role='model', parts=[Part.from_text(data['yearAnalysisResponse'])]))
    if 'monthAnalysisResponse' in data:
        chat.history.append(Content(role='user', parts=[Part.from_text(data['monthAnalysisPrompt'])]))
        chat.history.append(Content(role='model', parts=[Part.from_text(data['monthAnalysisResponse'])]))
    if 'weekAnalysisResponse' in data:
        chat.history.append(Content(role='user', parts=[Part.from_text(data['weekAnalysisPrompt'])]))
        chat.history.append(Content(role='model', parts=[Part.from_text(data['weekAnalysisResponse'])]))
    if 'currentAnalysisResponse' in data:
        chat.history.append(Content(role='user', parts=[Part.from_text(data['currentAnalysisPrompt'])]))
        chat.history.append(Content(role='model', parts=[Part.from_text(data['currentAnalysisResponse'])]))
    if float(buyingPower) > 10000.0:
        buyingPower = 10000.0
    if float(buyingPower) <= 100.0:
        prompt = [f"""You are an expert stock day trader. You make trades every 30 minutes to maximize profits. You have used up all your buying power and can only sell. Consider your current portfolio as well: {portfolioState} and consider your open orders: {orderState}. After viewing the yearly, monthly, weekly, and the day bar charts earlier in our context and previous messages keep them in mind. Prioritize day trading strategies
        and the current day bar chart analysis and the market snapshot data from your tool with only some minor influence from the other longer interval charts as well as use the performances of your current positions and their intraday performance. Consider all ticker symbols that have been analyzed. Let's move to make market decisions.
        You currently have numerous tools at your disposal such as "get_specific_ticker_symbol_market_snapshots" to assess what actions you want to take between selling, or holding current positions. Always use the tool! The tool gets you a current snapshot of all the stocks you want to analyze more closely to help make your decision for the next 30 minutes by giving you data on latest trade, latest quote, yesterday bar chart and today's current chart as well as the current minute interval bar candle.
        Make a decision on what stocks to sell for the next 30 minutes or to hold your current positions. Do not sell stocks that currently have an active order! Do not sell positions that you do not have! Please be very specific in the actions you want to take including price to sell, quantity to sell, etc."""]
    elif portfolioState == []:
        prompt = [f"""You are an expert stock day trader. You make trades every 30 minutes to maximize profits. You can only buy. You only have ${buyingPower} dollars in USD. Do not go over this limit! Consider your open orders: {orderState}. After viewing the yearly, monthly, weekly, and the day bar charts earlier in our context and previous messages keep them in mind. Prioritize day trading strategies
        and the current day bar chart analysis and the market snapshot data from your tool with only some minor influence from the other longer interval charts. Consider all ticker symbols that have been analyzed. Let's move to make market decisions.
        You currently have numerous tools at your disposal such as "get_specific_ticker_symbol_market_snapshots" to assess what actions you want to take between buying, or holding current positions or if you want to get new positions. Always use the tool! The tool gets you a current snapshot of all the stocks you want to analyze more closely to help make your decision for the next 30 minutes by giving you data on latest trade, latest quote, yesterday bar chart and today's current chart as well as the current minute interval bar candle.
        Make a decision on what stocks to buy for the next 30 minutes or to hold your current positions or new positions. Consider all ticker symbols that have been analyzed and ones in current positions. Do not buy stocks that currently have an active order! Please be very specific in the actions you want to take including price to buy, quantity to buy, etc."""]
    else:
        prompt = [f"""You are an expert stock day trader. You only have ${buyingPower} dollars in USD. Do not go over this limit! Consider your current portfolio: {portfolioState} and consider your open orders: {orderState}. You make trades every 30 minutes to maximize profits so view these trades as short term. After viewing the yearly, monthly, weekly, and the day bar charts earlier in our context and previous messages keep them in mind. Prioritize day trading strategies
        and the current day bar chart analysis and the market snapshot data from your tool with only some minor influence from the other longer interval charts as well as use the performances of your current positions and their intraday performance. Consider all ticker symbols that have been analyzed. Let's move to make market decisions.
        You currently have numerous tools at your disposal such as "get_specific_ticker_symbol_market_snapshots" to assess what actions you want to take between buying, selling, or holding current positions or if you want to get new positions. Always use the tool! The tool gets you a current snapshot of all the stocks you want to analyze more closely to help make your decision for the next 30 minutes by giving you data on latest trade, latest quote, yesterday bar chart and today's current chart as well as the current minute interval bar candle.
        Make a decision on what stocks to buy and sell for the next 30 minutes or to hold your current positions or new positions. Consider all ticker symbols that have been analyzed and ones in current positions. Do not buy or sell stocks that currently have an active order! Do not sell positions that you do not have! Please be very specific in the actions you want to take including price to buy/sell, quantity to buy/sell, etc."""]
    response = chat.send_message(prompt, generation_config=config)
    print(response)
    if response.candidates and response.candidates[0].content.parts[0].function_call.name == "get_specific_ticker_symbol_market_snapshots":
        # Extract the arguments to use in your API call
        try:
            ticker_list = (
                response.candidates[0].content.parts[0].function_call.args["symbol_ticker_list"]
            )
        except Exception as e:
            ticker_list = []
        if ticker_list:
            # getLatestQuotesDate = pd.read_pickle("./quotesHistory_df")
            # getLatestTradesDate = pd.read_pickle("./tradesHistory_df")
            # getLatestQuotesDate['timestamp'] = pd.to_datetime(getLatestQuotesDate['timestamp'])
            # latest_date_quotes = getLatestQuotesDate['timestamp'].max()
            # getLatestQuotesDate['timestamp'] = pd.to_datetime(getLatestTradesDate['timestamp'])
            # latest_date_trades = getLatestTradesDate['timestamp'].max()
            # if datetime.now(timezone.utc) - latest_date_quotes > 86400:
            #     latest_date_quotes = datetime.now(timezone.utc).replace(hour=13, minute=30, second=0, microsecond=0)
            # if datetime.now(timezone.utc) - latest_date_trades > 86400:
            #     latest_date_trades = datetime.now(timezone.utc).replace(hour=13, minute=30, second=0, microsecond=0)
            # getStockQuotes(symbols=ticker_list, start=latest_date_quotes)
            # getStockTrades(symbols=ticker_list, start=latest_date_trades)
            currentSnapshots = getCurrentSnapshots(symbols=ticker_list)
            for k, v in currentSnapshots.items():
                currentSnapshots[k] = v.model_dump()
                for key, value in currentSnapshots[k].items():
                    if isinstance(value, dict):
                        value.pop('timestamp', None)
            response = chat.send_message(
                Part.from_function_response(
                    name="get_specific_ticker_symbol_market_snapshots",
                    response={
                        "content": currentSnapshots,
                    },
                ),
            )
            summary = response.candidates[0].content.parts[0].text
            print(summary)
            if float(buyingPower) <= 100.0:
                newPrompt = [f"""You are an expert day trader. This is your result from analysis: {summary}. Ok you have made your analysis now and can execute on it by using your tool. You have no more cash so you cannot create buy orders, only sell orders. You must evaluate your current positions portfolio: {portfolioState} and evaluate your already open orders to not duplicate: {orderState}. Do not sell positions that you do not have! If portfolio is empty then you have nothing to sell! And do not sell stocks that currently have an active order! Once you have made your decisions and use your tool to create your orders. Specify the list of ticker symbols, list of prices, list of quantities, and list of limit order commands ('sell' only since no buying power). These lists should be respective to the list of ticker symbols."""]
            else:
                if float(buyingPower) > 10000.0:
                    buyingPower = 10000.0
                newPrompt = [f"""You are an expert day trader. This is your most up to date analysis: {summary}. With this analysis of symbol tickers you can execute limit orders on them by using your tool. You only have ${buyingPower} dollars in USD. Do not go over this limit! Divide the buying power dollar amount with all the stocks so you have orders for each one. You must evaluate your current positions portfolio: {portfolioState} and evaluate your already open orders to not duplicate: {orderState}. Do not buy or sell stocks that currently have an active order! Do not sell positions that you do not have! If portfolio is empty then you have nothing to sell! Use your tool to create your orders on market for both buy and sell commands. Specify the list of ticker symbols, list of prices, list of quantities, and list of limit order commands ('sell' or 'buy'). These lists should be respective to the list of ticker symbols."""]
            final = AgentModel.generate_content(newPrompt, generation_config=config, tools=[createOrder])
            if final.candidates and final.candidates[0].content.parts[0].function_call.name == "create_new_limit_order":
                try:
                    ticker_list = (
                        final.candidates[0].content.parts[0].function_call.args["symbol_ticker_list"]
                    )
                    prices = (
                        final.candidates[0].content.parts[0].function_call.args["prices"]
                    )
                    quantities = (
                        final.candidates[0].content.parts[0].function_call.args["quantities"]
                    )
                    commands = (
                        final.candidates[0].content.parts[0].function_call.args["commands"]
                    )
                    if ticker_list and prices and quantities and commands and len(ticker_list) == len(prices) and len(ticker_list) == len(quantities) and len(ticker_list) == len(commands):
                        for index, ticker in enumerate(ticker_list):
                            createLimitOrder(symbol=ticker, price=prices[index], qty=quantities[index], action=commands[index])
                except Exception as e:
                    ticker_list = []
                    prices = []
                    quantities = []
                    commands = []

if __name__ == "__main__":
    # llm_year_analysis()
    # llm_month_analysis()
    # llm_week_analysis()
    llm_current_analysis()
    # createPlan()
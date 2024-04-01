import base64
import json
import os
from datetime import datetime, timezone

import vertexai
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from vertexai import generative_models
from vertexai.generative_models import (ChatSession, Content, GenerativeModel,
                                        Image, Part)

from alpaca_data import (getCurrentSnapshots, getStockBarsForDay,
                         getStockBarsForLastMonth, getStockBarsForLastWeek,
                         getStockBarsForLastYear)

credentials = Credentials.from_service_account_file(os.getenv('GOOGLE_KEY_PATH'), scopes=['https://www.googleapis.com/auth/cloud-platform'])
if credentials.expired:
   credentials.refresh(Request())

vertexai.init(project = os.getenv('GOOGLE_PROJECT_ID'), location = os.getenv('GOOGLE_REGION'), credentials = credentials)

AgentModel = GenerativeModel("gemini-1.0-pro-vision")
chat = AgentModel.start_chat()

def countTokens(input):
    return AgentModel.count_tokens(input)

currentSnapshots = getCurrentSnapshots()
print(currentSnapshots)

# getStockBarsForLastWeek()
# getStockBarsForLastYear()
getStockBarsForDay()

def get_chat_response(chat: ChatSession,  prompt: str) -> str:
    config = {"max_output_tokens": 500, "temperature": 0, "top_p": 1, "top_k": 32}
    text_response = []
    responses = chat.send_message(prompt, generation_config=config, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

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
        prompt = [f"Here was your previous yearly analysis last month on the stock market: {data['yearAnalysisResponse']}. This table is the bar candle chart for the past year with a month long timeframe for each candle for all the stocks worth following . Please make analysises on these stocks: ", imageYear]
    else:
        prompt = [f"This table is the bar candle chart for the past year with a month long timeframe for each candle for all the stocks worth following . Please make analysises on these stocks: ", imageYear]
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
        prompt = [f"Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
    elif data and 'weekAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
    elif data and 'yearAnalysisResponse' in data and 'weekAnalysisResponse' in data:
        prompt = [f"Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. And Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
    elif data and 'yearAnalysisResponse' in data and 'monthAnalysisResponse' in data:
        prompt = [f"Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your current month analysis on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
    elif data and 'weekAnalysisResponse' in data:
        prompt = [f"Here is your previous weekly analysis from yesterday on the stock market: {data['weekAnalysisResponse']}. This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
    else:
        prompt = [f"This table is the bar candle chart for the past week with a day long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the month long table from before: ", imageWeek]
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
        prompt = [f"Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. Here is your previous month analysis from last week on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the year long table from before: ", imageMonth]
    if data and 'monthAnalysisResponse' in data:
        prompt = [f"Here is your previous month analysis from last week on the stock market: {data['monthAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the year long table from before: ", imageMonth]
    if data and 'yearAnalysisResponse' in data:
        prompt = [f"Here is your current year analysis on the stock market: {data['yearAnalysisResponse']}. This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the year long table from before: ", imageMonth]
    else:
        prompt = [f"This table is the bar candle chart for the past month with a week long timeframe  for each candle for all the stocks worth following . Please make analysises on these stocks as well as compare the performance to the year long table from before: ", imageMonth]
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

if __name__ == "__main__":
    llm_year_analysis()
    llm_month_analysis()
    llm_week_analysis()
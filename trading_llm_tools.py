from vertexai.generative_models import FunctionDeclaration, Tool

# Specify a function declaration and parameters for an API request
get_specific_screenshots = FunctionDeclaration(
    name="get_specific_ticker_symbol_market_snapshots",
    description="This function takes an array of market ticker symbols and will return the current market snapshots for each one. This will allow for better most up to date data on the ticker symbols you are most interested in. For each ticker symbol this includes the daily bar candle, the latest quote, the latest trade made, the current minute interval candle bar, and the previous daily bar",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {"symbol_ticker_list": {"type": "array", "description": "Array of ticker symbols chosen to get current market snapshots for to help with assessing next actions for these stocks."}}
    },
)

get_specific_daily_quotes = FunctionDeclaration(
    name="get_specific_ticker_symbol_all_quotes_of_day",
    description="This function takes an array of market ticker symbols and will return the current day's quotes for each one. This will allow for better most up to date data on the ticker symbols you are most interested in.",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {"symbol_ticker_list": {"type": "array", "description": "Array of ticker symbols chosen to get current day's quotes for to help with assessing next actions for these stocks."}}
    },
)

get_specific_daily_trades = FunctionDeclaration(
    name="get_specific_ticker_symbol_all_trades_of_day",
    description="This function takes an array of market ticker symbols and will return the current day's trades for each one. This will allow for better most up to date data on the ticker symbols you are most interested in and show insight on trade volume and prices and whale activity.",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {"symbol_ticker_list": {"type": "array", "description": "Array of ticker symbols chosen to get current day's trades for to help with assessing next actions for these stocks."}}
    },
)

create_limit_order = FunctionDeclaration(
    name="create_new_limit_order",
    description="This function creates limit orders. Either selling or buying orders. It takes a list of symbol tickers, a list of prices, list of quantities, and a list of either \'buy\' or \'sell\' commands respectively.",
    # Function parameters are specified in OpenAPI JSON schema format
    parameters={
        "type": "object",
        "properties": {"symbol_ticker_list": {"type": "array", "description": "Array of ticker symbols chosen to create a limit order for."},
                       "prices": {"type": "array", "description": "Array of prices chosen to limit the limit orders with. Respective to the symbol ticker list."},
                       "quantities": {"type": "array", "description": "Array of quantity values. Only whole numbers. Use this with the price to calculate total cost. Respective to the symbol ticker list."},
                       "commands": {"type": "array", "description": "Array of buy or sell command that shows the side of the order. Either only \'buy\' or \'sell\' values. Respective to the symbol ticker list."}}
    },
)

getSpecificTickerData = Tool(
        function_declarations=[
            get_specific_screenshots,
            # get_specific_daily_quotes,
            # get_specific_daily_trades
        ],
    )

createOrder = Tool(
        function_declarations=[
            create_limit_order,
        ],
    )
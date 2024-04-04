import os

from crewai_tools import tool


from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

load_dotenv()
api_key_id = os.getenv('API_KEY_ID')
secret_key = os.getenv('SECRET_KEY')

trading_client = TradingClient(api_key_id, secret_key)

acc = trading_client.get_account()

@tool("returns Alpaca accountount restriction or not")
def check_if_account_restricted() -> bool:
    """Return if account is restricted or not."""
    return acc.trading_blocked


@tool("Get buying power on Alpaca (accountount purchasing power).")
def get_buying_power() -> str:
    """Returns a string with the number of dollars as the purchasing power of the accountount."""
    return f"{acc.buying_power}$"

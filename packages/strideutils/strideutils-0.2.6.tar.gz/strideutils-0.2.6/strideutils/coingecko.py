"""
Exposes an easy API to get prices from coingecko
"""

from strideutils import stride_requests
from strideutils.stride_config import config

COINGECKO_ENDPOINT = "https://pro-api.coingecko.com/"
COINGECKO_PRICE_QUERY = "api/v3/simple/price?ids={ticker_id}&vs_currencies=usd"


def get_token_price(
    ticker: str,
    api_token: str = config.COINGECKO_API_TOKEN,
    cache_response: bool = False,
):
    """
    Reads token price from coingecko
    If a redis_client is provided, then store the value.
    """
    # TODO: Consider using the coingecko ID for stTokens instead of the redemption rate
    # Get redemption rate for calculating st token prices
    redemption_rate = float(1)
    if ticker.startswith('st') and ticker[3].isupper():
        redemption_rate = stride_requests.get_redemption_rate(ticker[2:])
        ticker = ticker[2:]

    coingecko_name = config.get_chain(ticker=ticker).coingecko_name
    endpoint = COINGECKO_ENDPOINT + COINGECKO_PRICE_QUERY.format(ticker_id=coingecko_name)
    headers = {'x-cg-pro-api-key': api_token}

    response = stride_requests.request(endpoint, headers=headers, cache_response=cache_response)
    price = response[coingecko_name]["usd"] * redemption_rate

    return price

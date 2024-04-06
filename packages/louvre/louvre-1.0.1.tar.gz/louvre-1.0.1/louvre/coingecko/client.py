import requests


class Coingecko:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_historical_prices(self, collection, currency="eth", days="max"):
        url = f"https://pro-api.coingecko.com/api/v3/nfts/{collection}/market_chart?vs_currency={currency}&days={days}"
        headers = {"x-cg-pro-api-key": self.api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(
                f"Failed to fetch data: HTTP {response.status_code}, {response.reason}"
            )
            return None

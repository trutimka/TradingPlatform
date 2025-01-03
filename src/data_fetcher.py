import requests


class DataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_realtime_data(self, asset):
        """Fetch realtime data for assets."""
        try:
            url = f'{self.base_url}?function=GLOBAL_QUOTE&symbol={asset}&apikey={self.api_key}'
            response = requests.get(url)
            print(response.json())
            return response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            print(f"Error fetching data for {asset}: {e}")
            return None

    def fetch_historical_data(self, asset, interval='5min'):
        """Fetch historical data for charts tab."""
        try:
            url = (f'{self.base_url}?function=TIME_SERIES_INTRADAY&symbol={asset}&interval={interval}'
                   f'&apikey={self.api_key}&outputsize=full')
            response = requests.get(url)
            print(response.json())
            return response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            print(f"Error fetching data for {asset}: {e}")
            return None

    def fetch_data(self, function, symbol, interval='daily', time_period=14, series_type='close'):
        """Fetch data from Alpha Vantage."""
        url = (f"{self.base_url}?function={function}&symbol={symbol}&interval={interval}"
               f"&time_period={time_period}&series_type={series_type}&apikey={self.api_key}")
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data for {symbol}. Status code: {response.status_code}")
            return None

    def fetch_sma(self, symbol, interval='daily', time_period=14):
        """Fetch Simple Moving Average (SMA) data."""
        data = self.fetch_data("SMA", symbol, interval=interval, time_period=time_period)
        if data:
            return data.get("Technical Analysis: SMA", {})
        return {}

    def fetch_bollinger_bands(self, symbol, interval='daily', time_period=14):
        """Fetch Bollinger Bands data."""
        data = self.fetch_data("BBANDS", symbol, interval=interval, time_period=time_period)
        if data:
            return data.get("Technical Analysis: BBANDS", {})
        return {}

    def fetch_rsi(self, symbol, interval='daily', time_period=14):
        """Fetch Relative Strength Index (RSI) data."""
        data = self.fetch_data("RSI", symbol, interval=interval, time_period=time_period)
        if data:
            return data.get("Technical Analysis: RSI", {})
        return {}

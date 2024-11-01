import requests
import json


class DataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_realtime_data(self, asset):
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={asset}&apikey={self.api_key}'
            response = requests.get(url)
            print(response.json())
            return response.json() if response.status_code == 200 else None
        except requests.RequestException as e:
            print(f"Error fetching data for {asset}: {e}")
            return None

    # def fetch_historical_data(self, asset, start_date, end_date):
    #     url = f'https://api.example.com/historical?symbol={asset}&start={start_date}&end={end_date}&apikey={self.api_key}'
    #     response = requests.get(url)
    #     return response.json() if response.status_code == 200 else None


import requests
import json
import os
from datetime import datetime
import time

class CryptoDataFetcher:
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        self.api_url = "https://api.coingecko.com/api/v3/coins/markets"
        self.params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }

    def fetch_top_20(self):
        """
        Fetches top 20 crypto data.
        1. Tries API.
        2. If successful, saves to cache.
        3. If fails, loads from latest cache.
        """
        try:
            print("Fetching data from CoinGecko API...")
            response = requests.get(self.api_url, params=self.params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Save to cache
            self._save_to_cache(data)
            return self._format_data(data)
            
        except Exception as e:
            print(f"API request failed: {e}")
            print("Attempting to load from cache...")
            return self._load_from_cache()

    def _save_to_cache(self, data):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        filename = f"market_data_{datetime.now().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filepath}")

    def _load_from_cache(self):
        if not os.path.exists(self.cache_dir):
            print("Cache directory does not exist.")
            return []
            
        files = [f for f in os.listdir(self.cache_dir) if f.endswith(".json")]
        if not files:
            print("No cache files found.")
            return []
            
        # Sort by filename (date) desc
        files.sort(reverse=True)
        latest_file = files[0]
        filepath = os.path.join(self.cache_dir, latest_file)
        
        print(f"Loading data from {filepath}")
        with open(filepath, "r") as f:
            data = json.load(f)
            
        return self._format_data(data)

    def _format_data(self, raw_data):
        """
        Formats raw API data into a cleaner structure.
        """
        formatted_list = []
        for item in raw_data:
            formatted_list.append({
                "rank": item.get("market_cap_rank"),
                "name": item.get("name"),
                "symbol": item.get("symbol").upper(),
                "price": item.get("current_price"),
                "market_cap": item.get("market_cap"),
                "change_24h": item.get("price_change_percentage_24h"),
                "image": item.get("image")
            })
        return formatted_list

if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    data = fetcher.fetch_top_20()
    print(json.dumps(data[:3], indent=2))

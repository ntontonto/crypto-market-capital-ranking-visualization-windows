
import requests
import json
import os
import time
from datetime import datetime, timedelta

class CryptoDataFetcher:
    def __init__(self, cache_dir="./cache"):
        self.cache_dir = cache_dir
        self.api_url_base = "https://api.coingecko.com/api/v3"
        
    def generate_input_json(self):
        """
        Orchestrates the fetching of all necessary data to produce the 'input.json' 
        required by the video generator.
        """
        print("Starting full data fetch sequence...")
        
        # 1. Fetch current Top 30
        current_top = self._fetch_current_top_markets(limit=30)
        
        # 2. Fetch Historical 7-day Market Chart
        history_map = {} # { coin_id: { 'market_caps': {date: val}, 'prices': {date: val} } }
        
        print(f"Fetching 7-day history for {len(current_top)} coins...")
        for i, coin in enumerate(current_top):
            coin_id = coin['id']
            print(f"[{i+1}/{len(current_top)}] Fetching history for {coin_id}...")
            history = self._fetch_coin_history_7d(coin_id)
            history_map[coin_id] = history
            time.sleep(4)
            
        # Determine 7 dates (today - 6 days through today)
        today = datetime.utcnow().date()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
            
        # 3. Calculate Dominance History (based on Top 30)
        print("Calculating dominance history (from sum of Top 30)...")
        dominance_series = []
        stable_ids = ["tether", "usd-coin", "dai", "first-digital-usd", "ethena-usde"] 
        
        for d in dates:
            day_total_cap = 0
            btc_cap = 0
            eth_cap = 0
            stable_cap = 0
            
            for c_id, hist in history_map.items():
                # Access market_caps
                cap = hist.get('market_caps', {}).get(d, 0)
                day_total_cap += cap
                
                if c_id == "bitcoin":
                    btc_cap = cap
                elif c_id == "ethereum":
                    eth_cap = cap
                elif c_id in stable_ids:
                    stable_cap += cap
            
            if day_total_cap > 0:
                dominance_series.append({
                    "date": d,
                    "btc_pct": round((btc_cap / day_total_cap) * 100, 1),
                    "eth_pct": round((eth_cap / day_total_cap) * 100, 1),
                    "stable_pct": round((stable_cap / day_total_cap) * 100, 1)
                })
        
        # 4. Construct Output
        top10_7d = []
        for d in dates:
            daily_snapshot = []
            for coin in current_top:
                c_id = coin['id']
                mcap = history_map.get(c_id, {}).get('market_caps', {}).get(d, 0)
                if mcap > 0:
                    daily_snapshot.append({
                        "id": c_id,
                        "symbol": coin['symbol'].upper(),
                        "name": coin['name'],
                        "market_cap": mcap
                    })
            daily_snapshot.sort(key=lambda x: x['market_cap'], reverse=True)
            top10_7d.append({
                "date": d,
                "items": daily_snapshot[:10]
            })
            
        # 5. Build "weekly_top_movers" (7 Days Change)
        # We calculate change from first date to last available date
        movers_list = []
        start_date = dates[0]
        end_date = dates[-1]
        
        for coin in current_top:
            c_id = coin['id']
            prices = history_map.get(c_id, {}).get('prices', {})
            
            # Find closest available start/end prices
            # (Sometimes specific dates are missing, fallback to earliest/latest)
            sorted_dates = sorted(prices.keys())
            if not sorted_dates:
                continue
                
            p_start = prices.get(start_date)
            p_end = prices.get(end_date)
            
            if not p_start: p_start = prices[sorted_dates[0]]
            if not p_end: p_end = prices[sorted_dates[-1]]
            
            if p_start and p_start > 0:
                change_pct = ((p_end - p_start) / p_start) * 100
                movers_list.append({
                    "id": c_id,
                    "symbol": coin['symbol'].upper(),
                    "name": coin['name'],
                    "price": p_end,
                    "change_7d_pct": change_pct,
                    "market_cap": coin['market_cap']
                })
                
        sorted_movers = sorted(movers_list, key=lambda x: x['change_7d_pct'], reverse=True)
        weekly_top_movers = {
            "gainers": sorted_movers[:3],
            "losers": sorted_movers[-3:][::-1] # Bottom 3 reversed (worst first)
        }
        
        # Keep 24h as well if needed, but we focus on weekly here
        
        final_json = {
            "asOf": datetime.utcnow().isoformat() + "Z",
            "currency": "usd",
            "top10_7d": top10_7d,
            "weekly_top_movers": weekly_top_movers,
            "dominance": {
                "series": dominance_series
            }
        }
        
        return final_json

    def _fetch_current_top_markets(self, limit=30):
        url = f"{self.api_url_base}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        print("Fetching current top markets...")
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _fetch_coin_history_7d(self, coin_id):
        """
        Returns a dict with 'market_caps' and 'prices' maps: { "YYYY-MM-DD": value }
        """
        url = f"{self.api_url_base}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "7",
            "interval": "daily" 
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 429:
                print("Rate limit hit. Sleeping 60s...")
                time.sleep(60)
                resp = requests.get(url, params=params, timeout=10)
                
            resp.raise_for_status()
            data = resp.json()
            
            result = {'market_caps': {}, 'prices': {}}
            
            for key in ['market_caps', 'prices']:
                for entry in data.get(key, []):
                    ts = entry[0]
                    val = entry[1]
                    date_str = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                    result[key][date_str] = val
                
            return result
        except Exception as e:
            print(f"Failed to fetch history for {coin_id}: {e}")
            return {'market_caps': {}, 'prices': {}}



if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    # Test run
    # data = fetcher.generate_input_json()
    # print(json.dumps(data, indent=2))

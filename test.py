import pprint

import requests

response = requests.get("https://api.binance.com/api/v3/trades",
                 params=dict(symbol='BTCUSDT'))
results = response.json()
pprint.pprint(results)
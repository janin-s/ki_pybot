import random

import alpaca_trade_api

# endpoint: https://paper-api.alpaca.markets
# api key id:
# secret key: AXBHvjLKqMQPQDEwosddasP0CZqjAUuvV6trCy3x
from alpaca_trade_api.common import URL
from alpaca_trade_api.entity import Asset


# from lib.db import db
def buy_stock(api, a: Asset):
    config = {'symbol': a.symbol,
              'notional': 28.,
              'type': 'market',
              'time_in_force': 'day',
              'order_class': 'simple'}
    response = api.submit_order(**config)
    print(response)
    print(type(response))


api_key_id = 'PKZ0AFHB21M8WVI8UMX3'
api_secret_key = 'AXBHvjLKqMQPQDEwosddasP0CZqjAUuvV6trCy3x'
endpoint = URL('https://paper-api.alpaca.markets')
api = alpaca_trade_api.REST(key_id=api_key_id, secret_key=api_secret_key, base_url=endpoint)

asset_fields = ['class', 'easy_to_borrow', 'exchange', 'fractionable', 'id', 'marginable', 'name', 'shortable',
                'status', 'symbol', 'tradable']

all_assets = api.list_assets(status='active')


unique_classes = set(map(lambda a: a.__getattr__('class'), all_assets))
print(unique_classes)
GME = list(filter(lambda a: a.symbol == 'TSLA', all_assets))
assert GME
print(GME[0])
# buy_stock(api, GME[0])

# t.update_assets()

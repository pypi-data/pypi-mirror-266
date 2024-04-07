#binance network
```python
def get_network(api_key, api_secret):
    client = Spot(api_key=api_key, api_secret=api_secret)  # show_header=True
    return client.coin_info()
```
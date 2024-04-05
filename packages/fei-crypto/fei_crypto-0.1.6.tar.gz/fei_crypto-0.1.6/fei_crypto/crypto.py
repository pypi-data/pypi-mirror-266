import os

import requests


def btc_etc() -> str:
    proxies = None
    proxy = os.getenv('HTTP_PROXY')
    if proxy is not None:
        proxies = {"http": proxy, "https": proxy, }

    resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbols=[%22BTCUSDT%22,%22ETHUSDT%22]",
                        proxies=proxies, timeout=20)

    p = []
    for item in resp.json():
        p.append(format(float(item["price"]), '.2f'))

    return '🍕'.join(p)

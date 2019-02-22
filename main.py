import requests
import time
from datetime import datetime
from json import load
from os import path
import product

with open(path.join(path.dirname(__file__), 'config.json')) as f:
    config = load(f)
    discord_webhook_url = config["webhook"]

# check time (in seconds)
monitor_check = 900


def main():
    searches = []
    collect_products = True
    while collect_products:
        product_name = str(input("Product name: "))
        searches.append(product_name)
        while True:
            res = input("Add more products to monitor? (Y/N) ")
            if res.lower() == 'y':
                break
            elif res.lower() == 'n':
                collect_products = False
                break
            else:
                print("Please enter a valid response.")

    # create objects each with a product put in and add to list
    objects = [product.Product(search) for search in searches]

    print("Monitor Started")
    while True:
        monitor_loop(objects)
        time.sleep(monitor_check)


def monitor_loop(objects):
    for obj in objects:
        product_data = obj.get_data()
        if product_data:
            while True:
                res = discord_hook(**product_data)
                if res == 1:
                    break
                else:
                    print("Webhook failed, trying again.")
                    time.sleep(2)
        else:
            pass
        time.sleep(2)


def discord_hook(product_name, product_url, thumbnail_url, retail, size, last_sale, last_sale_size, lowest_ask, lowest_ask_size, highest_bid, highest_bid_size):
    headers = {
        'Content-type': 'application/json'
    }

    time = str(datetime.utcnow())

    json_time = time.replace(" ", "T")

    payload = {
        "embeds": [
            {
                "title": product_name,
                # "description": "Retail ${} USD".format(retail),
                "url": product_url,
                "color": 4500277,
                "timestamp": json_time,
                "footer": {
                    "text": "By Jin Yi | Data accurate as of time sent"
                },
                "thumbnail": {
                    "url": thumbnail_url
                },
                "author": {
                    "name": "StockX Monitor"
                },
                "fields": [
                    {
                        "name": "Size",
                        "value": size,
                        "inline": True
                    },
                    {
                        "name": "Last Sale",
                        "value": "${} USD | {}".format(last_sale, last_sale_size),
                        "inline": True
                    },
                    {
                        "name": "Lowest Ask",
                        "value": "${} USD | {}".format(lowest_ask, lowest_ask_size),
                        "inline": True
                    },
                    {
                        "name": "Highest Bid",
                        "value": "${} USD | {}".format(highest_bid, highest_bid_size),
                        "inline": True
                    }
                ]
            }
        ]
    }

    r = requests.post(discord_webhook_url, json=payload, headers=headers)
    if r.status_code == 204:
        return 1
    else:
        return 0


if __name__ == '__main__':
    print("StockX Monitor by Jin Yi")
    main()

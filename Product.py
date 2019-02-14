import requests
from bs4 import BeautifulSoup

class Product:
    def __init__(self, product_search):
        self.product_search = product_search
        self.found_product = False
        self.index = 0
        self.product_name = None
        self.product_id = None
        self.ticker_symbol = None
        self.product_url = None
        self.thumbnail_url = None
        self.product_size = None

        while True:
            payload = {
                'x-algolia-agent': 'Algolia for vanilla JavaScript 3.27.1',
                'x-algolia-api-key': '6bfb5abee4dcd8cea8f0ca1ca085c2b3',
                'x-algolia-application-id': 'XW7SBCT9V6'
            }

            json_payload = {
                "params": "query={}&hitsPerPage={}".format(self.product_search, self.index + 1)
            }

            r = requests.post(url='https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query/', params=payload, json=json_payload)
            output = r.json()['hits']

            self.product_name = output[self.index]['name']

            while not self.found_product:
                ans = input("Monitor {}? (Y/N) ".format(self.product_name))
                if ans.lower() == 'y':
                    self.found_product = True
                    self.product_id = output[self.index]['objectID']
                    self.ticker_symbol = output[self.index]['ticker_symbol']
                    self.product_url = 'https://stockx.com/' + output[self.index]['url']
                    self.thumbnail_url = output[self.index]['thumbnail_url']
                    while True:
                        size = str(input("Size for {}? ".format(self.product_name)))
                        if size.lower() == 'all':
                            break
                        else:
                            try:
                                float(size)
                                self.product_size = size
                                break
                            except:
                                print("Please enter a valid size.")
                    return
                elif ans.lower() == 'n':
                    self.index += 1
                    break
                else:
                    print("Please give a valid response.")
       

    def get_data(self):
        if not self.found_product:
            return False        

        product_data = []

        payload = {
            'x-algolia-agent': 'Algolia for vanilla JavaScript 3.27.1',
            'x-algolia-api-key': '6bfb5abee4dcd8cea8f0ca1ca085c2b3',
            'x-algolia-application-id': 'XW7SBCT9V6'
        }

        json_payload = {
            "params": "query={}&hitsPerPage={}".format(self.product_search, self.index + 1)
        }

        r = requests.post(url='https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query/', params=payload, json=json_payload)
        output = r.json()['hits']

        last_sale = output[self.index]['last_sale']
        try:
            retail_price = output[self.index]['searchable_traits']['Retail Price']
        except:
            retail_price = 'None'

        try:
            r = requests.get(url=self.product_url, headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'})

            soup = BeautifulSoup(r.text, 'html.parser')

            last_sale_size = soup.find('div', {'class': 'last-sale-block'}).find(
                'span', {'class':'bid-ask-sizes'}).text.replace(':', '')
            lowest_ask_size = soup.find('div', {'class': 'bid bid-button-b'}).find(
                'span', {'class':'bid-ask-sizes'}).text.replace(':', '')
            highest_bid_size = soup.find('div', {'class': 'ask ask-button-b'}).find(
                'span', {'class':'bid-ask-sizes'}).text.replace(':', '')
        except:
            last_sale_size = "None"
            lowest_ask_size = "None"
            highest_bid_size = "None"

        if self.product_size:
            r = requests.get('https://stockx.com/api/products/{0}/activity?state={1}'.format(self.product_id, 400)) #asks
            order_json = r.json()

            for order in order_json: # search thru all and first one is lowest ask
                if order['shoeSize'] == self.product_size:
                    lowest_ask = round(float(order['amount']))
                    break
            else:
                print("Did not find given size for {}".format(self.product_name))
                return None

            r = requests.get('https://stockx.com/api/products/{0}/activity?state={1}'.format(self.product_id, 300)) #bids
            order_json = r.json()

            for order in order_json: # seach thru all and first one is highest bid
                if order['shoeSize'] == self.product_size:
                    highest_bid = round(float(order['amount']))
                    break
            else:
                print("Did not find given size for {}".format(self.product_name))
                return None

        else:
            lowest_ask = output[self.index]['lowest_ask']
            highest_bid = output[self.index]['highest_bid']
            
        product_data = {
            'product_name': self.product_name,
            'product_url': self.product_url,
            'thumbnail_url': self.thumbnail_url,
            'retail': retail_price,
            'size': self.product_size,
            'last_sale': last_sale,
            'last_sale_size': last_sale_size,
            'lowest_ask': lowest_ask,
            'lowest_ask_size': lowest_ask_size,
            'highest_bid': highest_bid,
            'highest_bid_size': highest_bid_size
        }

        if self.product_size:
            product_data['lowest_ask_size'] = self.product_size
            product_data['highest_bid_size'] = self.product_size
        else:
            product_data['size'] = "All sizes"

        return product_data

if __name__ == "__main__":
	print ("Can't run this file.")
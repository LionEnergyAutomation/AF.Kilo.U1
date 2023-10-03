import json
import time
from timeit import default_timer as timer
import oauth2 as oauth
import requests


class NetsuiteAPI(object):

    def __init__(self):
        """
        These are the only parameters that need to be changed for each account and each new token within each account.
        """
        self.base_url = "https://5518720.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=369&deploy=1"
        self.account_id = "5518720"
        self.consumer_key = "1ee2526e258b6c969731b8feefba58bfd7334a63f417cd0003534d1354657e60"
        self.consumer_secret = "7c460a6e081e551962841c31b5866294c39fe4ee84e5617d4551737ca491169a"
        self.token_key = "4195a005ba3bf230f173272d7425bcf16cbc8f06470533e7e8e0afa3a9e828c2"
        self.token_secret = "066b4228a45bb2a0e39794ec1644373396fc091ed0b7208e951325435069e987"
        self.http_method = ""   # This is set by the appropriate method call
        self.session = requests.Session()
        self.last_request_time = 0

    def get_headers(self, url):
        token = oauth.Token(self.token_key, secret=self.token_secret)
        consumer = oauth.Consumer(key=self.consumer_key, secret=self.consumer_secret)
        realm = self.account_id
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(31),
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': token.key,
            'oauth_consumer_key': consumer.key
        }
        req = oauth.Request(method=self.http_method, url=url, parameters=params)
        signature_method = oauth.SignatureMethod_HMAC_SHA256()
        req.sign_request(signature_method, consumer, token)
        headers = req.to_header(realm)
        headers = headers['Authorization'].encode('ascii', 'ignore')
        headers = {"Authorization": headers, "Content-Type": "application/json"}
        return headers

    def _post(self, data_in):
        self.http_method = "POST"
        headers = self.get_headers(self.base_url)
        start = timer()
        response = self.session.post(self.base_url, json=data_in, headers=headers)
        end = timer()
        self.last_request_time = (end - start)
        return json.loads(response.content)

    def _get(self, params):
        self.http_method = "GET"
        url = requests.Request(self.http_method, self.base_url, params=params).prepare().url
        headers = self.get_headers(url)
        start = timer()
        response = self.session.get(url, headers=headers)
        end = timer()
        self.last_request_time = (end - start)
        return json.loads(response.content)

    def _put(self, data_in):
        self.http_method = "PUT"
        headers = self.get_headers(self.base_url)
        start = timer()
        response = self.session.put(self.base_url, json=data_in, headers=headers)
        end = timer()
        self.last_request_time = (end - start)
        return json.loads(response.content)

    def _delete(self, data_in):
        self.http_method = "DELETE"
        headers = self.get_headers(self.base_url)
        start = timer()
        response = self.session.delete(self.base_url, json=data_in, headers=headers)
        end = timer()
        self.last_request_time = (end - start)
        return json.loads(response.content)

    def get_sales_order_details(self, sales_order_id):
        return self._get({"get_type": "salesorder", "id": sales_order_id})

    def get_customer_details(self, customer_id):
        return self._get({"get_type": "customer", "id": customer_id})

    def create_sales_order(self, data_in):
        data_in["post_type"] = "record_create"
        data_in["record_type"] = "salesorder"
        return self._post(data_in)

    def create_customer(self, data_in):
        data_in["post_type"] = "record_create"
        data_in["record_type"] = "customer"
        return self._post(data_in)

    def create_testing_record(self, data_in):
        data_in["post_type"] = "record_create"
        data_in["record_type"] = "customrecord_testing"
        return self._post(data_in)

    def search_customers(self, data_in):
        data_in["post_type"] = "search"
        return self._post(data_in)

    def search_sales_orders(self, data_in):
        data_in["post_type"] = "search"
        return self._post(data_in)

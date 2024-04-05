import logging
import requests
import copy
from .exceptions import ScraperAPIException

logger = logging.getLogger(__name__)


class ScraperAPIClient:
    def __init__(self, api_key: str, api_endpoint: str = "https://api.scraperapi.com"):
        """Create a new Client instance
        API Key is passed as a query parameter to the API endpoint

        :param api_key: ScraperAPI api_key
        :param api_endpoint: ScraperAPI endpoint
        """
        self.api_key = api_key
        self._api_endpoint = api_endpoint
        self.amazon = Amazon(client=self)
        self.google = Google(client=self)
        self.walmart = Walmart(client=self)

    def _get_headers(self, headers=None):
        if headers is None:
            headers = {}
        return headers

    def _get_params(self, params=None):
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        return params

    def make_request(
        self,
        *,
        url=None,
        method="GET",
        data=None,
        params=None,
        headers=None,
        timeout=55,
        endpoint=None,
        safe=None,
    ):
        if type(params) is not dict:
            params = {}
        params = copy.deepcopy(params)
        if url:
            params["url"] = url
        service_url = f"{self._api_endpoint}/{endpoint}"
        try:
            logger.debug(
                f"Making a {method} request to {url} data={data} params={params} headers={headers}"
            )
            response = requests.request(
                method=method,
                url=service_url,
                params=self._get_params(params),
                data=data,
                headers=self._get_headers(headers),
                timeout=timeout,
            )
            response.raise_for_status()
        except Exception as e:
            raise ScraperAPIException(f"Failed to scrape {method} {url}", e)
        return response

    def scrape(self, url, method, data=None, params=None, headers=None):
        response = self.make_request(
            url=url, method=method, params=params, headers=headers, data=data
        )
        content_type = response.headers.get("Content-Type", "")
        if "text" in content_type:
            return response.text
        elif "json" in content_type:
            return response.json()
        else:
            return response.content

    def get(self, url, params=None, headers=None):
        return self.scrape(url=url, method="GET", params=params, headers=headers)

    def post(self, url, data=None, params=None, headers=None):
        return self.scrape(
            url=url, data=data, method="POST", params=params, headers=headers
        )

    def put(self, url, data=None, params=None, headers=None):
        return self.scrape(
            url=url, data=data, method="PUT", params=params, headers=headers
        )


class Amazon:
    def __init__(self, client):
        super().__init__()
        self.client = client

    def product(self, asin, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/amazon/product",
            params=dict(asin=asin, country=country, tld=tld),
        )
        return response.json()

    def search(self, query, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/amazon/search",
            params=dict(query=query, country=country, tld=tld),
        )
        return response.json()

    def offers(self, asin, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/amazon/offers",
            params=dict(asin=asin, country=country, tld=tld),
        )
        return response.json()

    def review(self, asin, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/amazon/review",
            params=dict(asin=asin, country=country, tld=tld),
        )
        return response.json()

    def prices(self, asins: list | tuple, country=None, tld=None):
        if type(asins) not in (list, tuple):
            raise ValueError("asins must be a list or tuple")
        asins_string = ",".join(asins)
        response = self.client.make_request(
            endpoint=f"structured/amazon/prices?asins={asins_string}",
            params=dict(country=country, tld=tld),
        )
        return response.json()


class Google:
    def __init__(self, client):
        super().__init__()
        self.client = client

    def search(self, query, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/google/search",
            params=dict(query=query, country=country, tld=tld),
        )
        return response.json()

    def news(self, query, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/google/news",
            params=dict(query=query, country=country, tld=tld),
        )
        return response.json()

    def jobs(self, query, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/google/jobs",
            params=dict(query=query, country=country, tld=tld),
        )
        return response.json()

    def shopping(self, query, country=None, tld=None):
        response = self.client.make_request(
            endpoint="structured/google/shopping",
            params=dict(query=query, country=country, tld=tld),
        )
        return response.json()


class Walmart:
    def __init__(self, client):
        super().__init__()
        self.client = client

    def search(self, query, page=None):
        response = self.client.make_request(
            endpoint="structured/walmart/search",
            params=dict(query=query, page=page),
        )
        return response.json()

    def category(self, category, page=None):
        response = self.client.make_request(
            endpoint="structured/walmart/category",
            params=dict(category=category, page=page),
        )
        return response.json()

    def product(self, product_id):
        response = self.client.make_request(
            endpoint="structured/walmart/product",
            params=dict(product_id=product_id),
        )
        return response.json()

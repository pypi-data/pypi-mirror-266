# ScraperAPI Python SDK
## Install 

```
pip install scraperapi-sdk
```


## Usage
```
from scraperapi_sdk import ScraperAPIClient

client = ScraperAPIClient("<API-KEY>")

# regular get request
content = client.get('https://amazon.com/')
# get request with premium
content = client.get('https://amazon.com/', params={'premium': True})

# post request
content = client.post('https://webhook.site/403e44ce-5835-4ce9-a648-188a51d9395d', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'field1': 'data1'})

# put request
content = client.put('https://webhook.site/403e44ce-5835-4ce9-a648-188a51d9395d', headers={'Content-Type': 'application/json'}, data={'field1': 'data1'})
```

The `content` variable will contain the scraped page.

If you want to get the `Response` object instead of the content you can use `make_request`.

```
response = client.make_request(url='https://webhook.site/403e44ce-5835-4ce9-a648-188a51d9395d', headers={'Content-Type': 'application/json'}, data={'field1': 'data1'})
# response will be <Response [200]>
```

## Exception

```
from scraperapi_sdk import ScraperAPIClient
from scraperapi_sdk.exceptions import ScraperAPIException

client = ScraperAPIClient(
    api_key=api_key,
)
try:
    result = client.post('https://webhook.site/403e44ce-5835-4ce9-a648-188a51d9395d', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'field1': 'data1'})
    _ = result
except ScraperAPIException as e:
    print(e.original_exception)  # you can access the original exception via `.original_exception` property.
```


## Structured Data Collection Methods
### Amazon Endpoints
#### Amazon Product Page API

This method will retrieve product data from an Amazon product page and transform it into usable JSON.

```
result = client.amazon.product("<ASIN>")
result = client.amazon.product("<ASIN>", country="us", tld="com")
```

Read more in docs: [Amazon Product Page API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/amazon-product-page-api)

#### Amazon Search API

This method will retrieve products for a specified search term from Amazon search page and transform it into usable JSON.

```
result = client.amazon.search("<QUERY>")
result = client.amazon.search("<QUERY>", country="us", tld="com")
```

Read more in docs: [Amazon Search API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/amazon-search-api)

#### Amazon Offers API
This method will retrieve offers for a specified product from an Amazon offers page and transform it into usable JSON.

```
result = client.amazon.offers("<ASIN>")
result = client.amazon.offers("<ASIN>", country="us", tld="com")
```
Read more in docs: [Amazon Offers API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/amazon-offers-api)

#### Amazon Reviews API 
This method will retrieve reviews for a specified product from an Amazon reviews page and transform it into usable JSON.

```
result = client.amazon.review("<ASIN>")
result = client.amazon.offers("<ASIN>", country="us", tld="com")
```
Read more in docs: [Amazon Reviews API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/amazon-reviews-api)

#### Amazon Prices API 

This method will retrieve product prices for the given ASINs and transform it into usable JSON.

```
result = client.amazon.prices(['<ASIN1>'])
result = client.amazon.prices(['<ASIN1>', '<ASIN2>'])
result = client.amazon.prices(['<ASIN1>', '<ASIN2>'], country="us", tld="com")
```
Read more in docs: [Amazon Prices API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/amazon-prices-api)


### Google API
#### Google SERP API
This method will retrieve product data from an Google search result page and transform it into usable JSON.

```
result = client.google.search('free hosting')
result = client.google.search('free hosting', country="us", tld="com")
```
Read more in docs: [Google SERP API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/google-serp-api)
#### Google News API
This method will retrieve news data from an Google news result page and transform it into usable JSON.
```
result = client.google.news('tornado')
result = client.google.news('tornado', country="us", tld="com")
```
Read more in docs: [Google News API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/google-news-api)

#### Google Jobs API

This method will retrieve jobs data from an Google jobs result page and transform it into usable JSON.

```
result = client.google.jobs('Senior Software Developer')
result = client.google.jobs('Senior Software Developer', country="us", tld="com")
```
Read more in docs: [Google Jobs API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/google-jobs-api)

#### Google Shopping API
This method will retrieve shopping data from an Google shopping result page and transform it into usable JSON.
```
result = client.google.shopping('macbook air')
result = client.google.shopping('macbook air', country="us", tld="com")
```

Read more in docs: [Google Shopping API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/google-shopping-api)

### Walmart API
#### Walmart Search API
This method will retrieve product list data from Walmart as a result of a search.
```
result = client.walmart.search('hoodie')
result = client.walmart.search('hoodie', page=2)
```
Read more in docs: [Walmart Search API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/walmart-search-api)

#### Walmart Category API

This method will retrieve Walmart product list for a specified product category.
```
result = client.walmart.category('5438_7712430_8775031_5315201_3279226')
result = client.walmart.category('5438_7712430_8775031_5315201_3279226', page=2)
```
Read more in docs: [Walmart Category API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/walmart-category-api)

#### Walmart Product API
This method will retrieve Walmart product details for one product.
```
result = client.walmart.product('5053452213')
```

Read more in docs: [Walmart Product API](https://docs.scraperapi.com/making-requests/structured-data-collection-method/walmart-product-api)


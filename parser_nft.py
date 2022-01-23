import typing
import datetime
import requests

from configobj import ConfigObj


cfg = ConfigObj('static/config.cfg')

TOKEN = cfg.get('API_TOKEN')

#URL = 'https://api.opensea.io/api/v1/events'
URL = 'https://testnets-api.opensea.io/api/v1/events'
HEADERS = {
    'Accept': 'application/json',
    'X-API-KEY': TOKEN
}


def _get_data(collection: str,
              limit: int = 1,
              before: float = None,
              after: float = None) -> typing.Dict[str, typing.List[dict]]:

    """
        Requests data from the site: https://api.opensea.io/api/v1/events

        collection: Сollection name.
        limit: Еhe amount of data to receive. Max. 300
        after: Seconds in unix will filter the time data. After.
        before: Seconds in unix will filter the time data. Before.

        https://docs.opensea.io/reference/retrieving-asset-events
    """

    session = requests.Session()
    session.headers = HEADERS

    data = {
        'collection_slug': collection,
        'event_type': 'successful',
        'occurred_before': before,
        'occurred_after': after,
        'only_opensea': False,
        'limit': limit,
        'offset': 0
    }

    response = session.get(URL, params=data)

    if response.ok is False:
        print(f'Request Error: Status {response.status_code}')
        return {}

    return response.json()


def parser(collection: str,
           limit: int = 1,
           timestamp_before: float = None,
           timestamp_after: float = None) -> typing.List[list]:

    """
        Parsing raw data.

        collection: Сollection name.
        limit: Еhe amount of data to receive. Max. 300
        timestamp_after: Seconds in unix will filter the time data. After.
        timestamp_before: Seconds in unix will filter the time data. Before.
    """

    raw_data = _get_data(collection, limit, timestamp_before, timestamp_after)
    pars_data = []

    for data in raw_data.get('asset_events', []):
        token_id = data.get('asset').get('token_id', 0)
        img_url = data.get('asset').get('image_url')
        name = data.get('asset').get('name')

        currency = data.get('payment_token').get('symbol')
        iso_date = data.get('created_date')
        price = data.get('total_price')

        created_at = datetime.datetime.fromisoformat(iso_date)
        name = name if '#' in name else f'{name} #{token_id}'
        date = created_at.strftime('%H:%M %d-%m-%Y')
        price = int(price[::-1][15:][::-1]) / 1000

        pars_data.append([img_url, name, price, currency, date])

    pars_data.reverse()
    return pars_data

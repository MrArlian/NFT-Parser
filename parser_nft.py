from datetime import datetime, timedelta

import typing
import time
import re

import requests

from bs4 import BeautifulSoup


URL = 'https://larvalabs.com/cryptopunks/sales'
HOST = 'https://larvalabs.com'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) \
                   Chrome/96.0.4664.110 Safari/537.36',
    'accept': '*/*'
}

IN_SECONDS = {
    'hours': 3600,
    'hour': 3600,

    'minutes': 60,
    'minute': 60,

    'seconds': 1,
    'second': 1
}


def _get_data(per_page: int = 10) -> str:
    """
        Getting the html template.

        :perPage: Number of items per page.
    """

    session = requests.Session()
    session.headers = HEADERS

    response = session.get(URL, params={'perPage': per_page})

    if response.ok is False:
        print(f'Request Error: Status {response.status_code}')
        return ''

    return response.text


def parser(timestamp_1: float, timestamp_2: float) -> typing.List[list]:
    """
        Parsing raw data.

        :timestamp_1: Seconds in unix. After.
        :timestamp_2: Seconds in unix. Before.
    """

    soup = BeautifulSoup(_get_data(), 'html.parser')

    main_div = soup.find(class_='row row-flex')
    items = main_div.find_all(class_='col-flex')

    now = datetime.now()
    pars_data = []

    for item in items:
        div = item.find(class_='punk-image-text-dense')

        img_url = HOST + item.a.img.get('src', '')
        name = item.a.get('title', '')

        data = re.split(r'[ΞK\s]', div.get_text(strip=True))
        coin, price, num, label = data[:4]

        seconds = float(num) * IN_SECONDS.get(label, 86400)
        created_at = now - timedelta(seconds=seconds)
        date = created_at.strftime('%H:%M %d-%m-%Y')
        name = ' '.join(name.split()[:2])

        unix_time = time.mktime(created_at.timetuple())

        if timestamp_1 < unix_time < timestamp_2:
            pars_data.append([img_url, name, coin, price, date])

    pars_data.reverse()
    return pars_data

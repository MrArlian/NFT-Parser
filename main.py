import urllib.request
import time
import io

from tweepy import API, OAuthHandler
from configobj import ConfigObj

from parser_nft import parser


cfg = ConfigObj('static/config.cfg')

API_KEY = cfg.get('API_KEY')
API_SECRET = cfg.get('API_SECRET')

TOKEN = cfg.get('TOKEN')
TOKEN_SECRET = cfg.get('TOKEN_SECRET')

COLLECTION = cfg.get('COLLECTION')

auth = OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)

bot = API(auth)


def main():
    """
        Gets new sales data every minute.
        And also creates a new tweet based on this data.
    """

    text_pattern = '%s\n\nКуплено за %.2f %s\n%s'

    while True:
        timestamp = time.time()
        time.sleep(60)

        pars_data = parser(COLLECTION, 5, time.time(), timestamp)

        if not pars_data:
            continue

        for data in pars_data:
            file = urllib.request.urlopen(data[0]).read()

            media = bot.media_upload(None, file=io.BytesIO(file))
            bot.update_status(status=text_pattern % tuple(data[1:]),
                              media_ids=[media.media_id])


if __name__ == '__main__':
    main()

import urllib.request
import time
import io

from tweepy import API, OAuthHandler
from configobj import ConfigObj
from PIL import Image

from parser_nft import parser, HEADERS


cfg = ConfigObj('static/config.cfg')

API_KEY = cfg.get('API_KEY')
API_SECRET = cfg.get('API_SECRET')

TOKEN = cfg.get('TOKEN')
TOKEN_SECRET = cfg.get('TOKEN_SECRET')

auth = OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(TOKEN, TOKEN_SECRET)

bot = API(auth)


def main():
    """
        Receives new NFT sales data every minute.
        And also creates a new tweet based on this data.
    """

    text_pattern = '{}\nSale: {} ETC\nTime: {} UTC'

    while True:
        timestamp = time.time()
        time.sleep(60)

        pars_data = parser(timestamp, time.time())

        if not pars_data:
            continue

        for data in pars_data:
            request = urllib.request.Request(data[0], headers=HEADERS)
            file = urllib.request.urlopen(request)
            buff = io.BytesIO()

            img = Image.open(file)
            new_img = img.resize((270, 270), Image.NEAREST)
            new_img.save(buff, 'png')
            new_img.close()

            media = bot.simple_upload(None, file=buff.getvalue())
            bot.update_status(status=text_pattern.format(*data[1:]),
                              media_ids=[media.media_id])

            buff.close()


if __name__ == '__main__':
    main()

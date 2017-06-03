import logging
from operator import attrgetter

import tweepy

from .base import BaseNewsClient


LOGGER = logging.getLogger(__name__)


class TwitterNews(BaseNewsClient):

    def __init__(self, config):
        super(TwitterNews, self).__init__(config)

        auth = tweepy.OAuthHandler(config['consumer']['key'],
                                   config['consumer']['secret'])
        auth.set_access_token(config['access']['token'],
                              config['access']['token_secret'])
        self.api = tweepy.API(auth)

        try:
            self.myself = self.api.me()
        except tweepy.TweepError:
            raise self.APIError

    def _fetch(self, topic, limit):
        for text in map(attrgetter('text'), self.api.search(topic)):
            LOGGER.debug(text)
            yield text

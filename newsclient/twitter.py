import logging
import os
from operator import attrgetter

import tweepy

from .base import BaseNewsClient


logger = logging.getLogger(__name__)


class TwitterNews(BaseNewsClient):

    def __init__(self, config):
        self.settings = config

        self.auth = tweepy.OAuthHandler(config['consumer']['key'],
                                        config['consumer']['secret'])
        self.auth.set_access_token(config['access']['token'],
                                   config['access']['token_secret'])
        self.api = tweepy.API(self.auth)

        try:
            self.me = self.api.me()
        except tweepy.TweepError:
            raise self.APIError

    def _fetch(self, topic, limit):
        for text in map(attrgetter('text'), self.api.search(topic)):
            logger.debug(text)
            yield text

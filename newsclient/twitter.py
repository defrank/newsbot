import logging
import os

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

    def fetch(self, topic='general news'):
        articles = [self.NewsArticle(r.text) for r in self.api.search(topic)]
        for art in articles:
            logger.debug(art)
        return articles[:1]

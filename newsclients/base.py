from abc import ABCMeta, abstractmethod
from itertools import islice


class BaseNewsClient(object, metaclass=ABCMeta):
    class APIError(EnvironmentError):
        pass

    class NewsArticle(str):
        """
        Use the `pprint` or `textwrap` libraries to format articles.
        Inherits from `str` so as to remain JSON serializable.
        
        """
        def __init__(self, text):
            self.text = text

        def __str__(self):
            return self.text

        def __repr__(self):
            return self.text

    def __init__(self, config=None):
        """Use the constructor to take secrets and initialize an API."""
        self.config = config

    def fetch(self, topic=None, limit=1, lang='en'):
        """
        Uses the overridden method `_fetch` to retrieve an iterable of
        text news articles.  Each text is wrapped in a NewsArticle.
        Limit is enforced.

        The overridden method, `_fetch` should return a generator, but
        any iterable is acceptable.

        Arguments:
            topic -- str of news topic
            limit -- int of max news articles
            lang -- str of ISO-639-1 formatted language

        Returns:
            list -- of str-like NewsArticle objects

        """
        if topic is None:
            topic = 'general news'
        return [
            self.NewsArticle(a)
            for a in islice(self._fetch(topic=topic, limit=limit, lang=lang),
                            limit)
        ]

    @abstractmethod
    def _fetch(self, topic, limit, lang):
        """
        Use the client's API to get news of the given topic.  General
        news will be retrieved if the topic is not given.

        The format that is returned needs to be interable.

        Arguments:
            topic -- str of news topic
            limit -- int of max article count returned
            lang -- str of ISO-639-1 formatted language

        Returns: 
            iterable -- of str, preferably a generator

        """
        raise NotImplementedError

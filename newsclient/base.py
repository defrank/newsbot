class BaseNewsClient(object):
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

    def __init__(self):
        """Use the constructor to take secrets and initialize an API."""

    def fetch(self, topic=None):
        """
        Use the client's API to get news of the given topic.  General
        news will be retrieved if the topic is not given.

        The format that is returned needs to be a list of nicely
        formatted articles.

        Arguments:
            topic -- optional, str of news topic

        Returns: 
            list -- pretty formatted str articles

        """
        raise NotImplementedError

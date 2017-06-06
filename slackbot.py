import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
from importlib import import_module
from operator import itemgetter
from pkgutil import iter_modules
from time import sleep

import yaml
from slackclient import SlackClient


LOGGER = logging.getLogger(__name__)

CLIENTS_PKG = 'newsclients'


class NewsSlackBot(object):
    """
    News Slackbot uses extensible news clients to fetch news articles
    from different sources.

    * News topic is determined by a channel's topic or purpose.

    """
    def __init__(self, secrets_yaml='secrets.yml'):
        with open(secrets_yaml, 'rb') as secrets_file:
            self.config = config = yaml.load(secrets_file)
        self.bot = bot = {
            'token': config['slackbot']['token'],
            'id': config['slackbot'].get('id'),
            'name': config['slackbot'].get('name'),
        }

        # Instantiate Slack client.
        self.slack_client = SlackClient(bot['token'])

        # Set bot id.
        if not bot['id']:
            if not bot['name']:
                raise EnvironmentError

            users_list = self.get('users.list')
            if not users_list.get('ok'):
                raise EnvironmentError
            users = [u for u in users_list.get('members') if 'name' in u]
            bot['id'] = next(u.get('id') for u in users if u['name'] == bot['name'])
        bot['at'] = '<@{id}>'.format(id=bot['id'])

        self._clients = None

        self.meta_by_channel_id = defaultdict(lambda: defaultdict(lambda: None))
        self._channels = None, None

    def get(self, name, key=None):
        result = self.slack_client.api_call(name)
        return result if key is None else result[key]

    @staticmethod
    def update_purpose(meta, purpose):
        for line in purpose.splitlines():
            try:
                key, value = (t.strip() for t in line.split(':', 1))
            except ValueError:
                continue
            key = key.lower()

            if key == 'topic':
                meta[key].append(value)
            elif key == 'frequency':
                if value.isdigit():
                    meta[key] = int(value)
            elif key == 'limit':
                if value.isdigit():
                    meta[key] = int(value)
            elif key == 'language':
                if len(value) == 2 and value.isalpha():
                    meta[key] = value

    def parse_meta(self, channel):
        meta = self.meta_by_channel_id[channel['id']]
        meta.update(
            topic=[],
            frequency=60,
            limit=2,
            language='en',
        )

        topic = channel['topic']['value']
        if topic:
            meta['topic'].append(topic)
        self.update_purpose(meta, channel['purpose']['value'])

        return channel

    @property
    def channels(self):
        last_update, channels = self._channels

        now = datetime.now()
        if last_update is None or now - last_update > timedelta(minutes=10):
            channels = [self.parse_meta(c)
                        for c in self.get('channels.list', 'channels')
                        if c['is_member']]
            self._channels = now, channels

        return channels

    def loop_forever(self):
        if self.slack_client.rtm_connect():
            LOGGER.info('StarterBot connected and running!')
            while True:
                command, channel_id = self.parse_rtm_events(self.slack_client.rtm_read())
                if command and channel_id:
                    # Respond to messages.
                    self.handle_command(command, channel_id)
                else:
                    # Try to send news updates.
                    self.send_news()

                sleep(1)
        else:
            LOGGER.critical('Connection failed. Invalid Slack token or bot ID?')

    def parse_rtm_events(self, events):
        """
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns any for any non-empty message.

        """
        at_bot = self.bot['at']
        for evt in events:
            LOGGER.debug(evt)
            channel_id, text = evt.get('channel'), evt.get('text')
            if 'purpose' in evt:
                self.update_purpose(self.meta_by_channel_id[channel_id],
                                    evt['purpose'])
            if evt.get('user') == self.bot['id'] or not text or evt['type'] != 'message':
                continue
            elif at_bot in text \
                    or channel_id not in map(itemgetter('id'), self.channels):
                # Handle command only if @mention or direct channel (IM).
                tokens = filter(None, (t.strip() for t in text.split(at_bot)))
                # return text, whitespace and @mention removed
                return ' '.join(t.lower() for t in tokens), channel_id
        return None, None

    def handle_command(self, cmd, channel):
        cmd = cmd.split()[0]
        response = 'I am unable to process commands at this time...'
        self.slack_client.api_call('chat.postMessage',
                                   channel=channel,
                                   text=response,
                                   as_user=True)

    @property
    def clients(self):
        """
        Yield all of the NewsClients existing in non-private modules of the
        given package.

        """
        if not self._clients:
            self._clients = []
            for _, name, is_pkg in iter_modules([CLIENTS_PKG]):
                if not is_pkg and not name.startswith('_'):
                    module = import_module('{pkg}.{client}'.format(
                        pkg=CLIENTS_PKG, client=name))
                    if hasattr(module, 'NewsClient'):
                        self._clients.append(module.NewsClient(self.config))
        return self._clients

    def send_news(self):
        now = datetime.now()
        for client in self.clients:
            for channel in self.channels:
                meta = self.meta_by_channel_id[channel['id']]
                last_update = meta['last_update']
                if last_update is None \
                        or last_update < now - timedelta(minutes=meta['frequency']):
                    meta['last_update'] = now
                else:
                    continue
                for article in client.fetch(topic=' OR '.join(meta['topic']),
                                            limit=meta['limit'],
                                            lang=meta['language']):
                    self.slack_client.api_call('chat.postMessage',
                                               channel=channel['id'],
                                               text=article,
                                               as_user=True)
                    sleep(1)


if __name__ == '__main__':
    logging.basicConfig(filename='bot.log', level=logging.DEBUG)
    NewsSlackBot().loop_forever()

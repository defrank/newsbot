import logging
from datetime import datetime, timedelta
from operator import itemgetter
from time import sleep

import yaml
from slackclient import SlackClient

if __name__ == '__main__':
    # Setup basic config before importing local since `disable_existing_loggers`
    # defaults to True.
    logging.basicConfig(filename='bot.log', level=logging.DEBUG)
from newsclient.twitter import TwitterNews


LOGGER = logging.getLogger(__name__)


class NewsSlackBot(object):

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

        self._channels = None, None

    def get(self, name, key=None):
        result = self.slack_client.api_call(name)
        return result if key is None else result[key]

    @property
    def channels(self):
        last_update, channels = self._channels

        now = datetime.now()
        if last_update is None or now - last_update > timedelta(minutes=10):
            last_update = now
            self._channels = last_update, channels = now, [
                c
                for c in self.get('channels.list', 'channels') if c['is_member']]

        return channels

    def loop_forever(self):
        if self.slack_client.rtm_connect():
            LOGGER.info('StarterBot connected and running!')
            interval = timedelta(minutes=60)
            last_news_update = datetime.now() - 2*interval
            while True:
                now = datetime.now()
                command, channel = self.parse_rtm_events(self.slack_client.rtm_read())
                if command and channel:
                    # Respond to messages.
                    self.handle_command(command, channel)
                elif now - last_news_update > interval:
                    # Send news updates.
                    last_news_update = now
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
            channel, text = evt.get('channel'), evt.get('text')
            if evt.get('user') == self.bot['id'] or not text or evt['type'] != 'message':
                continue
            elif at_bot in text \
                    or channel not in map(itemgetter('id'), self.channels):
                # Handle command only if @mention or direct channel (IM).
                tokens = filter(None, (t.strip() for t in text.split(at_bot)))
                # return text, whitespace and @mention removed
                return ' '.join(t.lower() for t in tokens), channel
        return None, None

    def handle_command(self, cmd, channel):
        cmd = cmd.split()[0]
        response = 'I am unable to process commands at this time...'
        self.slack_client.api_call('chat.postMessage',
                                   channel=channel,
                                   text=response,
                                   as_user=True)

    def get_newsclients(self):
        return [TwitterNews(self.config['twitter'])]

    def send_news(self):
        for client in self.get_newsclients():
            for channel in self.channels:
                for article in client.fetch(topic=channel['topic']['value']
                                            or channel['purpose']['value']):
                    self.slack_client.api_call('chat.postMessage',
                                               channel=channel['id'],
                                               text=article,
                                               as_user=True)
                    sleep(1)


if __name__ == '__main__':
    NewsSlackBot().loop_forever()

import logging
import os
import sys
import yaml
from datetime import datetime, timedelta
from time import sleep

from slackclient import SlackClient

if __name__ == '__main__':
    # Setup basic config before importing local since `disable_existing_loggers`
    # defaults to True.
    logging.basicConfig(filename='bot.log', level=logging.DEBUG)
from newsclient.twitter import TwitterNews


logger = logging.getLogger(__name__)

# Constants.
NEWS_CHANNEL = 'news'  # No prefixing '#'


class NewsSlackBot(object):

    def __init__(self, secrets_yaml='secrets.yml', loop_delay=1, news_interval=60):
        self.loop_delay = loop_delay  # In seconds.
        self.interval = timedelta(minutes=news_interval)
        self.last_news_update = datetime.now() - timedelta(minutes=2*news_interval)

        with open(secrets_yaml, 'rb') as fp:
            self.settings = yaml.load(fp)
        self.bot_token = self.settings['slackbot']['token']
        self.bot_name = self.settings['slackbot'].get('name')
        self.bot_id = self.settings['slackbot'].get('id')

        # Instantiate Slack client.
        self.slack_client = sc = SlackClient(self.bot_token)

        # Set bot id.
        if not self.bot_id:
            if not self.bot_name:
                raise EnvironmentError

            users_list = sc.api_call('users.list')
            if not users_list.get('ok'):
                raise EnvironmentError
            users = [u for u in users_list.get('members') if 'name' in u]
            self.bot_id = next(u.get('id') for u in users if u['name'] == self.bot_name)
        self.at_bot = '<@{id}>'.format(id=self.bot_id)

        # Channel IDs: used to differentiate between IMs.
        # TODO: treat this as a cache and update periodically or when receiving
        # channel events.
        self.channel_ids =  [c['id'] for c in sc.api_call('channels.list')['channels']]

    def loop_forever(self):
        if self.slack_client.rtm_connect():
            logger.info('StarterBot connected and running!')
            while True:
                now = datetime.now()

                command, channel = self.parse_rtm_events(self.slack_client.rtm_read())
                if command and channel:
                    # Respond to messages.
                    self.handle_command(command, channel)
                elif now - self.last_news_update > self.interval:
                    # Send news updates.
                    self.last_news_update = now
                    self.send_news()

                sleep(self.loop_delay)
        else:
            logger.critical('Connection failed. Invalid Slack token or bot ID?')

    def parse_rtm_events(self, events):
        """
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns any for any non-empty message.

        """
        for evt in events:
            logger.debug(evt)
            channel, text = evt.get('channel'), evt.get('text')
            if evt.get('user') == self.bot_id or not text or evt['type'] != 'message':
                continue
            elif channel not in self.channel_ids or self.at_bot in text:
                # return text, whitespace and @mention removed
                tokens = filter(None, (t.strip() for t in text.split(self.at_bot)))
                return ' '.join(t.lower() for t in tokens), channel
        return None, None

    def handle_command(self, cmd, channel):
        cmd = cmd.split()
        cmd, args = cmd[0], cmd[1:]

        response = 'I am unable to process commands at this time...'

        self.slack_client.api_call('chat.postMessage',
                                   channel=channel,
                                   text=response,
                                   as_user=True)

    def send_news(self):
        twitter_client = TwitterNews(self.settings['twitter'])
        articles = twitter_client.fetch()
        for article in articles:
            self.slack_client.api_call('chat.postMessage',
                                       channel='#{channel}'.format(
                                           channel=NEWS_CHANNEL.lstrip('#'),
                                       ),
                                       text=article,
                                       as_user=True)


if __name__ == '__main__':
    NewsSlackBot().loop_forever()

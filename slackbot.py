import logging
import os
import sys
from time import sleep

from slackclient import SlackClient

from commands.mood import get_mood
from commands.special import celebration
from commands.articles import get_num_posts
from commands.challenge import create_tweet
from commands.weather import get_weather


logger = logging.getLogger(__name__)

# Constants.
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_ID = os.environ.get('BOT_ID')
AT_BOT = '<@{id}>'.format(id=BOT_ID)
NEWS_CHANNEL = 'news'

cmd_names = ['mood', 'celebration', 'num_posts', '100day_tweet', 'weather']
cmd_functions = [get_mood, celebration, get_num_posts, create_tweet, get_weather]
COMMANDS = dict(zip(cmd_names, cmd_functions))


class NewsSlackBot(object):

    def __init__(self, read_websocket_delay=1):
        self.read_websocket_delay = read_websocket_delay

        # instantiate Slack & Twilio clients
        self.slack_client = SlackClient(BOT_TOKEN)

    def loop_forever(self):
        if self.slack_client.rtm_connect():
            logger.info('StarterBot connected and running!')
            while True:
                command, channel = self.parse_rtm_events(self.slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                sleep(self.read_websocket_delay)
        else:
            logger.critical('Connection failed. Invalid Slack token or bot ID?')

    @staticmethod
    def parse_rtm_events(events):
        """
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns any for any non-empty message.

        """
        logger.debug(events)
        for evt in events:
            text = evt.get('text')
            if evt.get('user') == BOT_ID or not text:
                continue
            elif evt['type'] == 'message':
                # return text, whitespace and @mention removed
                tokens = filter(None, (t.strip() for t in text.split(AT_BOT)))
                return ' '.join(t.lower() for t in tokens), evt['channel']
        return None, None

    def handle_command(self, cmd, channel):
        cmd = cmd.split()
        cmd, args = cmd[0], cmd[1:]

        if cmd in COMMANDS:
            response = COMMANDS[cmd](*args)
        else:
            response = ('Not sure what you mean? '
                        'I can help you with these commands:\n'
                        '{}'.format('\n'.join(cmd_names)))

        self.slack_client.api_call('chat.postMessage',
                                   channel=channel,
                                   text=response,
                                   as_user=True)


if __name__ == '__main__':
    logging.basicConfig(filename='bot.log', level=logging.DEBUG)
    slackbot = NewsSlackBot()
    slackbot.loop_forever()

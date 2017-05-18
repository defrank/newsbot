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

# constants
AT_BOT = "<@" + os.environ.get("BOT_ID") + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('BOT_TOKEN'))

cmd_names = ('mood', 'celebration', 'num_posts', '100day_tweet', 'weather')
cmd_functions = (get_mood, celebration, get_num_posts, create_tweet, get_weather)
COMMANDS = dict(zip(cmd_names, cmd_functions))


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def handle_command(cmd, channel):
    
    cmd = cmd.split()
    cmd, args = cmd[0], cmd[1:]

    if cmd in COMMANDS:
        response = COMMANDS[cmd](*args)
    else:
        response = ('Not sure what you mean? '
		    'I can help you with these commands:\n'
		    '{}'.format('\n'.join(cmd_names)))

    slack_client.api_call('chat.postMessage', channel=channel,
                          text=response, as_user=True)


if __name__ == '__main__':
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        logger.info('StarterBot connected and running!')
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            sleep(READ_WEBSOCKET_DELAY)
    else:
        logger.critical('Connection failed. Invalid Slack token or bot ID?')

#coding=utf8
import os
import time
from slackclient import SlackClient
import re
import random
import datetime
import json


cheers = [
    'Կէնաձդ', 'Gesondheid', 'Gëzuar', 'فى صحتك:', 'Nuş olsun', 'Živjeli', 'Наздраве', '	Aung myin par say', 'Salut'
    'Biba', '干杯', 'Nazdravlje', 'Na zdravi', 'Skål', 'Proost', 'Terviseks', 'Mabuhay', 'Kippis', 'Santé', 'Salud',
    'Prost', 'ΥΓΕΙΑ', '	Å’kålè ma’luna', 'לחיים', 'Egészségedre', 'Skál', 'Sláinte', 'Cin cin', '乾杯', '건배', 'Priekā',
    'į sveikatą', 'На здравје', 'Эрүүл мэндийн төлөө', 'Skål', 'Na zdrowie', 'Saúde', 'Noroc', 'На здоровье',
    'živeli', 'Na zdravie', 'Salud', 'Skål', 'Chok dee', 'Şerefe', 'будьмо', 'Một hai ba, yo', 'Iechyd da', 'Sei gesund'
]

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

last_weekly_update = None

beertabs = {}

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    user_id = command['user']

    if user_id == BOT_ID:
        return
    beertabs[user_id] = {'balance': 0} if user_id not in beertabs else beertabs[user_id]
    if not beertabs[user_id].get('name'):
        username = slack_client.api_call("users.info", user=user_id).get('user', {}).get('name')
        beertabs[user_id]['name'] = username


    if command['text'].lower().strip() == 'cleared':
        beertabs[user_id]['balance'] = 0
        response = "Cleared! {}'s beer balance is 0 :beers:".format(username)
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    elif re.search(r"^\+(\d+)$", command['text']):
        match = re.search(r"^\+(\d+)$", command['text'])
        amount = int(match.group(1))
        beertabs[user_id]['balance'] = beertabs[user_id]['balance'] + amount
        sign = '+' if amount > 0 else ''
        response = "{}, {}! Your beer balance is {}{} :beers:".format(random.choice(cheers), username, sign, beertabs[user_id]['balance'])
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    elif re.search(r"^\-(\d+)$", command['text']):
        match = re.search(r"^\-(\d+)$", command['text'])
        amount = int(match.group(1))
        beertabs[user_id]['balance'] = beertabs[user_id]['balance'] - amount
        sign = '+' if amount > 0 else ''
        response = "Thank you, {}! Your beer balance is {}{} :beers:".format(username, sign, beertabs[user_id]['balance'])
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    elif command['text'].lower() == 'my balance':
        response = "{}'s current beer balance is {} :beers:".format(username, beertabs[user_id]['balance'])
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    elif command['text'].lower() == 'all balances':
        response = ""
        for item in beertabs.values():
            sign = '-' if item['balance'] < 0 else '+'
            response += "{}: {}{} :beers:\n".format(item['name'], sign, item['balance'])
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    elif re.match(r"(?i)set (\d+)", command['text']):
        match = re.match(r"(?i)set (\d+)", command['text'])
        print match.group()
        amount = int(re.match(r"(?i)set (\d+)", command['text']).group(1))
        beertabs[user_id]['balance'] = amount
        response = "{}'s beer balance adjusted to {} :beers:".format(username, amount)
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    print slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and 'user' in output:
                # return text after the @ mention, whitespace removed

                return output, output['channel']

    return None, None


if __name__ == "__main__":

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

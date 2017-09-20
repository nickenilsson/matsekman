#coding=utf8
import os
import time
from slackclient import SlackClient
import re
import random
import json
import traceback
import time
import socket
from websocket import WebSocketConnectionClosedException

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
#slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client = SlackClient("xoxb-169125561744-3g4L5lbhrBSLSfD5P5z0iRO4")


FALLBACK_USERNAME = 'Jean Doe'
SILENT_MODE = True

beertabs = {}

def cleared(user_id, channel):
    username = beertabs[user_id].get('name', FALLBACK_USERNAME)
    beertabs[user_id]['balance'] = 0
    response = "Cleared! {}'s beer balance is 0 :beers:".format(username)
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def add_beer(user_id, amount, channel):
    username = beertabs[user_id].get('name', FALLBACK_USERNAME)
    beertabs[user_id]['balance'] = beertabs[user_id]['balance'] - amount
    sign = '+' if beertabs[user_id]['balance'] > 0 else ''
    response = "Thank you, {}! Your beer balance is *{}{}* :beers:".format(username, sign, beertabs[user_id]['balance'])
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def deduct_beer(user_id, amount, channel):
    username = beertabs[user_id].get('name', FALLBACK_USERNAME)
    beertabs[user_id]['balance'] = beertabs[user_id]['balance'] + amount
    sign = '+' if beertabs[user_id]['balance'] > 0 else ''
    response = "{}, {}! Your beer balance is *{}{}* :beers:".format(random.choice(cheers), username, sign,
                                                                    beertabs[user_id]['balance'])
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def set_balance(user_id, amount, channel):
    username = beertabs[user_id].get('name', FALLBACK_USERNAME)
    beertabs[user_id]['balance'] = amount
    sign = '+' if beertabs[user_id]['balance'] > 0 else ''
    response = "*{}*'s beer balance adjusted to *{}{}* :beers:".format(username, sign, amount)
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def show_help(channel):
    response = "Hello beer lovers! This is how you will speak to me:\n" \
               "Take/drink x amount of beers, say *-x*\n" \
               "Refill fridge with x amount of beers, say *+x*\n" \
               "To check your balance, just say: *my balance*\n" \
               "To see everyone's balance, you say *all balances*\n" \
               "To zero out your balance, please say *cleared*\n" \
               "If you need to adjust your balance to x amount you can do that by saying *set x*\n" \
               "I am case insensitive. "
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def show_my_balance(user_id, channel):
    username = beertabs[user_id].get('name', FALLBACK_USERNAME)
    sign = '+' if beertabs[user_id]['balance'] > 0 else ''
    response = "{}'s current beer balance is *{}{}* :beers:".format(username, sign, beertabs[user_id]['balance'])
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def show_all_balances(channel):
    response = ""
    for user_id, item in beertabs.items():
        if user_id == BOT_ID:
            continue
        sign = '+' if item['balance'] > 0 else ''
        response += "*{}*: *{}{}* :beers:\n".format(item.get('name', FALLBACK_USERNAME), sign, item['balance'])
    if not SILENT_MODE:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)



def handle_command(command, channel):

    user_id = command['user']
    if user_id == BOT_ID:
        return

    beertabs[user_id] = {'balance': 0} if user_id not in beertabs else beertabs[user_id]
    if not beertabs[user_id].get('name'):
        username = slack_client.api_call("users.info", user=user_id).get('user', {}).get('name')
        beertabs[user_id]['name'] = username

    elif command['text'].lower().strip() == 'cleared':
        cleared(user_id=user_id, channel=channel)
        return

    elif command['text'].lower().strip() == 'help':
        show_help(channel=channel)
        return

    elif re.search(r"^\+(\d+)$", command['text']):
        match = re.search(r"^\+(\d+)$", command['text'])
        deduct_beer(user_id=user_id, amount=int(match.group(1)), channel=channel)
        return

    elif re.search(r"^-(\d+)$", command['text']):
        match = re.search(r"^-(\d+)$", command['text'])
        add_beer(user_id=user_id, amount=int(match.group(1)), channel=channel)
        return

    elif command['text'].lower() == 'my balance':
        show_my_balance(user_id=user_id, channel=channel)
        return

    elif command['text'].lower() == 'all balances':
        show_all_balances(channel=channel)
        return

    elif re.match(r"(?i)^set (\+|-)?(\d+)$", command['text']):
        match = re.match(r"(?i)^set (\+|-)?(\d+)$", command['text'])
        amount = int(match.group(2))
        amount = -amount if match.group(1) == '-' else amount
        amount = 0 if match.group(2) == 0 else amount
        set_balance(user_id=user_id, amount=amount, channel=channel)
        return


def parse_slack_output(slack_rtm_output):

    output_list = slack_rtm_output
    #print slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and 'user' in output:
                return output, output['channel']

    return None, None


def get_member_channels():
    cursor = None
    channel_ids = []
    while True:
        response = slack_client.api_call(
            "channels.list",
            cursor=cursor
        )
        for c in response["channels"]:
            if c["is_member"] == False:
                continue
            else:
                channel_ids.append(c["id"])
        if response["response_metadata"].get("next_cursor"):
            cursor = response["response_metadata"].get("next_cursor")
        else:
            break
    return channel_ids

def find_channel_id(name):
    cursor=None
    while True:
        params = {"method": "channels.list"}
        if cursor:
            params["cursor"] = cursor
        response = slack_client.api_call(**params)

        for c in response["channels"]:
            if c["name"].lower() == name.lower():
                return c["id"]
        if response.get("response_metadata", {}).get("next_cursor"):
            cursor = response["response_metadata"]["next_cursor"]
        else:
            break


def get_balance_from_channel(channel_id):
    last_message_id = None
    all_messages = []
    while True:
        params = {"method": "channels.history", "channel": channel_id}
        if last_message_id:
            params["latest"] = last_message_id
        response = slack_client.api_call(**params)

        for message in response["messages"]:
            all_messages.append(message)
        if not response["has_more"]:
            break

        last_message_id = response["messages"][-1]["ts"]

    print len(all_messages)
    for i in range(len(all_messages)-1, 0, -1):
        handle_command(all_messages[i], channel_id)

def initilize_beer_balance():
    beer_channel_id = find_channel_id("beer_balance")
    get_balance_from_channel(beer_channel_id)


if __name__ == "__main__":

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        print "initializing beer balances..."
        initilize_beer_balance()
        print "Beer balances are initialized!"
        SILENT_MODE = False

        while True:
            try:
                command, channel = parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    handle_command(command, channel)
            except (socket.error, WebSocketConnectionClosedException), e:
                print e.message
                time.sleep(5)
                slack_client.rtm_connect()
                continue
            except:
                print traceback.print_exc()
                print "Something else went wrong"
                continue

            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

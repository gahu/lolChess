# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter

SLACK_TOKEN = 'xoxb-691564988023-689723470832-YOEDQIS4JgeZtIsg8M078iUU'
SLACK_SIGNING_SECRET = 'db405cc062a74c7091224c77a51ad149'

app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

# 명령어 목록을 보여주는 함수
def _crawl_command(text):

    return text

# 가이드 함수
def _crawl_guide(text):

    return text

# 챔피언 함수
def _crawl_champion(text):

    url = "https://lolchess.gg/champions/" + text + "?hl=ko-KR"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    message = []

    for i in soup.find_all("div", class_="guide-champion-detail"):
        print(i)

    return text

# 시너지 함수
def _crawl_synergies(text):

    return text

# 예외처리
def _crawl_else():

    return "없는 명령어 입니다. 확인하고 다시 시도해주세요"

# 챗봇이 멘션을 받았을 경우
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]

    if text[13:] == 'command':
        message = _crawl_command(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            text="명령어 목록"
        )
    elif text[13:] == "guide":
        message = _crawl_guide(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            # text=message
            text="게임 가이드 입니다."
        )
    elif text[13:] == "champion":
        message = _crawl_champion(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            # text=message
            text="챔피언 정보 입니다.\n" + message
        )
    elif text[13:] == "synergies":
        message = _crawl_synergies(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            # text=message
            text="시너지 정보 입니다."
        )
    else:
        message = _crawl_else
        slack_web_client.chat_postMessage(
            channel=channel,
            text=message
        )


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)

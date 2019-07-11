# -*- coding: utf-8 -*-
import re
import urllib.request

from bs4 import BeautifulSoup

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent

SLACK_TOKEN = 'xoxb-691564988023-689257415652-53Ime9PhhdIZ4yS6FzVBfUBs'
SLACK_SIGNING_SECRET = 'cdd6271c90db7f3e70bfe46c39459dcc'

app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)

# 명령어 목록을 보여주는 함수
def _crawl_command(text):

    return text

# 가이드 함수
def _crawl_guide(text):
    menu = text[19:]

    if menu == '1' : # gold
        menu_url = 'guide/exp'
        title_block = SectionBlock(
            text="*ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ 골드 수익 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ*"
        )
    elif menu == '2': # exp
        menu_url = 'guide/exp'
        title_block = SectionBlock(
            text="*ㅡㅡㅡㅡㅡㅡㅡ 레벨별 필요 경험치 ㅡㅡㅡㅡㅡㅡㅡ*"
        )
    elif menu == '3': # 단축키
        menu_url = 'guide/hotkeys'
        title_block = SectionBlock(
            text="*ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ 단축키 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ*"
        )
    elif menu == '4': # 리롤
        menu_url = 'guide/reroll'
        title_block = SectionBlock(
            text="*ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ 리롤 확률 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ*"
        )
    elif menu == '5': # 아이템 정보
        menu_url = 'items'
        title_block = SectionBlock(
            text="*ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ 아이템 정보 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ*"
        )
    else: # guide 뒤에 잘못된 글자를 썼을 때
        block1 = SectionBlock(
            fields=["*Guide에는 다음과 같은 메뉴가 있습니다.*", '\n', "1.  골드", "2.  경험치", "3.  단축키", "4.  리롤 확률", "5.  아이템 정보", '\n',
                    "`@lolchess guide 1`과 같은 방법으로 입력해주세요"]
        )
        return [block1]

    url = "https://lolchess.gg/champions/garen"
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    # 표에 있는 데이터들 가져오기
    columns = soup.select('table > tbody > tr')
    df = []
    alltd = []
    allth = []
    for column in columns:
        ths = column.find_all("th")
        tds = column.find_all("td")
        for td in tds:
            df.append(td.text)
        for th in ths:
            allth.append(th.text)
        alltd.append(df)
        df = []
    print(allth)
    # 글씨 굵게
    bold = []
    for i in allth:
        i = "*" + i + "*"
        bold.append(i)
    # block 만들기
    block = []
    if menu == '1':
        for i in range(0, 5):
            td = alltd[i]
            temp = SectionBlock(
                fields=[bold[i], "\n", td[0], td[1]]
            )
            block.append([temp])
        img = ImageBlock(
            image_url= "https://raw.githubusercontent.com/gahu/lolChess/master/gold.png",
            alt_text = "응 안나와"
        )
        # 바깥의 list 제거
        message = [title_block] + [item for sublist in block for item in sublist] + [img]
    elif menu == '2':
        for i in range(19, 26):
            td = alltd[i]
            temp = SectionBlock(
                fields=[bold[i], td[0]]
            )
            block.append([temp])
        # 바깥의 list 제거
        message = [title_block] + [item for sublist in block for item in sublist]
    elif menu == '3': # 단축키
        img = ImageBlock(
            image_url="https://raw.githubusercontent.com/gahu/lolChess/master/hotkey.png",
            alt_text="응 안나와"
        )
        message = [title_block]+[img]
    elif menu == '4': #리롤
        img = ImageBlock(
            image_url="https://raw.githubusercontent.com/gahu/lolChess/master/reroll.png",
            alt_text="응 안나와"
        )
        message = [title_block] + [img]
    else: # 아이템
        img = ImageBlock(
            image_url="https://raw.githubusercontent.com/gahu/lolChess/master/item.png",
            alt_text="응 안나와"
        )
        message = [title_block] + [img]

    print(message)
    return message
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
    title_block = SectionBlock(
        text = "*LoLChess의 기능과 단축키는 다음과 같습니다*\n"
    )
    s_block = SectionBlock(
        fields = ["*1. 챔피언 정보*","@lolchess c 챔피언 이름","*2. 시너지 정보*", "@lolchess 귀족 or 챔피언 이름","*3. 가이드*", "@lolchess g"]
    )
    message = [title_block] + [s_block]
    return message

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
    elif text[13:14] == "g":
        message = _crawl_guide(text)
        print(message)
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks= extract_json(message)
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
        message = _crawl_else()
        print(message)
        slack_web_client.chat_postMessage(
            channel = channel,
            blocks = extract_json(message)
        )


# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)

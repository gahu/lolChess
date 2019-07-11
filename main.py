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

SLACK_TOKEN = 'xoxb-691564988023-689257415652-HwOaw33U2pdY5MSWTRG77TBb'
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
    menu = text[15]
    print(menu)
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

    url = "https://lolchess.gg/" + menu_url + "?hl=ko-KR"
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
    command = text.split(" ")
    """
    text에 담겨 들어오는 데이터
    ['<@UL9M9DUQG>', 'champion', '루시안']
    """
    # 예외처리
    if len(command[1]) > 8:
        return "champion 명령어와 챔피언 이름 사이를 띄워주세요."

    filename = "champions.txt"
    champion = ""
    # 한글 챔피언 이름 받아서 영어로 치환
    with open(filename, 'rt', encoding='UTF8') as file:
        for line in file:
            chamKo, chamEn = line.split(',')
            if command[2] == chamKo:
                champion = chamEn.replace("\n", "")
                break
            elif command[2] == chamEn:
                champion = chamEn.replace("\n", "")
                break
            else:
                continue

    if champion == "":
        return "챔피언 이름을 잘 못 입력하셨습니다.\n 확인하시고 다시 시도해주세요."

    # lucian
    url = "https://lolchess.gg/champions/" + champion + "?hl=ko-KR"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # 챔피언 이미지
    championImageBlock = ImageBlock(
        image_url="//static.lolchess.gg/images/lol/champion-splash-modified/"+champion[0].upper()+champion[1:]+".jpg",
        alt_text="캐릭터 이미지를 띄워주는 블럭"
    )

    synergies = []
    skills = []
    synergies_champ = []
    synergies_ch2 = []

    for champ in soup.find_all("div", class_="guide-champion-detail"):
        # 챔피언 이름
        name = champ.find("span", class_="guide-champion-detail__name").get_text()
        nameText = "*영웅 이름* : "+name

        detail = champ.find("div", class_="guide-champion-detail__stats-small px-3 py-2 d-md-none")
        # 챔피언 비용
        cost = detail.find("div", class_="col-4").find("div", class_="").get_text().strip()
        costText = "*비용* : "+cost+"\n"

        # 챔피언 시너지(종족, 직업)
        for dep in detail.find_all("span", class_="align-middle"):
            synergies.append(dep.get_text())
        job = "*종족, 직업* : || "
        for dep in synergies:
            job += dep+" || "

        # 종족, 직업 이미지 넣기(미완성)
        # jjongjok = ""
        # with open("synergies.txt", 'rt', encoding='UTF8') as sy:
        #     for line in sy:
        #         for jj in synergies:
        #             if line in jj:
        #                 jjongjok += line

        # jongjokBlock = ImageBlock(
        #     image_url="//static.lolchess.gg/images/tft/traiticons-white/trait_icon_"+jjongjok+".png",
        #     alt_text="jongjok"
        # )

        # 스킬
        skillText = "*스킬* : "
        skill = champ.find("div", class_="guide-champion-detail__skill")
        skillname = skill.find("strong", class_="d-block font-size-14").get_text()
        skills.append(skillname)
        skillclass = ""
        for k in skill.find("div", class_="text-gray").find_all("span"):
            skillclass += k.get_text().strip() + " "
        skills.append(skillclass)
        skilldetail = skill.find("span", class_="d-block mt-1").get_text()
        skills.append(skilldetail)
        for dep in skills:
            skillText += dep+"\n"

        # 시너지 챔피언
        synText = "*시너지* : \n"
        synergies_detail = champ.find("div", class_="guide-champion-detail__synergies__content")
        cnt = 0
        # tft-hexagon tft-hexagon--knight
        # 시너지 영웅들 및 이미지(미구현)
        # for c, de in enumerate(synergies_detail.find_all("span", class_="name")):
        #     if c < 6:
        #         # print("위", de.get_text())
        #         synergies_ch2.append(de.get_text())
        #     else:
        #         # print("아래", de.get_text())
        #         synergies_ch2.append(de.get_text())

        for de in synergies_detail.find_all("div", class_="text-gray"):
            synergies_champ.append(synergies[cnt])
            synergies_champ.append(de.find("strong").get_text().strip())
            for de2 in de.find_all("div", class_="guide-champion-detail__synergy__stat mt-2"):
                synergies_champ.append(de2.get_text().strip())
            cnt += 1
        for dep in synergies_champ:
            synText += dep+"\n"

        # 추천아이템
        items = "*추천 아이템* : \n|| "
        src = []
        for dep in champ.find_all("div", class_="d-inline-block mr-2"):
            items += dep.find("img")["alt"] + " || "
        for dep in champ.find_all("div", class_="guide-champion-detail__recommend-items mt-2"):
            for depth in dep.find_all("img"):
                src.append(depth["src"])

        # 추천아이템 이미지(미완성)
        # item1 = ""
        # item2 = ""
        # item3 = ""
        # item4 = ""
        # for ct, kp in enumerate(src):
        #     if ct == 0:
        #         item1 += kp
        #     elif ct == 1:
        #         item2 += kp
        #     elif ct == 2:
        #         item3 += kp
        #     elif ct == 3:
        #         item4 += kp
        #     else:
        #         pass

        # first_item_image = ImageBlock(
        #     image_url=item1,
        #     alt_text="item1"
        # )
        # second_item_image = ImageBlock(
        #     image_url=item1,
        #     alt_text="item1"
        # )
        # third_item_image = ImageBlock(
        #     image_url=item1,
        #     alt_text="item1"
        # )
        # fourth_item_image = ImageBlock(
        #     image_url=item1,
        #     alt_text="item1"
        # )
        # itemImageBlock = SectionBlock(
        #     accessory=first_item_image,
        #     accessory=second_item_image,
        #     accessory=third_item_image,
        #     accessory=fourth_item_image,
        # )

        textBlock = SectionBlock(
            fields=[nameText, costText, job, skillText, synText, items]
        )

    return [championImageBlock, textBlock]

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
    elif text[13:14] == "c":
        messageBlock = _crawl_champion(text)
        slack_web_client.chat_postMessage(
            channel=channel,
            blocks=extract_json(messageBlock)
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

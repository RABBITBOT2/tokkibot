from captcha.image import ImageCaptcha
import random
import openpyxl
import os
import time
import bs4  
from discord.ext import commands
import urllib
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import re # Regex for youtube link
import unicodedata
import json
import logging
from alliteration import *
import youtube_dl
import warnings
from selenium import webdriver
import discord, asyncio, requests, datetime

def GetMelonChart():
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://www.melon.com/chart/'
    html = requests.get(url, headers=headers).text.replace('\t','').split('\n')
    chart = []
    for i in range(0,len(html)):
        if html[i].startswith('<a href="javascript:melon.link.goSongDetail'):
            chart.append(html[i][65:html[i].find("곡")])
    return chart

#사용하는 변수들
idA, moneyA, timeA, give, ID, TIME =  [], [], [], 0, 0, 0
ment = ["`룰렛 돌리는 중.`", "`룰렛 돌리는 중..`", "`룰렛 돌리는 중...`"]

try: #만약 파일이 없으면 새로 만듦
    f = open("UserData.txt", "r")
except:
    f = open("UserData.txt", "w")
    f.close()
    f = open("UserData.txt", "r")
while True: #유저들 데이터를 읽음 데이터 형식 : 유저ID,가지고 있는 돈,돈받은 시간
    line = f.readline()
    if not line: break
    line = line.split(",")
    idA.append(line[0])
    moneyA.append(int(line[1]))
    timeA.append(int(line[2]))
f.close()

client_id = "SvHKPVR9KaEEJeg31YbQ"
#Naver Open API application token
client_secret = "lGSLZgRYD0"

client = discord.Client()

with open('kkutu.txt', 'rt', encoding='utf-8') as f:
    s = f.read()

with open('user_info.json', 'r', encoding='utf-8') as file:
    user_info = json.load(file)
    user_card = user_info

with open('user_info.json', 'w', encoding='utf-8') as file:
    file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

pat = re.compile('^[ㄱ-ㅎ가-힣]+$')
wordDict = dict()
hanbangSet = set()

for i in sorted([i for i in s.split() if pat.match(i) and len(i) >= 2], key=lambda x: -len(x)):
    if i[0] not in wordDict:
        wordDict[i[0]] = set()
    wordDict[i[0]].add(i)

delList = list()
for i in wordDict:
    for j in wordDict[i]:
        if j[-1] not in wordDict:
            delList.append(j)
for j in delList:
    hanbangSet.add(j)
    wordDict[j[0]].remove(j)


tierScore = {
    'default' : 0,
    'iron' : 1,
    'bronze' : 2,
    'silver' : 3,
    'gold' : 4,
    'platinum' : 5,
    'diamond' : 6,
    'master' : 7,
    'grandmaster' : 8,
    'challenger' : 9
}
def tierCompare(solorank,flexrank):
    if tierScore[solorank] > tierScore[flexrank]:
        return 0
    elif tierScore[solorank] < tierScore[flexrank]:
        return 1
    else:
        return 2
warnings.filterwarnings(action='ignore')

opggsummonersearch = 'https://www.op.gg/summoner/userName='

'''
Simple Introduction about asyncio
asyncio : Asynchronous I/O. It is a module for asynchronous programming and allows CPU operations to be handled in parallel with I/O.
async def (func name)(parameters): -> This type of asynchronous function or method is called Native Co-Rutine.
- await : you can use await keyword only in Native Co-Rutine
async def add(a,b):
    print("add {0} + {1}".format(a,b))
    await asyncio.sleep(1.0)
    return a + b
async def print_add(a,b):
    result = await add(a,b)
    print("print_add : {0} + {1} = {2}".format(a,b,result))
loop = asyncio.get_event_loop()
loop.run_until_complete(print_add(1,2))
loop.close()
'''

def deleteTags(htmls):
    for a in range(len(htmls)):
        htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
    return htmls


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Streaming(name=".도움 / .ㅗ / .h", url='https://www.twitch.tv/rnrygus0613'))
    print(' ________________________________________________________________________________')
    print('ㅣ{0.user}이 온라인이 되었습니다!                                            ㅣ'.format(client))
    print('ㅣBOT MADE BY RABBIT#2020                                                       ㅣ')
    print('ㅣRABBIT CLIENT ID : 477076429058605056                                         ㅣ')
    print('ㅣTOKKI BOT CLIENT ID : 760776430845558794                                      ㅣ')
    print('ㅣTOKKI BOT TOKEN : NzYwNzc2NDMwODQ1NTU4Nzk0.X3Q-Qw.-EXInfI0PMpYX0SjNnv_KN5jvrg ㅣ')
    print('ㅣ______________________________________________________________________________ㅣ')

each_server = {
    "606362634131865602": {
        "alreadySet": set(),
        "round": 0,
        "win": 0,
        "lose": 0,
        "who": "토끼봇",
        "lastWord": "",
        "firstLetter": "",
        "firstTurn": True,
        "resetRound": False,
        "isPlaying": False,
        "error": False
    }
}

def patch_data(dict, null_name, null_data):
    if not (null_name in dict):
        dict[null_name] = null_data

def get_level_xp(n):
        return 5*(n**2)+50*n+100

def get_level_from_xp(xp):
        remaining_xp = int(xp)
        level = 0
        while remaining_xp >= Levels._get_level_xp(level):
            remaining_xp -= Levels._get_level_xp(level)
            level += 1
        return level

@client.event
async def on_message(message):


    channel = message.channel
    server_id = message.guild.id

    if not (str(server_id) in each_server):
        each_server[str(server_id)] = {
            "alreadySet": set(),
            "round": 0,
            "win": 0,
            "lose": 0,
            "who": "토끼봇",
            "lastWord": "",
            "firstLetter": "",
            "firstTurn": True,
            "resetRound": False,
            "isPlaying": False,
            "error": False
        }

    this_server = each_server[str(server_id)]



    if message.author.bot:
        return None


    if message.content in ['.끝말', '.끝말잇기', '.끝말잇기정보']:
        if '.끝' == message.content or '.끝말잇기' == message.content:
            embed = discord.Embed(title="끝말잇기 게임", colour = 0xDC00FF)
            embed.add_field(name="시작", value="`.s` or `.ㄴ` or `.시작`", inline=True)
            embed.add_field(name="기권", value="`.e` or `.ㄷ` or `.기권`", inline=True)
            embed.add_field(name="끝말잇기 정보 보기", value="`.끝말잇기정보` or `.ku` or `ㅏㅕ`", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send("", embed=embed)
        if message.content == ".끝말잇기정보" or message.content.startswith('.ku') or message.content.startswith('.ㅏㅕ'):
            if not (str(message.author.id) in user_card):
                user_card[str(message.author.id)] = {
                    "user": message.author.name,
                    "level": 1,
                    "word": 0,
                    "win": 0,
                    "length": 0
                }
            with open('user_info.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
            embed = discord.Embed(title=message.author.name, description=str(message.author.name), colour = 0xDC00FF)
            embed.add_field(name="레벨", value=str(user_card[str(message.author.id)]["level"]), inline=True)
            embed.add_field(name="승리", value=str(user_card[str(message.author.id)]["win"]), inline=True)
            embed.add_field(name="단어", value=str(user_card[str(message.author.id)]["word"]), inline=True)
            embed.add_field(name="글자", value=str(user_card[str(message.author.id)]["length"]), inline=True)
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send("", embed=embed)
    else:
        if message.channel.name == "끝말잇기":

            if not (str(message.author.id) in user_card):
                user_card[str(message.author.id)] = {
                    "user": message.author.name,
                    "level": 1,
                    "word": 0,
                    "win": 0,
                    "length": 0
                }

            with open('user_info.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(user_card, ensure_ascii=False, indent=4))

            if ('.s' == message.content or '.시작' == message.content or '.ㄴ' == message.content) and (not this_server["isPlaying"]):
                this_server["round"] += 1

                embed = discord.Embed(title='끝말잇기를 시작합니다.',
                                      description="기권하시려면 `.e`  또는 `.기권` 또는 `.ㄷ`를 입력해주시기 바랍니다.", colour = 0xDC00FF)
                embed.timestamp = datetime.datetime.utcnow()
                await channel.send("", embed=embed)

                this_server["lastWord"] = ''
                this_server["alreadySet"] = set()
                this_server["firstTurn"], this_server["resetRound"], this_server["isPlaying"] = True, False, True
                this_server["who"] = '토끼봇'

            if this_server["isPlaying"] and this_server["who"] == '토끼봇':
                if this_server["firstTurn"]:
                    this_server["lastWord"] = random.choice(list(wordDict[random.choice(list(wordDict.keys()))]))
                    this_server["alreadySet"].add(this_server["lastWord"])
                    await channel.send('`토끼봇 :` ' + this_server["lastWord"])
                    this_server["who"] = 'USER'
                    this_server["firstTurn"] = False
                    return None

            if this_server["isPlaying"] and this_server["who"] == 'USER' and not message.author.bot and not this_server["firstTurn"]:
                yourWord = message.content
                if yourWord == '.e' or yourWord == '.기권' or yourWord == '.ㄷ':
                    await channel.send('`[결과] 당신은 기권했습니다. 토끼봇의 승리입니다!`')
                    this_server["resetRound"] = True
                    this_server["isPlaying"] = False
                    this_server["lose"] += 1
                    this_server["who"] = '토끼봇'
                    this_server["error"] = False
                    return None

                this_server["firstLetter"] = yourWord[0]
                this_server["error"] = False
                try:
                    if (this_server["firstLetter"] != this_server["lastWord"][-1]) and not checkDueum(
                            this_server["lastWord"][-1], this_server["firstLetter"]):
                        await channel.send("`[오류] '" + this_server["lastWord"][-1] + "' (으)로 시작하는 단어를 입력하세요.`")
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord in hanbangSet:
                        await channel.send('`[오류] 한방단어는 사용할 수 없습니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord in this_server["alreadySet"]:
                        await channel.send('`[오류] 이미 나온 단어입니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord not in wordDict.get(this_server["firstLetter"], set()):
                        await channel.send('`[오류] 사전에 없는 단어입니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                except IndexError:
                    if (this_server["firstLetter"] != this_server["lastWord"][-1]):
                        await channel.send("`[오류] '" + this_server["lastWord"][-1] + "' (으)로 시작하는 단어를 입력하세요.`")
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord in hanbangSet:
                        await channel.send('`[오류] 한방단어는 사용할 수 없습니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord in this_server["alreadySet"]:
                        await channel.send('`[오류] 이미 나온 단어입니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True
                    elif yourWord not in wordDict.get(this_server["firstLetter"], set()):
                        await channel.send('`[오류] 사전에 없는 단어입니다.`')
                        this_server["who"] = 'USER'
                        this_server["error"] = True

                if not this_server["error"]:
                    this_server["who"] = '토끼봇'
                    this_server["alreadySet"].add(yourWord)
                    this_server["lastWord"] = yourWord
                    user_card[str(message.author.id)]["word"] += 1
                    user_card[str(message.author.id)]["length"] += len(yourWord)
                    with open('user_info.json', 'w', encoding='utf-8') as file:
                        file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    this_server["firstLetter"] = this_server["lastWord"][-1]
                    if not list(filter(lambda x: x not in this_server["alreadySet"], wordDict.get(this_server["firstLetter"], set()))):
                        # 라운드 종료
                        await channel.send('`[결과] 토끼봇가 기권했습니다. 당신의 승리입니다!`')
                        this_server["who"] = '토끼봇'
                        this_server["isPlaying"] = False
                        this_server["win"] += 1
                        this_server["error"] = False
                        user_card[str(message.author.id)]["win"] += 1
                        with open('user_info.json', 'w', encoding='utf-8') as file:
                            file.write(json.dumps(user_card, ensure_ascii=False, indent=4))
                    else:
                        nextWords = sorted(filter(lambda x: x not in this_server["alreadySet"], wordDict[this_server["firstLetter"]]),
                                           key=lambda x: -len(x))[
                                    :random.randint(20, 50)]
                        this_server["lastWord"] = nextWords[random.randint(0, random.randrange(0, len(nextWords)))]
                        this_server["alreadySet"].add(this_server["lastWord"])
                        await channel.send('`토끼봇 :` ' + this_server["lastWord"])
                        this_server["who"] = 'USER'

            if this_server["resetRound"] and not this_server["firstTurn"]:
                this_server["firstTurn"], this_server["resetRound"] = True, False
                this_server["who"] = '토끼봇'

    if message.content.startswith(".날씨") or message.content.startswith('.w') or message.content.startswith('.ㅈ'):
        learn = message.content.split(" ")
        location = learn[1]
        enc_location = urllib.parse.quote(location+'날씨')
        hdr = {'User-Agent': 'Mozilla/5.0'}
        url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=' + enc_location
        print(url)
        req = Request(url, headers=hdr)
        html = urllib.request.urlopen(req)
        bsObj = bs4.BeautifulSoup(html, "html.parser")
        todayBase = bsObj.find('div', {'class': 'main_info'})

        todayTemp1 = todayBase.find('span', {'class': 'todaytemp'})
        todayTemp = todayTemp1.text.strip()  # 온도
        print(todayTemp)

        todayValueBase = todayBase.find('ul', {'class': 'info_list'})
        todayValue2 = todayValueBase.find('p', {'class': 'cast_txt'})
        todayValue = todayValue2.text.strip()  # 밝음,어제보다 ?도 높거나 낮음을 나타내줌
        print(todayValue)

        todayFeelingTemp1 = todayValueBase.find('span', {'class': 'sensible'})
        todayFeelingTemp = todayFeelingTemp1.text.strip()  # 체감온도
        print(todayFeelingTemp)

        todayMiseaMongi1 = bsObj.find('div', {'class': 'sub_info'})
        todayMiseaMongi2 = todayMiseaMongi1.find('div', {'class': 'detail_box'})
        todayMiseaMongi3 = todayMiseaMongi2.find('dd')
        todayMiseaMongi = todayMiseaMongi3.text  # 미세먼지
        print(todayMiseaMongi)

        tomorrowBase = bsObj.find('div', {'class': 'table_info weekly _weeklyWeather'})
        tomorrowTemp1 = tomorrowBase.find('li', {'class': 'date_info'})
        tomorrowTemp2 = tomorrowTemp1.find('dl')
        tomorrowTemp3 = tomorrowTemp2.find('dd')
        tomorrowTemp = tomorrowTemp3.text.strip()  # 오늘 오전,오후온도
        print(tomorrowTemp)

        tomorrowAreaBase = bsObj.find('div', {'class': 'tomorrow_area'})
        tomorrowMoring1 = tomorrowAreaBase.find('div', {'class': 'main_info morning_box'})
        tomorrowMoring2 = tomorrowMoring1.find('span', {'class': 'todaytemp'})
        tomorrowMoring = tomorrowMoring2.text.strip()  # 내일 오전 온도
        print(tomorrowMoring)

        tomorrowValue1 = tomorrowMoring1.find('div', {'class': 'info_data'})
        tomorrowValue = tomorrowValue1.text.strip()  # 내일 오전 날씨상태, 미세먼지 상태
        print(tomorrowValue)

        tomorrowAreaBase = bsObj.find('div', {'class': 'tomorrow_area'})
        tomorrowAllFind = tomorrowAreaBase.find_all('div', {'class': 'main_info morning_box'})
        tomorrowAfter1 = tomorrowAllFind[1]
        tomorrowAfter2 = tomorrowAfter1.find('p', {'class': 'info_temperature'})
        tomorrowAfter3 = tomorrowAfter2.find('span', {'class': 'todaytemp'})
        tomorrowAfterTemp = tomorrowAfter3.text.strip()  # 내일 오후 온도
        print(tomorrowAfterTemp)

        tomorrowAfterValue1 = tomorrowAfter1.find('div', {'class': 'info_data'})
        tomorrowAfterValue = tomorrowAfterValue1.text.strip()

        print(tomorrowAfterValue)  # 내일 오후 날씨상태,미세먼지

        embed = discord.Embed(
            title=learn[1]+ '의 날씨 정보',
            colour=discord.Colour.gold()
        )
        embed.add_field(name='현재온도', value=todayTemp+'˚', inline=True)  # 현재온도
        embed.add_field(name='체감온도', value=todayFeelingTemp, inline=True)  # 체감온도
        embed.add_field(name='현재상태', value=todayValue, inline=True)  # 밝음,어제보다 ?도 높거나 낮음을 나타내줌
        embed.add_field(name='현재 미세먼지 상태', value=todayMiseaMongi, inline=True)  # 오늘 미세먼지
        embed.add_field(name='오늘 오전/오후 날씨', value=tomorrowTemp, inline=True)  # 오늘날씨 # color=discord.Color.blue()
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".핑") or message.content.startswith('.p') or message.content.startswith('.ㅔ'):
        latency = round(client.latency * 1000)
        embed = discord.Embed(
                title='핑(MS)',
                description = "{0}`MS`".format(latency),
                colour=discord.Colour.red()
        )
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".인증") or message.content.startswith('.i') or message.content.startswith('.ㅑ'):
        Image_captcha = ImageCaptcha()
        a = ""  
        for i in range(6):
            a += str(random.randint(0, 9))
        name = str(message.author.name) + ".png"
        Image_captcha.write(a, name)
        await message.channel.send(file=discord.File(name))
        def check(msg):
            return msg.author == message.author and msg.channel == message.channel
        try:
            msg = await client.wait_for("message", timeout=30, check=check)
        except:
            await message.channel.send("`시간초과입니다.`")
            return
        if msg.content == a:
            await message.channel.send("`정답입니다.`")
        else:
            await message.channel.send("`틀렸습니다.`")

    if message.content.startswith(".도움말") or message.content.startswith('.h') or message.content.startswith('.ㅗ'):
        embed = discord.Embed(title='도움말', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.관리자도움 / .ah / .모        `   :   **관리자 명령어를 보여줍니다.**\n`.번역도움 / .th / .소          `   :   **번역 명령어를 보여줍니다.**\n`.크롤링도움 / .ch / .초        `   :   **크롤링 명령어를 보여줍니다.**\n`.끝말잇기도움 / .kh / .ㅏㅗ    `   :   **끝말잇기 명령어를 보여줍니다.**\n`.도박도움 / .dh / .오        `   :   **도박 명령어를 보여줍니다.**\n`.기타도움 / .eh / .도           `   :   **기타 명령어를 보여줍니다.**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".관리자도움") or message.content.startswith('.ah') or message.content.startswith('.모'):
        embed = discord.Embed(title='관리자도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="없음")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".번역도움") or message.content.startswith('.th') or message.content.startswith('.소'):
        embed = discord.Embed(title='번역도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.한영번역 / .ke / .ㅏㄷ     `   :   **Korean  : > English**\n`.영한번역 / .ek / .다       `   :   **English  : > Korean**\n`.일한번역 / .jk / .ㅓㅏ     `   :   **Japanese  : > Korean**\n`.한일번역 / .kj / .ㅏㅓ     `   :   **Korean  : > Japanese**\n`.중한번역 / .ck / .차       `   :   **Chinese  : > Korean**\n`.한중번역 / .kc / .ㅏㅊ     `   :   **Korean  : > Chinese**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".크롤링도움") or message.content.startswith('.ch') or message.content.startswith('.초'):
        embed = discord.Embed(title='크롤링도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.코로나 / .co / .채         `   :   **전국 코로나를 보여줍니다.**\n`.롤전적 / .lol / .ㅣㅐㅣ    `   :   **롤의 전적을 보여줍니다.**\n`.날씨 / .w / .ㅈ            `   :   **날씨를 보여줍니다.(대한민국만 가능)**\n`.멜론차트 / .ml / .ㅢ       `   :   **멜론차트를 보여줍니다.**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".끝말잇기도움") or message.content.startswith('.kh') or message.content.startswith('.ㅏㅗ'):
        embed = discord.Embed(title='끝말잇기도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.시작 / .s / .ㄴ            `   :   **끝말잇기를 시작합니다.**\n`.기권 / .e / .ㄷ            `   :   **끝말잇기를 종료합니다.**\n`.끝말정보 / .ku / .ㅏㅕ     `   :   **끝말잇기의 정보를 보여줍니다.**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".도박도움") or message.content.startswith('.dh') or message.content.startswith('.오'):
        embed = discord.Embed(title='도박도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.일하기 / .mg / .ㅡㅎ       `   :   **돈을 받습니다.**\n`.룰렛 / .db / .유         `   :   **도박을 합니다.**\n`.돈 / .mn / .ㅡㅜ           `   :   **보유한 돈을 확인합니다.**\n`.올인 / .all / .미ㅣ        `   :   **보유한 돈을 도박에 올인합니다.**\n`.랭킹 / .lk / .ㅣㅏ         `   :   **돈의 랭킹을 확인합니다.**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".기타도움") or message.content.startswith('.eh') or message.content.startswith('.도'):
        embed = discord.Embed(title='기타도움', colour = 0xDC00FF)
        embed.add_field(name="명령어:", value="`.인증 / .i / .ㅑ            `   :   **로봇인지 아닌지 확인합니다.**\n`.정보 / .u / .ㅕ            `   :   **유저의 정보를 보여줍니다.**\n`.핑 / .p / .ㅔ              `   :   **봇의 핑을 알려줍니다.**\n`.레벨 / .lv / .ㅣㅍ         `   :   **레벨을 보여줍니다.**")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".한영번역") or message.content.startswith('.ke') or message.content.startswith('.ㅏㄷ'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        #띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                print(combineword)
                # Make Query String.
                dataParmas = "source=ko&target=en&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 한국어 -> 영어", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated English", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")


    if message.content.startswith(".영한번역") or message.content.startswith('.ek') or message.content.startswith('.다'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=en&target=ko&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 영어 -> 한국어", description="", color=0x5CD1E5)
                    embed.add_field(name="English to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

    if message.content.startswith(".한일번역") or message.content.startswith('.kj') or message.content.startswith('.ㅏㅓ'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=ko&target=ja&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 한국어 -> 일본어", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Japanese", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

    if message.content.startswith(".일한번역") or message.content.startswith('.jk') or message.content.startswith('.ㅓㅏ'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=ja&target=ko&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 일본어 -> 한국어", description="", color=0x5CD1E5)
                    embed.add_field(name="Japanese to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()        
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

    if message.content.startswith(".한중번역") or message.content.startswith('.kc') or message.content.startswith('.ㅏㅊ'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.

                #Simplified Chinese
                dataParmas = "source=ko&target=zh-CN&text=" + combineword

                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 한국어 -> 중국어", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Chinese", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

    if message.content.startswith(".중한번역") or message.content.startswith('.ck') or message.content.startswith('.차'):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        # 띄어쓰기 : split처리후 [1:]을 for문으로 붙인다.
        trsText = message.content.split(" ")
        try:
            if len(trsText) == 1:
                await message.channel.send("`단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.`")
            else:
                trsText = trsText[1:]
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                # Simplified Chinese
                dataParmas = "source=zh-CN&target=ko&text=" + combineword


                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="번역 | 중국어 -> 한국어", description="", color=0x5CD1E5)
                    embed.add_field(name="Chinese to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await message.channel.send("Translate Failed. HTTPError Occured.")

    if message.content.startswith(".코로나") or message.content.startswith('.co') or message.content.startswith('.채'):
        # 보건복지부 코로나 바이러스 정보사이트"
        covidSite = "http://ncov.mohw.go.kr/index.jsp"
        covidNotice = "http://ncov.mohw.go.kr"
        html = urlopen(covidSite)
        bs = BeautifulSoup(html, 'html.parser')
        latestupdateTime = bs.find('span', {'class': "livedate"}).text.split(',')[0][1:].split('.')
        statisticalNumbers = bs.findAll('span', {'class': 'num'})
        beforedayNumbers = bs.findAll('span', {'class': 'before'})

        #주요 브리핑 및 뉴스링크
        briefTasks = []
        mainbrief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
        for brf in mainbrief:
            container = []
            container.append(brf.text)
            container.append(covidNotice + brf['href'])
            briefTasks.append(container)
        print(briefTasks)

        # 통계수치
        statNum = []
        # 전일대비 수치
        beforeNum = []
        for num in range(7):
            statNum.append(statisticalNumbers[num].text)
        for num in range(4):
            beforeNum.append(beforedayNumbers[num].text.split('(')[-1].split(')')[0])

        totalPeopletoInt = statNum[0].split(')')[-1].split(',')
        tpInt = ''.join(totalPeopletoInt)
        lethatRate = round((int(statNum[3]) / int(tpInt)) * 100, 2)
        embed = discord.Embed(title="Covid-19 Virus Korea Status", description="",color=0x0008FF)
        embed.add_field(name="데이터 출처 : Ministry of Health and Welfare of Korea", value="http://ncov.mohw.go.kr/index.jsp", inline=False)
        embed.add_field(name="최신 데이터",value="해당 자료는 " + latestupdateTime[0] + "월 " + latestupdateTime[1] + "일 "+latestupdateTime[2] +" 자료입니다.", inline=False)
        embed.add_field(name="확진환자(누적)", value=statNum[0].split(')')[-1]+"("+beforeNum[0]+")",inline=True)
        embed.add_field(name="완치환자(격리해제)", value=statNum[1] + "(" + beforeNum[1] + ")", inline=True)
        embed.add_field(name="치료중(격리 중)", value=statNum[2] + "(" + beforeNum[2] + ")", inline=True)
        embed.add_field(name="사망", value=statNum[3] + "(" + beforeNum[3] + ")", inline=True)
        embed.add_field(name="누적확진률", value=statNum[6], inline=True)
        embed.add_field(name="치사율", value=str(lethatRate) + " %",inline=True)
        embed.add_field(name="- 최신 브리핑 1 : " + briefTasks[0][0],value="링크 : " + briefTasks[0][1],inline=False)
        embed.add_field(name="- 최신 브리핑 2 : " + briefTasks[1][0], value="링크 : " + briefTasks[1][1], inline=False)
        embed.set_thumbnail(url="https://wikis.krsocsci.org/images/7/79/%EB%8C%80%ED%95%9C%EC%99%95%EA%B5%AD_%ED%83%9C%EA%B7%B9%EA%B8%B0.jpg")
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".롤전적") or message.content.startswith('.lol') or message.content.startswith('.ㅣㅐㅣ'):
        try:
            if len(message.content.split(" ")) == 1:
                embed = discord.Embed(title="소환사 이름이 입력되지 않았습니다!", description="", color=0x5CD1E5)
                embed.add_field(name="소환사 이름을 입력하지 않았습니다.",
                                value=".롤전적 닉네임", inline=False)
                embed.timestamp = datetime.datetime.utcnow()
                await message.channel.send(embed=embed)
            else:
                playerNickname = ''.join((message.content).split(' ')[1:])
                # Open URL
                checkURLBool = urlopen(opggsummonersearch + quote(playerNickname))
                bs = BeautifulSoup(checkURLBool, 'html.parser')

                # 자유랭크 언랭은 뒤에 '?image=q_auto&v=1'표현이없다

                # Patch Note 20200503에서
                # Medal = bs.find('div', {'class': 'ContentWrap tabItems'}) 이렇게 바꾸었었습니다.
                # PC의 설정된 환경 혹은 OS플랫폼에 따라서 ContentWrap tabItems의 띄어쓰기가 인식이

                Medal = bs.find('div', {'class': 'SideContent'})
                RankMedal = Medal.findAll('img', {'src': re.compile('\/\/[a-z]*\-[A-Za-z]*\.[A-Za-z]*\.[A-Za-z]*\/[A-Za-z]*\/[A-Za-z]*\/[a-z0-9_]*\.png')})
                # Variable RankMedal's index 0 : Solo Rank
                # Variable RankMedal's index 1 : Flexible 5v5 rank

                # for mostUsedChampion
                mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})

                # 솔랭, 자랭 둘다 배치가 안되어있는경우 -> 사용된 챔피언 자체가 없다. 즉 모스트 챔피언 메뉴를 넣을 필요가 없다.

                # Scrape Summoner's Rank information
                # [Solorank,Solorank Tier]
                solorank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {'class': {'RankType', 'TierRank'}}))
                # [Solorank LeaguePoint, Solorank W, Solorank L, Solorank Winratio]
                solorank_Point_and_winratio = deleteTags(
                    bs.findAll('span', {'class': {'LeaguePoints', 'wins', 'losses', 'winratio'}}))
                # [Flex 5:5 Rank,Flexrank Tier,Flextier leaguepoint + W/L,Flextier win ratio]
                flexrank_Types_and_Tier_Info = deleteTags(bs.findAll('div', {
                    'class': {'sub-tier__rank-type', 'sub-tier__rank-tier', 'sub-tier__league-point',
                              'sub-tier__gray-text'}}))
                # ['Flextier W/L]
                flexrank_Point_and_winratio = deleteTags(bs.findAll('span', {'class': {'sub-tier__gray-text'}}))

                # embed.set_imag()는 하나만 들어갈수 있다.

                # 솔랭, 자랭 둘다 배치 안되어있는 경우 -> 모스트 챔피언 출력 X
                if len(solorank_Point_and_winratio) == 0 and len(flexrank_Point_and_winratio) == 0:
                    embed = discord.Embed(title="소환사 " + playerNickname + "님의 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="데이터 검색", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)

                # 솔로랭크 기록이 없는경우
                elif len(solorank_Point_and_winratio) == 0:

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]
                    embed = discord.Embed(title="소환사 " + playerNickname + "님의 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="데이터 검색", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)

                # 자유랭크 기록이 없는경우
                elif len(flexrank_Point_and_winratio) == 0:

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    embed = discord.Embed(title="소환사 " + playerNickname + "님의 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="데이터 검색", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + "WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
                # 두가지 유형의 랭크 모두 완료된사람
                else:
                    # 더 높은 티어를 thumbnail에 안착
                    solorankmedal = RankMedal[0]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')
                    flexrankmedal = RankMedal[1]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')

                    # Make State
                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]

                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()

                    cmpTier = tierCompare(solorankmedal[0], flexrankmedal[0])
                    embed = discord.Embed(title="소환사 " + playerNickname + "님의 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="데이터 검색", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    if cmpTier == 0:
                        embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    elif cmpTier == 1:
                        embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    else:
                        if solorankmedal[1] > flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        elif solorankmedal[1] < flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        else:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])

                    embed.timestamp = datetime.datetime.utcnow()
                    await message.channel.send(embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await message.channel.send(embed=embed)

        except UnicodeEncodeError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="???", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await message.channel.send(embed=embed)

        except AttributeError as e:
            embed = discord.Embed(title="존재하지 않는 소환사", description="", color=0x5CD1E5)
            embed.add_field(name="해당 닉네임의 소환사가 존재하지 않습니다.", value="소환사 이름을 확인해주세요", inline=False)
            embed.timestamp = datetime.datetime.utcnow()
            await message.channel.send(embed=embed)

    if message.content.startswith(".멜론차트") or message.content.startswith('.ml') or message.content.startswith('.ㅢ'):
        chart, msg = GetMelonChart(), ""
        for i in range(1,11):
            msg += str(i)+"위: "+chart[i-1]+"\n"
        embed = discord.Embed(title='', description=msg, color=0x2EFE2E)
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

    if message.content.startswith(".일하기") or message.content.startswith('.mg') or message.content.startswith('.ㅡㅎ'):
        ID = str(message.author.id)
        TIME = int(time.time())
        if ID in idA: #만약 등록된 ID라면
            if TIME - timeA[idA.index(ID)] < 3600: #1시간이 안 지났을 때
                embed = discord.Embed(title='오류', description='1시간 마다 일할 수 있습니다.', color=0xFF0000)
                await message.channel.send(embed=embed)
                raise ValueError #탈출
            elif TIME - timeA[idA.index(ID)] >= 3600: #1시간이 지났을 때
                timeA[idA.index(ID)] = int(time.time())
        give = random.randrange(1,10)*random.randrange(1000,10000) # 줄 돈
        if ID in idA:
            moneyA[idA.index(ID)] += give
            f = open("UserData.txt", "w") #저장
            for i in range(0,len(idA),1):
                f.write(str(idA[i])+","+str(moneyA[i])+","+str(timeA[i])+"\n")
            f.close()
        elif not ID in idA:
            idA.append(ID)
            moneyA.append(give)
            timeA.append(int(time.time()))
            f = open("UserData.txt", "w") #저장
            for i in range(0,len(idA),1):
                f.write(str(idA[i])+","+str(moneyA[i])+","+str(timeA[i])+"\n")
            f.close()
        msg = str(give)+"원 만큼 받았습니다. 현재 돈: "+str(moneyA[idA.index(ID)])+"원"
        embed = discord.Embed(title='일하기', description=msg, color=0x00FF00)
        await message.channel.send(embed=embed)
    if message.content.startswith(".룰렛") or message.content.startswith('.db') or message.content.startswith('.유'):
        ID = str(message.author.id)
        msg = message.content.split()
        if msg[1].isdecimal() == False: #만약 숫자가 아니라면
            embed = discord.Embed(title='', description='숫자만 입력해 주세요!', color=0xFF0000)
            await message.channel.send(embed=embed)
            raise ValueError
        msg[1] = int(msg[1])
        if not ID in idA or moneyA[idA.index(ID)] - int(msg[1]) < 0: #등록된 ID가 아니거나 돈이 부족하면
            embed = discord.Embed(title='오류', description='`돈이 부족합니다!`', color=0xFF0000)
            await message.channel.send(embed=embed)
            raise ValueError #탈출
        moneyA[idA.index(ID)] -= msg[1]
        give = random.randrange(1,11)
        count = await message.channel.send("`룰렛 돌리는 중...`")
        for i in range(0,2):
            await count.edit(content = ment[0])
            await asyncio.sleep(0.2)
            await count.edit(content = ment[1])
            await asyncio.sleep(0.2)
            await count.edit(content = ment[2])
            await asyncio.sleep(0.2)
        await count.edit(content = '`만약 성공하면 건 돈의` '+str(give)+"`배 를 얻어요`")
        await asyncio.sleep(1)
        if give % 2 == 0:
            await count.edit(content = "`도박 성공!`")
            moneyA[idA.index(ID)] += give*msg[1]
            await asyncio.sleep(0.5)
            await count.edit(content = "`도박 성공! 현재 돈` : "+str(moneyA[idA.index(ID)])+"`원`")
        elif give % 2 != 0:
            await count.edit(content = "`도박 실패...`")
            await asyncio.sleep(0.5)
            await count.edit(content = "`도박 실패... 현재 돈` : "+str(moneyA[idA.index(ID)])+"`원`")
        f = open("UserData.txt", "w") #저장
        for i in range(0,len(idA),1):
            f.write(str(idA[i])+","+str(moneyA[i])+","+str(timeA[i])+"\n")
        f.close()

    if message.content.startswith(".돈") or message.content.startswith('.mn') or message.content.startswith('.ㅡㅜ'):
        ID = str(message.author.id)
        if ID in idA: #만약 등록된 ID라면
            embed = discord.Embed(title='현재 보유중인 돈', description=str(moneyA[idA.index(ID)])+" 원", color=0x118811)
            await message.channel.send(embed=embed)
        elif not ID in idA: #등록된 ID가 아니라면
            embed = discord.Embed(title='현재 보유중인 돈', description="0 원", color=0x118811)
            await message.channel.send(embed=embed)

    if message.content.startswith(".올인") or message.content.startswith('.all') or message.content.startswith('.미ㅣ'):
        ID = str(message.author.id)
        if not ID in idA or moneyA[idA.index(ID)] <= 0: #만약 돈이 부족하면
            embed = discord.Embed(title='오류', description='돈이 부족합니다.', color=0xFF0000)
            await message.channel.send(embed=embed)
            raise ValueError
        give = random.randrange(2,10)
        count = await message.channel.send("룰렛 돌리는 중...")
        for i in range(0,2):
            await count.edit(content = ment[0])
            await asyncio.sleep(0.2)
            await count.edit(content = ment[1])
            await asyncio.sleep(0.2)
            await count.edit(content = ment[2])
            await asyncio.sleep(0.2)
        await count.edit(content = '만약 성공하면 건 돈의 '+str(give)+"배 를 얻어요")
        await asyncio.sleep(1)
        if give % 2 == 0:
            await count.edit(content = "`올인 성공!`")
            moneyA[idA.index(ID)]*= give
            await asyncio.sleep(0.5)
            await count.edit(content = "`올인 성공! 현재 돈` : "+str(moneyA[idA.index(ID)])+"`원`")
        elif give % 2 != 0:
            await count.edit(content = "`올인 실패...`")
            moneyA[idA.index(ID)] = 0
            await asyncio.sleep(0.5)
            await count.edit(content = "`올인 실패... 현재 돈` : "+str(moneyA[idA.index(ID)])+"`원`")
        f = open("UserData.txt", "w") #저장
        for i in range(0,len(idA),1):
            f.write(str(idA[i])+","+str(moneyA[i])+","+str(timeA[i])+"\n")
        f.close()
    
    if message.content.startswith(".랭킹") or message.content.startswith('.lk') or message.content.startswith('ㅣㅏ'):
        rank, rankA = "", []
        for i in range(0,len(idA)): rankA.append([idA[i], moneyA[i]])
        rankA = sorted(rankA, reverse = True, key = lambda x: x[1]) #많은 순으로 정렬
        for i in range(0,10): #10위 까지만 출력
            try:
                rank += str(i+1)+"위 <@"+rankA[i][0]+"> : "+str(rankA[i][1])+"\n"
            except:
                break
        embed = discord.Embed(title='돈 랭킹', description=rank, color=0xd8aa2d)
        await message.channel.send(embed=embed)

    if message.content.startswith("") and message.author.id != 760776430845558794:
        file = openpyxl.load_workbook("레벨.xlsx")
        sheet = file.active
        exp = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000,3100,3200,3300,3400,3500,3600,3700,3800,3900,4000,4100,4200,4300,4400,4500,4600,4700,4800,4900,5000,5100,5200,5300,5400,5500,5600,5700,5800,5900,6000,6100,6200,6300,6400,6500,6600,6700,6800,6900,7000,7100,7200,7300,7400,7500,7600,7700,7800,7900,8000,8100,8200,8300,8400,8500,8600,8700,8800,8900,9000,9100,9200,9300,9400,9500,9600,9700,9800,9900,10000]
        i = 1
        while True:
            if sheet["A" + str(i)].value == str(message.author.id):
                sheet["B" + str(i)].value = sheet["B" + str(i)].value + 1
                if sheet["B" + str(i)].value >= exp[sheet["C" + str(i)].value - 1]:
                    sheet["C" + str(i)].value = sheet["C" + str(i)].value + 1
                file.save("레벨.xlsx")
                break
            if sheet["A" + str(i)].value == None:
                sheet["A" + str(i)].value = str(message.author.id)
                sheet["B" + str(i)].value = 0
                sheet["C" + str(i)].value = 1
                file.save("레벨.xlsx")
                break
            i += 1

    if message.content.startswith(".정보") or message.content.startswith('.u') or message.content.startswith('.ㅕ'):
        ID = str(message.author.id)
        if ID in idA:
            date = datetime.datetime.utcfromtimestamp(((int(message.author.id) >> 22) + 1420070400000) / 1000)
            embed = discord.Embed(title= message.author.name + '님의 정보', colour = 0x00FFD1)
            embed.add_field(name="이름", value=message.author.name, inline=True)
            embed.add_field(name="서버닉네임", value=message.author.display_name, inline=True)
            embed.add_field(name="가입일", value=str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline=True)
            embed.add_field(name="아이디", value=message.author.id, inline=True)
            embed.add_field(name="레벨", value=str(sheet["C" + str(i)].value), inline=True)
            embed.add_field(name="돈", value=str(moneyA[idA.index(ID)])+" 원")
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            await message.channel.send(embed=embed)

    if message.content.startswith(".레벨") or message.content.startswith(".ㅣㅍ") or message.content.startswith(".lv"):
        embed = discord.Embed(title= message.author.name + '님의 레벨', colour = 0x00FFD1)
        embed.add_field(name="현재 레벨", value=str(sheet["C" + str(i)].value), inline=True)
        embed.add_field(name="경험치", value=str(sheet["B" + str(i)].value), inline=True)
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        await message.channel.send(embed=embed)

access_token = os.environ["BOT_TOKEN"]
client.run(access_token)

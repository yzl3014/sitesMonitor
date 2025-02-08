# sitesMonitor.py by yzl3014
# https://github.com/yzl3014/sitesMonitor
# 2025-02-08 v1
import hashlib, json, requests, time, urllib.parse
from datetime import datetime  # 获取时间。为了转换时区，不使用time
from pytz import timezone  # 时区转换。
from bs4 import BeautifulSoup  # 解析访问网站后返回的对象
from colorama import init, Fore, Back  # 命令行输出彩色文本


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}  # 自定义header

proxies = {"http": "socks5://127.0.0.1:10808", "https": "socks5://127.0.0.1:10808"}  # 代理功能。仅作为开发调试时使用


def md5(text):  # 计算文本的MD5值
    return hashlib.md5(text.encode("utf8")).hexdigest()


def tg_replace(rawText: str):  # 转义Telegram特殊字符
    # 注意，需要渲染的字符（如Markdown标记）不能被转义。
    specialLetters = ["_", "[", "]", "(", ")", "~", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for letter in specialLetters:
        if letter in rawText:
            rawText = rawText.replace(letter, "\\" + letter)  # 在特殊字符前加反斜杠
    return rawText


def tg_send(text: str, type: int):  # 发送信息到Telegram
    text = tg_replace(text)  # 转义 Telegram 要求的特殊字符
    chatId = ""
    if type == 0:  # 发送到频道或个人
        chatId = "@【CHANNEL NAME】"
    elif type == 1:
        chatId = "【CHAT ID】"
    apiLink = (
        "https://api.telegram.org/【API KEY】/sendMessage?chat_id="
        + chatId
        + "&parse_mode=MarkdownV2&text="
    )
    response = requests.get(apiLink + urllib.parse.quote(text), proxies=proxies).text
    ok = json.loads(response)["ok"]  # 提取API返回值。其中“ok”的值表示是否成功。
    print(Fore.BLUE + "推送信息到 Telegram (type=" + str(type) + ")，是否成功:", ok)


def getBJTime():  # 获取北京时间字符串。用于处理服务器时区差异。
    now = datetime.now()  # 当前时间
    target_timezone = timezone("Asia/Shanghai")  # 目标时区
    target_time = now.astimezone(target_timezone)
    return str(target_time.now())


def checkRSS(url: str):  # 检测目标网站RSS文件
    print(Back.CYAN + "任务开始：", "检测 {} 的任务即将开始。".format(url))
    start_time = time.time()  # 开始计时
    source = requests.get(url, headers=headers)  # 网页源码
    soup = BeautifulSoup(source.text, features="xml")  # 以RSS解析源码
    item = soup.channel.find_all("item")[0]


    currentMd5 = md5(source.text)  # 计算网页MD5值
    DataFile = open("data.json", "r+")  # 打开本地文件
    localData = json.loads(DataFile.read())  # 以JSON格式解析文件
    if url in localData:  # 输出若干内容以供参考
        previousMD5 = localData[url]
        print(Back.RED + "MD5检测:")
        print(Fore.BLUE + "Feed片段:", source.text[:38])
        print(Fore.BLUE + "旧MD5:", repr(previousMD5))
        print(Fore.BLUE + "新MD5:", repr(currentMd5))
        print(Fore.RED + "是否一致:", str(currentMd5 == previousMD5))
    else:
        print(Back.RED + "MD5检测：")
        print("检测的", url, "没有本地日志，将作为新链接。")
        print(Fore.BLUE + "MD5值:", currentMd5)
        localData[url] = currentMd5
        previousMD5 = "0"


    if currentMd5 != previousMD5:
        # 向本地写入最新的MD5值
        print(Back.RED + "写入发送消息并记录MD5:")
        localData[url] = currentMd5
        DataFile.seek(0)  # 光标移动到文件开头，然后进行写入
        print(Fore.BLUE + "已写入字符(个)(未保存):", DataFile.write(json.dumps(localData, sort_keys=False, indent=2)))
        DataFile.truncate()

        # 向 Telegram 频道发送内容
        sendText = f"""*‼️网站变动事件 {getBJTime()} (UTC+8) ‼️ :*

🌐网站：`{url}`

🔑Feed文件变动(md5):
> 上一次: {previousMD5}
> 本次: {currentMd5}

📝最新文章信息:
> 标题: {item.title.string}
> 发布时间: {item.pubDate.string}

💬最新文章简介:
```
{item.description.string}
```
*🔗文章链接:* {item.link.string}"""
        tg_send(sendText, 0)

    DataFile.close()  # 关闭文件
    end_time = time.time()  # 计时结束
    print(Back.CYAN + "任务结束：", "检测 {} 的任务已完成，耗时 {:.2f} 秒。\n".format(url, (end_time - start_time)))
    report = "*" + getBJTime() + " 任务结束*\n检测`{}`的任务已完成，耗时{:.2f}秒。".format(url, (end_time - start_time))
    tg_send(report, 1)


if __name__ == "__main__":
    init(autoreset=True)
    print("")
    checkRSS("https://www.chuzixuan.com/feed/")

# sitesMonitor
> 基于Typecho博客RSS文件的网站变动监测程序

本程序基于`Python 3.12.2`开发，主程序为`sitesMonitor.py`。

本程序运行后，访问目标网站的RSS文件，并获取该文件的MD5值，与`data.json`上次保存的值比对。如果有变动，则通过 Telegram Bot 向指定频道发布消息。一切完成后，程序将通过相同的Bot向指定用户发送本次监测的简单结果。

在运行之前，你需要检查以下内容：

- 是否安装所有所需的包。
- 填写代码中的空缺：`CHANNEL NAME`（报告要被发布到的频道），`CHAT ID`（运行完成后的简单结果发给谁），`API KEY`（你的Telegram Bot的API Key）。
- 保证`data.json`不是空的。
- 代理是为了在测试时，程序能够正常访问Telegram API。如果不需要代理，请去除第43行代码中的参数`proxies=proxies`。

# Telegram 频道推送结果

部分内容是截图时打码遮盖，并非Telegram显示。

![](https://github.com/user-attachments/assets/f868540a-089f-45d1-9364-a9659bec31ef)

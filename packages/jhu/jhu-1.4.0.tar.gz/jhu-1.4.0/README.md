# JHU(Join Happy Utils)
> 这个是我自己编写的一个python工具库,简化或者自动化的帮助我做一些工作

# ChangeLog
## V1.4.0(2024-04-09)
### security.py
- 追加了对称加密
- JWTAPI中的datetime.utcnow函数弃用,用了其他替代方法

## V1.3.0
- 2023-12-19:从v1.3.0版本开始,基于python3.12进行开发.并整合优化代码

## 更早的版本说明(history)
- 2023-11-30:DrissionPage具备了更强的能力,selenium不在使用,因此移除掉webdriver,追加了jwt和hash password的能力
- 2023-10-24:更新了auth,移除了钉钉,整合了钉钉和飞书的三方扫码登录
- 2023-10-23:更新了默认chrome驱动的下载版本为88.0.4324.27,当浏览器版本低于该版本内的时候,可能无法正常运行使用
- 2023-10-17:追加了在windows环境下,驱动名为chromedirver.exe的设定,同时下载完成后移除不必要的文件,仅保留驱动文件
- 2023-10-08:支持发送dingding的webhook,支持text类型和link类型的快速构建和发送
- 2023-09-14:从浏览器版本115开始,使用新的地址下载链接,请确保你的网络能够访问该地址 https://googlechromelabs.github.io/chrome-for-testing
- 2023-03-06:支持生成钉钉扫码登录的url,支撑获取钉钉扫码登录的用户信息
- 2022-11-17:工具基于python3.11版本进行开发
- 2022-11-10:支持运行chrome自动化脚本
- 2022-07-01:支持SMTP发送邮件
- 2022-06-09:企业微信发送webhook消息,当前仅支持text格式

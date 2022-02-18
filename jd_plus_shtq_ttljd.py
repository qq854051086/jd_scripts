# -*- coding: utf-8 -*
'''
cron: 20 1 * * * python3 jd_plus_shtq_ttljd.py
new Env('plus会员天天领京豆');
plus生活特权，天天领京豆
此脚本针对青龙面板编写
默认不执行，请确认自己是plus会员，并增加环境变量export JD_PLUS_VIP_SIGN=1
'''
# cron: 10 2 * * *
import os, re
try:
    import requests
except Exception as e:
    print("\n青龙面板：依赖环境管理-python3-添加新的-requests")
    exit(3)
from urllib.parse import unquote
import json
import time

requests.packages.urllib3.disable_warnings()

UserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1'
cookies = ''

class getJDCookie(object):
    # 适配各种平台环境ck
    def getckfile(self):
        if os.path.exists('/ql/config/env.sh'):
            print("当前环境青龙面板新版")
            return '/ql/config/env.sh'
        elif os.path.exists('/ql/config/cookie.sh'):
            print("当前环境青龙面板旧版")
            return '/ql/config/env.sh'
        print("在判定青龙面板时失败，请检查当前运行环境是否为‘青龙面板’，否则不要运行")
        return

    # 获取cookie
    def getCookie(self):
        global cookies
        self.getckfile()
        flag = os.environ["JD_PLUS_VIP_SIGN"] if "JD_PLUS_VIP_SIGN" in os.environ else False
        if int(flag) != 1:
            print("未添加开启plus签到变量，任务不执行")
            exit(0)

        cookies = os.environ["JD_COOKIE"] if "JD_COOKIE" in os.environ else False
        if int(flag) == False:
            print("未检测到Cookie")
            exit(0)

        cookiesList, userNameList, pinNameList = self.iscookie()
        return cookiesList, userNameList, pinNameList

    # 检测cookie格式是否正确
    def getUserInfo(self, ck, pinName, userNum):
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder&channel=4&isHomewhite=0&sceneval=2&sceneval=2&callback=GetJDUserInfoUnion'
        headers = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'close',
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'me-api.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'zh-cn'
        }
        try:
            resp = requests.get(url=url, verify=False, headers=headers, timeout=60).text
            r = re.compile(r'GetJDUserInfoUnion.*?\((.*?)\)')
            result = r.findall(resp)
            userInfo = json.loads(result[0])
            if userInfo['data']['userInfo']['isPlusVip'] == "1":
                print("当前用户为Plus用户，继续执行")
            else:
                print("当前用户不是plus用户")
                return "ck",False
            nickname = userInfo['data']['userInfo']['baseInfo']['nickname']
            return ck, nickname
        except Exception:
            context = f"账号{userNum}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def iscookie(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookiesList = []
        userNameList = []
        pinNameList = []
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                print("您已配置{}个账号".format(len(result)))
                u = 1
                for i in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(i)
                    pinName = unquote(pinName[0])
                    # 获取账号名
                    ck, nickname = self.getUserInfo(i, pinName, u)
                    if nickname != False:
                        cookiesList.append(ck)
                        userNameList.append(nickname)
                        pinNameList.append(pinName)
                    else:
                        u += 1
                        continue
                    u += 1
                if len(cookiesList) > 0 and len(userNameList) > 0:
                    return cookiesList, userNameList, pinNameList
                else:
                    print("没有可用Cookie，已退出")
                    exit(3)
            else:
                print("cookie 格式错误！...本次操作已退出")
                exit(4)
        else:
            print("cookie 格式错误！...本次操作已退出")
            exit(4)


def start():
    print("\n")
    print("### plus生活特权，天天领京豆 ###")
    print("\n")

    getCk = getJDCookie()
    cookiesList, userNameList, pinNameList = getCk.getCookie()

    for ck in cookiesList:
        print(f"\n账号：{userNameList[cookiesList.index(ck)]}")
        url = 'https://api.m.jd.com/client.action?functionId=doInteractiveAssignment'
        header = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-CN;q=1',
            'origin': 'https://pro.m.jd.com',
            'referer': 'https://pro.m.jd.com',
            'Content-Type': 'application/x-www-form-urlencoded'

        }
        data = "appid=babelh5&body= %7B%22encryptProjectId%22%3A%223FCTNcsr7BoQUw7dx1h3KJ9Hi9yJ%22%2C%22encryptAssignmentId%22%3A%223o2cWjTjZoCjKJcQwQ2bFgLkTnZC%22%2C%22completionFlag%22%3Atrue%2C%22itemId%22%3A%221%22%2C%22sourceCode%22%3A%22aceaceqingzhan%22%7D&sign=11"
        try:
            resp = requests.post(url=url,data=data, headers=header, verify=False, timeout=30).json()
            print("\n原始数据:", resp)
            if int(resp["code"]) == 0:
                print(f"\n签到：{resp['msg']}")
            if int(resp["subCode"]) == 0:
                print("\n获得京豆：", resp['rewardsInfo']["successRewards"]["3"][0]["rewardName"])
            time.sleep(1)
        except Exception as e:
            print(e)
            continue
    print("\n运行结束")


if __name__ == '__main__':
    start()
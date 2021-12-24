# -*- coding: utf8 -*-
import base64
import json
import random
import re
import os
import sys
import time
import logging
import execjs
from urllib import parse
import requests
from bs4 import BeautifulSoup
from Parser import Parser1, Parser2
from aip import AipOcr
from requests.adapters import HTTPAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# 使用FileHandler输出到文件
fh = logging.FileHandler('log.txt', encoding='utf-8')
fh.setFormatter(formatter)

# 使用StreamHandler输出到控制台
sh = logging.StreamHandler()
sh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)

# 连接超时时间
TIMEOUT = 10
# 登录失败时重试的次数
RETRY = 5
# 每次连接的间隔
RETRY_INTERVAL = 10


class YQTB:
    # 初始化参数
    def __init__(self):
        try:
            self.USERNAME = str(os.environ['USERNAME'])  # 学号
            self.PASSWORD = str(os.environ['PASSWORD'])  # 密码
            if self.USERNAME == '' or self.PASSWORD == '':
                raise ValueError("无法获取学号和密码")
        except Exception as e:
            logger.error('无法获取学号和密码，程序终止')
            sys.exit(1)
        self.csrfToken = ''
        self.formStepId = ''
        self.formUrl = ''
        self.workflowId = ''
        self.client = requests.session()
        self.client.trust_env = False
        self.client.proxies = {
            'http': 'socks5://nat.opapa.top:9192',
            'https': 'socks5://nat.opapa.top:9192'
        }
        try:
            ip = self.client.get("http://ip-api.com/json/?lang=zh-CN").json()
            logger.info('连接到代理服务器')
        except Exception as e:
            logger.error('连接代理服务器失败')
            self.client.proxies = None
            pass
        self.boundFields = "fieldSTQKzdjgmc,fieldSTQKjtcyglkssj,fieldCXXXsftjhb,fieldJCDDqmsjtdd,fieldYQJLksjcsj," \
                           "fieldSTQKjtcyzd,fieldJBXXjgsjtdz,fieldSTQKbrstzk,fieldSTQKfrtw,fieldSTQKjtcyqt," \
                           "fieldCXXXjtfslc,fieldJBXXlxfs,fieldSTQKxgqksm,fieldSTQKpcsj,fieldJKMsfwlm,fieldJKHDDzt," \
                           "fieldYQJLsfjcqtbl,fieldYQJLzhycjcsj,fieldSTQKfl,fieldSTQKhxkn,fieldJBXXbz,fieldCXXXsfylk," \
                           "fieldFLid,fieldjgs,fieldSTQKglfs,fieldCXXXsfjcgyshqzbl,fieldSTQKjtcyfx," \
                           "fieldCXXXszsqsfyyshqzbl,fieldJCDDshi,fieldSTQKrytsqkqsm,fieldJCDDs,fieldSTQKjtcyfs," \
                           "fieldSTQKjtcyzljgmc,fieldSQSJ,fieldJZDZC,fieldJBXXnj,fieldSTQKjtcyzdkssj,fieldSTQKfx," \
                           "fieldSTQKfs,fieldYQJLjcdry,fieldCXXXjtfsdb,fieldCXXXcxzt,fieldYQJLjcddshi," \
                           "fieldCXXXjtjtzz,fieldCXXXsftjhbs,fieldHQRQ,fieldSTQKjtcyqtms,fieldCXXXksjcsj," \
                           "fieldSTQKzdkssj,fieldSTQKfxx,fieldSTQKjtcyzysj,fieldjgshi,fieldSTQKjtcyxm,fieldJBXXsheng," \
                           "fieldZJYCHSJCYXJGRQzd,fieldJBXXdrsfwc,fieldqjymsjtqk,fieldJBXXdw,fieldCXXXjcdr," \
                           "fieldCXXXsftjhbjtdz,fieldJCDDq,fieldSFJZYM,fieldSTQKjtcyclfs,fieldSTQKxm,fieldCXXXjtgjbc," \
                           "fieldSTQKjtcygldd,fieldSTQKjtcyzdjgmcc,fieldSTQKzd,fieldSTQKqt,fieldCXXXlksj," \
                           "fieldSTQKjtcyfrsj,fieldCXXXjtfsqtms,fieldSTQKjtcyzdmc,fieldCXXXjtfsfj,fieldJBXXfdy," \
                           "fieldSTQKjtcyjmy,fieldJBXXxm,fieldJKMjt,fieldSTQKzljgmc,fieldCXXXzhycjcsj," \
                           "fieldCXXXsftjhbq,fieldSTQKqtms,fieldYCFDY,fieldJBXXxb,fieldSTQKglkssj,fieldCXXXjtfspc," \
                           "fieldSTQKbrstzk1,fieldYCBJ,fieldCXXXssh,fieldSTQKzysj,fieldLYYZM,fieldJBXXgh,fieldCNS," \
                           "fieldCXXXfxxq,fieldSTQKclfs,fieldSTQKqtqksm,fieldCXXXqjymsxgqk,fieldYCBZ,fieldSTQKjmy," \
                           "fieldSTQKjtcyxjwjjt,fieldJBXXxnjzbgdz,fieldSTQKjtcyfl,fieldSTQKjtcyzdjgmc,fieldCXXXddsj," \
                           "fieldSTQKfrsj,fieldSTQKgldd,fieldCXXXfxcfsj,fieldJBXXbj,fieldSTQKjtcyfxx,fieldSTQKks," \
                           "fieldJBXXcsny,fieldCXXXjtzzq,fieldJBXXJG,fieldCXXXdqszd,fieldCXXXjtzzs,fieldJBXXshi," \
                           "fieldSTQKjtcyfrtw,fieldSTQKjtcystzk1,fieldCXXXjcdqk,fieldSTQKzdmc,fieldSTQKjtcyks," \
                           "fieldSTQKjtcystzk,fieldCXXXjtfshc,fieldCXXXcqwdq,fieldSTQKxjwjjt,fieldSTQKjtcypcsj," \
                           "fieldJBXXqu,fieldSTQKlt,fieldJBXXjgshi,fieldYQJLjcddq,fieldYQJLjcdryjkqk,fieldYQJLjcdds," \
                           "fieldSTQKjtcyhxkn,fieldCXXXjtzz,fieldJBXXjgq,fieldCXXXjtfsqt,fieldJBXXjgs," \
                           "fieldSTQKjtcylt,fieldSTQKzdjgmcc,fieldJBXXqjtxxqk,fieldDQSJ,fieldSTQKjtcyglfs "
        self.client.headers = {
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent':
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7',
        }

    #新版教务系统需要加密
    def desEnc(self, data, firstKey, sencondKey, thirdKey):
        with open('./des.js', 'r', encoding='UTF-8') as file:
            js = file.read()
        des = execjs.compile(js)
        return des.call('strEnc', data, firstKey, sencondKey, thirdKey)

    # 登陆账号
    def login(self):
        logger.info('开始登陆')
        res = self.client.get(url="https://yq.gzhu.edu.cn/", timeout=TIMEOUT)
        if res.status_code != 200:
            raise ConnectionError('无法连接到网站')
        soup = BeautifulSoup(res.text, "html.parser")
        form = soup.find_all('input')
        post_url = soup.find('form')['action']
        post_data = {}
        for row in form:
            if row.has_attr('name') and row.has_attr('value'):
                post_data[row['name']] = row['value']

        post_data['un'] = self.USERNAME
        post_data['pd'] = self.PASSWORD
        post_data['ul'] = len(self.USERNAME)
        post_data['pl'] = len(self.PASSWORD)
        encData = post_data['un'] + post_data['pd'] + post_data['lt']
        post_data['rsa'] = self.desEnc(encData, '1', '2', '3')

        login_post_url = parse.urljoin(res.url, post_url)

        res = self.client.post(url=login_post_url, data=post_data)
        soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

        if soup.title.string != '广州大学':
            # 账号或密码错误
            msg = soup.select('#msg')[0].text
            if msg == '账号或密码错误':
                logger.error('账号或密码错误，程序终止')
                self.notify('打卡失败——账号或密码错误')
                # 直接退出程序
                sys.exit(1)
            logger.warning('验证码错误，尝试重新登陆')
            return False
        logger.info('登陆成功')
        return True

    # 准备数据
    def prepare(self):
        logger.info("准备数据")
        res = self.client.get(
            url=
            "https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start?back=1&x_posted=true",
            timeout=TIMEOUT)
        if res.status_code != 200:
            raise ConnectionError('无法连接到网站')
        soup = BeautifulSoup(res.content.decode('utf-8'), 'html.parser')
        self.csrfToken = soup.find(attrs={"itemscope": "csrfToken"})['content']
        self.formStepId = re.findall(r"\d+", res.url)[0]
        self.formUrl = res.url
        # 温馨提示
        if self.formStepId == '1':
            self.workflowId = re.findall(r"workflowId = \"(.*?)\"",
                                         res.content.decode('utf-8'))[0]
            url = "https://yqtb.gzhu.edu.cn/infoplus/interface/preview"
            payload = {
                'workflowId': self.workflowId,
                'rand': random.uniform(300, 400),
                'width': 1440,
                'csrfToken': self.csrfToken
            }
            headers = {
                'Host':
                    'yqtb.gzhu.edu.cn',
                'Content-Length':
                    '123',
                'Pragma':
                    'no-cache',
                'Cache-Control':
                    'no-cache',
                'Accept':
                    'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With':
                    'XMLHttpRequest',
                'User-Agent':
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Content-Type':
                    'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin':
                    'https://yqtb.gzhu.edu.cn',
                'Referer':
                    'https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start?back=1&x_posted=true',
                'Accept-Encoding':
                    'gzip, deflate',
                'Accept-Language':
                    'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7',
                'Connection':
                    'close'
            }

            res = self.client.post(url, headers=headers, data=payload)
            formData = Parser2(res.json()).get()

            url = "https://yqtb.gzhu.edu.cn/infoplus/interface/start"
            payload = {
                'idc': 'XNYQSB',
                'release': '',
                'admin': 'false',
                'formData': json.dumps(formData),
                'lang': 'cn',
                'csrfToken': self.csrfToken
            }
            headers = {
                'Host':
                    'yqtb.gzhu.edu.cn',
                'Content-Length':
                    '4202',
                'Accept':
                    'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With':
                    'XMLHttpRequest',
                'User-Agent':
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Content-Type':
                    'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin':
                    'https://yqtb.gzhu.edu.cn',
                'Referer':
                    'https://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start?back=1&x_posted=true',
                'Accept-Encoding':
                    'gzip, deflate',
                'Accept-Language':
                    'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7',
                'Connection':
                    'close'
            }

            res = self.client.post(url, headers=headers, data=payload).json()
            if res['errno']:
                self.notify('system error')
                return False
            else:
                self.formStepId = re.findall(r"\d+", res['entities'][0])[0]
                self.formUrl = "https://yqtb.gzhu.edu.cn/infoplus/form/{}/render?back=2".format(
                    self.formStepId)
        post_data = {
            'stepId': self.formStepId,
            'instanceId': '',
            'admin': 'false',
            'rand': random.uniform(300, 400),
            'width': 1440,
            'lang': 'zh',
            'csrfToken': self.csrfToken
        }
        headers = {
            'Host':
                'yqtb.gzhu.edu.cn',
            'Accept':
                'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':
                'XMLHttpRequest',
            'User-Agent':
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Content-Type':
                'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':
                'https://yqtb.gzhu.edu.cn',
            'Referer':
                self.formUrl,
            'Accept-Encoding':
                'gzip, deflate',
            'Accept-Language':
                'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7',
            'Connection':
                'close'
        }
        res = self.client.post(
            url="https://yqtb.gzhu.edu.cn/infoplus/interface/render",
            headers=headers,
            data=post_data)
        self.getDatas = res.json()
        return True

    # 开始执行打卡
    def start(self):
        logger.info("执行打卡")
        formData = Parser1(self.getDatas).get(),
        formData[0]["_VAR_URL"] = self.formUrl
        formData[0]['_VAR_ENTRY_NAME'] = '学生健康状况申报_'
        formData[0]['_VAR_ENTRY_TAGS'] = '疫情应用,移动端'

        formData[0]['fieldYQJLsfjcqtbl'] = '2'
        formData[0]['fieldJKMsfwlm'] = '1'
        formData[0]['fieldCXXXsftjhb'] = '2'
        headers = {
            'Host':
                'yqtb.gzhu.edu.cn',
            'Accept':
                'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With':
                'XMLHttpRequest',
            'User-Agent':
                'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Content-Type':
                'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin':
                'https://yqtb.gzhu.edu.cn',
            'Referer':
                self.formUrl,
            'Accept-Encoding':
                'gzip, deflate',
            'Accept-Language':
                'zh-CN,zh;q=0.9,en;q=0.8,und;q=0.7',
            'Connection':
                'close'
        }
        post_data1 = {
            'stepId': self.formStepId,
            'actionId': 1,
            'formData': json.dumps(formData[0]),
            'timestamp': int(time.time()),
            'rand': random.uniform(300, 500),
            'boundFields': self.boundFields,
            'csrfToken': self.csrfToken,
            'lang': 'zh'
        }

        post_data2 = {
            'stepId': self.formStepId,
            'actionId': 1,
            'formData': json.dumps(formData[0]),
            'timestamp': int(time.time()),
            'rand': random.uniform(300, 500),
            'boundFields': self.boundFields,
            'csrfToken': self.csrfToken,
            'lang': 'zh',
            'nextUsers': '{}',
            'remark': ''
        }

        res1 = self.client.post(
            url='https://yqtb.gzhu.edu.cn/infoplus/interface/listNextStepsUsers',
            headers=headers,
            data=post_data1)
        res2 = self.client.post(
            url='https://yqtb.gzhu.edu.cn/infoplus/interface/doAction',
            headers=headers,
            data=post_data2)

        if res1.json()['errno'] or res2.json()['errno']:
            return False
        return True

    # 消息推送
    def notify(self, msg):
        try:
            self.PUSH_PLUS_TOKEN = os.environ['PUSH_PLUS_TOKEN']
            if self.PUSH_PLUS_TOKEN == '':
                raise ValueError("未提供PUSH_PLUS_TOKEN")
            self.pushNotify(msg)
        except:
            pass

    def pushNotify(self, msg):
        with open('log.txt') as f:
            contents = f.read()
            msg = '<h1>' + msg + '</h1>\n' + contents
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": self.PUSH_PLUS_TOKEN,
            "title": '健康打卡',
            "content": msg,
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = json.dumps(requests.post(url, data=body,
                                            headers=headers).json(),
                              ensure_ascii=False)
        datas = json.loads(response)
        if datas['code'] == 200:
            logger.info('【Push+】发送通知消息成功')
        elif datas['code'] == 600:
            logger.error('【Push+】PUSH_PLUS_TOKEN 错误')
        else:
            logger.error('【Push+】发送通知调用API失败！！')

    # 开始运行
    def run(self):
        res = self.login()
        if res:
            res = self.prepare()
        else:
            raise RuntimeError('登录失败')
        if res:
            res = self.start()
        else:
            raise RuntimeError('数据准备失败')
        if res:
            logger.info('打卡成功')
            self.notify('打卡成功')
            sys.exit(0)
        else:
            raise RuntimeError('数据提交失败')


# 云函数
def main_handler(event, context):
    logger.info('got event{}'.format(event))
    for _ in range(RETRY):
        r = YQTB()
        try:
            r.run()
        except Exception as e:
            logger.error(e)
            if _ == RETRY - 1:
                r.notify('打卡失败')
                sys.exit(1)
            else:
                time.sleep(RETRY_INTERVAL)


# 本地测试
if __name__ == '__main__':
    for _ in range(RETRY):
        r = YQTB()
        try:
            r.run()
        except Exception as e:
            logger.error(e)
            if _ == RETRY - 1:
                r.notify('打卡失败')
                sys.exit(1)
            else:
                time.sleep(RETRY_INTERVAL)
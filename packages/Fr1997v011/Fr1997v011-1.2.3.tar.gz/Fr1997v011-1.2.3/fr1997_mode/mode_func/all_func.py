import re
import os
import sys
import uuid
import time
import json
import redis
import pymysql
import random
import hashlib
import requests
import ctypes
import struct
import base64
import memcache  # pip install python-memcached
from elasticsearch import Elasticsearch  # ES
from concurrent.futures import ThreadPoolExecutor  # 线程次
from pypinyin import pinyin, Style  # 汉字转拼音

import execjs  # pip install PyExecJS
from urllib import parse  # 三位
from urllib.parse import quote  # 两位
from urllib.parse import urlparse, quote

# 腾讯云cos  pip install -U cos-python-sdk-v5
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

"""
    pip install redis
    pip install elasticsearch
    pip install python-memcached
    pip install PyExecJS
    pip install -U cos-python-sdk-v5
    pip install pypinyin
"""

"""
    配置文件
        所有配置在这个地方读取 
        使用内存缓存机制 memcache
        没有读取到内存中的配置，这个包相当于不能用
    pip3 cache purge
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Fr1997v011==1.1.9
"""


# 存储内存数据
def cache_set(key, data, save_time=None):
    mc = memcache.Client(['127.0.0.1:11211'], debug=True)
    if save_time:
        mc.set(key=key, val=data, time=save_time)
    else:
        mc.set(key=key, val=data)  # 永久存储


# 获取内存数据
def cache_get(key):
    mc = memcache.Client(['127.0.0.1:11211'], debug=True)
    return mc.get(key)


config_dict = cache_get("my_config_dict")
if not config_dict:
    sys.exit(0)


# 抖音加密参数破解
class ZhihuSign(object):
    local_48 = [48, 53, 57, 48, 53, 51, 102, 55, 100, 49, 53, 101, 48, 49, 100, 55]
    local_55 = "6fpLRqJO8M/c3jnYxFkUVC4ZIG12SiH=5v0mXDazWBTsuw7QetbKdoPyAl+hN9rgE"
    h = {
        "zk": [1170614578, 1024848638, 1413669199, -343334464, -766094290, -1373058082, -143119608, -297228157,
               1933479194, -971186181, -406453910, 460404854, -547427574, -1891326262, -1679095901, 2119585428,
               -2029270069, 2035090028, -1521520070, -5587175, -77751101, -2094365853, -1243052806, 1579901135,
               1321810770, 456816404, -1391643889, -229302305, 330002838, -788960546, 363569021, -1947871109],
        "zb": [20, 223, 245, 7, 248, 2, 194, 209, 87, 6, 227, 253, 240, 128, 222, 91, 237, 9, 125, 157, 230, 93, 252,
               205, 90, 79, 144, 199, 159, 197, 186, 167, 39, 37, 156, 198, 38, 42, 43, 168, 217, 153, 15, 103, 80, 189,
               71, 191, 97, 84, 247, 95, 36, 69, 14, 35, 12, 171, 28, 114, 178, 148, 86, 182, 32, 83, 158, 109, 22, 255,
               94, 238, 151, 85, 77, 124, 254, 18, 4, 26, 123, 176, 232, 193, 131, 172, 143, 142, 150, 30, 10, 146, 162,
               62, 224, 218, 196, 229, 1, 192, 213, 27, 110, 56, 231, 180, 138, 107, 242, 187, 54, 120, 19, 44, 117,
               228, 215, 203, 53, 239, 251, 127, 81, 11, 133, 96, 204, 132, 41, 115, 73, 55, 249, 147, 102, 48, 122,
               145, 106, 118, 74, 190, 29, 16, 174, 5, 177, 129, 63, 113, 99, 31, 161, 76, 246, 34, 211, 13, 60, 68,
               207, 160, 65, 111, 82, 165, 67, 169, 225, 57, 112, 244, 155, 51, 236, 200, 233, 58, 61, 47, 100, 137,
               185, 64, 17, 70, 234, 163, 219, 108, 170, 166, 59, 149, 52, 105, 24, 212, 78, 173, 45, 0, 116, 226, 119,
               136, 206, 135, 175, 195, 25, 92, 121, 208, 126, 139, 3, 75, 141, 21, 130, 98, 241, 40, 154, 66, 184, 49,
               181, 46, 243, 88, 101, 183, 8, 23, 72, 188, 104, 179, 210, 134, 250, 201, 164, 89, 216, 202, 220, 50,
               221, 152, 140, 33, 235, 214],
        "zm": [120, 50, 98, 101, 99, 98, 119, 100, 103, 107, 99, 119, 97, 99, 110, 111]
    }

    @staticmethod
    def pad(data_to_pad):
        padding_len = 16 - len(data_to_pad) % 16
        padding = chr(padding_len).encode() * padding_len
        return data_to_pad + padding

    @staticmethod
    def unpad(padded_data):
        padding_len = padded_data[-1]
        return padded_data[:-padding_len]

    @staticmethod
    def left_shift(x, y):
        x, y = ctypes.c_int32(x).value, y % 32
        return ctypes.c_int32(x << y).value

    @staticmethod
    def Unsigned_right_shift(x, y):
        x, y = ctypes.c_uint32(x).value, y % 32
        return ctypes.c_uint32(x >> y).value

    @classmethod
    def Q(cls, e, t):
        return cls.left_shift((4294967295 & e), t) | cls.Unsigned_right_shift(e, 32 - t)

    @classmethod
    def G(cls, e):
        t = list(struct.pack(">i", e))
        n = [cls.h['zb'][255 & t[0]], cls.h['zb'][255 & t[1]], cls.h['zb'][255 & t[2]], cls.h['zb'][255 & t[3]]]
        r = struct.unpack(">i", bytes(n))[0]
        return r ^ cls.Q(r, 2) ^ cls.Q(r, 10) ^ cls.Q(r, 18) ^ cls.Q(r, 24)

    @classmethod
    def g_r(cls, e):
        n = list(struct.unpack(">iiii", bytes(e)))
        [n.append(n[r] ^ cls.G(n[r + 1] ^ n[r + 2] ^ n[r + 3] ^ cls.h['zk'][r])) for r in range(32)]
        return list(
            struct.pack(">i", n[35]) + struct.pack(">i", n[34]) + struct.pack(">i", n[33]) + struct.pack(">i", n[32]))

    @classmethod
    def re_g_r(cls, e):
        n = [0] * 32 + list(struct.unpack(">iiii", bytes(e)))[::-1]
        for r in range(31, -1, -1):
            n[r] = cls.G(n[r + 1] ^ n[r + 2] ^ n[r + 3] ^ cls.h['zk'][r]) ^ n[r + 4]
        return list(
            struct.pack(">i", n[0]) + struct.pack(">i", n[1]) + struct.pack(">i", n[2]) + struct.pack(">i", n[3]))

    @classmethod
    def g_x(cls, e, t):
        n = []
        i = 0
        for _ in range(len(e), 0, -16):
            o = e[16 * i: 16 * (i + 1)]
            a = [o[c] ^ t[c] for c in range(16)]
            t = cls.g_r(a)
            n += t
            i += 1
        return n

    @classmethod
    def re_g_x(cls, e, t):
        n = []
        i = 0
        for _ in range(len(e), 0, -16):
            o = e[16 * i: 16 * (i + 1)]
            a = cls.re_g_r(o)
            t = [a[c] ^ t[c] for c in range(16)]
            n += t
            t = o
            i += 1
        return n

    @classmethod
    def b64encode(cls, md5_bytes: bytes, device: int = 0, seed: int = 63) -> str:
        local_50 = bytes([seed, device]) + md5_bytes  # 随机数  0 是环境检测通过
        local_50 = cls.pad(bytes(local_50))
        local_34 = local_50[:16]
        local_35 = [local_34[local_11] ^ cls.local_48[local_11] ^ 42 for local_11 in range(16)]
        local_36 = cls.g_r(local_35)
        local_38 = local_50[16:]
        local_39 = cls.g_x(local_38, local_36)
        local_53 = local_36 + local_39
        local_56 = 0
        local_57 = ""
        for local_13 in range(len(local_53) - 1, 0, -3):
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_53[local_13] ^ cls.Unsigned_right_shift(58, local_58) & 255
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 1] ^ cls.Unsigned_right_shift(58, local_58) & 255) << 8
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 2] ^ cls.Unsigned_right_shift(58, local_58) & 255) << 16
            local_57 = local_57 + cls.local_55[local_59 & 63]
            local_57 = local_57 + cls.local_55[cls.Unsigned_right_shift(local_59, 6) & 63]
            local_57 = local_57 + cls.local_55[cls.Unsigned_right_shift(local_59, 12) & 63]
            local_57 = local_57 + cls.local_55[cls.Unsigned_right_shift(local_59, 18) & 63]
        return local_57

    @classmethod
    def b64decode(cls, x_zse_96: str) -> dict:
        local_56 = 0
        local_57 = []
        for local_13 in range(0, len(x_zse_96), 4):
            local_59 = (cls.local_55.index(x_zse_96[local_13 + 3]) << 18) + (
                    cls.local_55.index(x_zse_96[local_13 + 2]) << 12) + (
                               cls.local_55.index(x_zse_96[local_13 + 1]) << 6) + cls.local_55.index(
                x_zse_96[local_13])
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_57.append((local_59 & 255) ^ cls.Unsigned_right_shift(58, local_58))
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_57.append(((local_59 >> 8) & 255) ^ cls.Unsigned_right_shift(58, local_58))
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_57.append(((local_59 >> 16) & 255) ^ cls.Unsigned_right_shift(58, local_58))
        local_36, local_39 = local_57[-16:][::-1], local_57[:-16][::-1]
        local_38 = cls.re_g_x(local_39, local_36)
        local_35 = cls.re_g_r(local_36)
        local_34 = [local_35[local_11] ^ cls.local_48[local_11] ^ 42 for local_11 in range(16)]
        local_50 = cls.unpad(bytes(local_34 + local_38))
        return {
            'seed': local_50[0],
            'device': local_50[1],
            'md5_bytes': local_50[2:]
        }


# 静态函数 【其它函数集合】
class ModeStatic:
    # 运行计算机判断 【通过判断计算机，方便链接内网，加快数据库访问速度，判断资源位置】
    @staticmethod
    def run_machine():
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
        machine_cfg = {
            # win_gx8r9
            'd4:93:90:25:1b:60': {
                'type': 'win_gx8r9',
                'platform': 0
            },

            # esc_tx 高阳的腾讯云
            '52:54:00:55:0b:d4': {
                'type': 'esc_tx',
                'platform': 0
            },

            # esc_jike_pachong1
            '52:54:00:03:18:2c': {
                'type': 'esc_jike_pachong1',
                'platform': 1
            },
        }

        if mac_address in machine_cfg:
            return machine_cfg[mac_address]
        else:
            return {'type': 'other', 'platform': 0}

    # 手机号判断
    @staticmethod
    def phone_num(num):
        num = str(num.strip())
        # 中国联通：130，131，132，155，156，185，186，145，176
        # 中国移动：134, 135 ,136, 137, 138, 139, 147, 150, 151, 152, 157, 158, 159, 178, 182, 183, 184, 187, 188
        # 中国电信：133,153,189
        pat_lt = re.compile(r'^1(3[0-2]|45|5[5-6]|8[5-6]|76)\d{8}$')
        pat_yd = re.compile(r'^1(3[4-9]|47|5[0-27-9]|8[2-47-8]|78)\d{8}$')
        pat_dx = re.compile(r'^1(33|53|89)\d{8}$')

        if pat_lt.match(num):
            return f"联通_{pat_lt.match(num).group()}"
        elif pat_yd.match(num):
            return f"移动_{pat_yd.match(num).group()}"
        elif pat_dx.match(num):
            return f"电信_{pat_dx.match(num).group()}"
        else:
            return 0

    # 文本截取手机号  --> dict
    @staticmethod
    def phone_text(text):
        # text 不需要去空白
        phone_dict = {}  # 号码 + 个数

        # 匹配出所有 以1开头 11位的数字
        pat = re.compile(r'1\d{10}')
        res = pat.findall(text)

        # 统计每个好吗 以及个数 判断是否是标准号码 以及 运营商
        for phone in res:
            if phone_dict.get(phone):
                phone_dict[phone] += 1
            else:
                phone_dict[phone] = 1
        return phone_dict

    # user_agent
    @staticmethod
    def get_user_agent(one=False):
        user_agents = config_dict['user_agents']
        if one:
            return random.choice(user_agents)
        else:
            return user_agents

    # Windows合法文件名 转为Windows合法文件名
    @staticmethod
    def title_path(title: str):
        lst = ['\r', '\n', '\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for key in lst:
            title = title.replace(key, '-')
        if len(title) > 60:
            title = title[:60]
        return title.strip()

    # md5
    @staticmethod
    def md5_base(text, salt=None):
        md5 = hashlib.md5()
        if salt:
            md5 = hashlib.md5(salt.encode('utf-8'))
        md5.update(text.encode('utf-8'))
        result = md5.hexdigest()
        return result

    # ua 详情
    @staticmethod
    def ua_info(ua_string):
        from user_agents import parse
        user_agent = parse(ua_string)

        if user_agent.is_pc:
            user_use = '电脑'
        elif user_agent.is_mobile:
            user_use = '手机'
        elif user_agent.is_tablet:
            user_use = '平板'
        else:
            user_use = '其他'

        return {
            'browser': user_agent.browser.family,  # 浏览器
            'user_use': user_use,
            'browser_sys': user_agent.os.family,  # 系统
            'browser_device_brand': user_agent.device.brand,  # '品牌'
            'browser_device_type': user_agent.device.model,  # 'iPhone'
            'browser_all': str(user_agent),  # "iPhone / iOS 5.1 / Mobile Safari 5.1"
        }

    # 图片转base64
    @staticmethod
    def img_md5(pic_path):
        import base64
        # 将本地图片转换为base64编码和md5值
        with open(pic_path, 'rb') as f:
            image = f.read()
            image_base64 = str(base64.b64encode(image), encoding='utf-8')
            my_md5 = hashlib.md5()
            img_data = base64.b64decode(image_base64)
            my_md5.update(img_data)
            myhash = my_md5.hexdigest()
        return image_base64, myhash

    # cookie解析
    @staticmethod
    def cookies_split(cookie_str: str) -> str:
        # 判断是否为字符串
        if not isinstance(cookie_str, str):
            raise TypeError("cookie_str must be str")

        # 拆分Set-Cookie字符串,避免错误地在expires字段的值中分割字符串。
        cookies_list = re.split(', (?=[a-zA-Z])', cookie_str)

        # 拆分每个Cookie字符串，只获取第一个分段（即key=value部分）
        cookies_list = [cookie.split(';')[0] for cookie in cookies_list]

        # 拼接所有的Cookie
        cookie_str = ";".join(cookies_list)

        return cookie_str


# requests 封装
class HttpJike(object):

    def __init__(self):
        self.status_code = 500
        self.msg = 'ok'
        self.text = None
        self.json = None
        self.ret_url = None

    # cookie 分隔
    @staticmethod
    def cookie_format(cookie):
        cookie_dict = {}
        c = cookie.split(";")
        for i in c:
            cc = i.split('=')
            if len(cc) > 1:
                cookie_dict[str(cc[0]).strip()] = str(cc[1]).strip()
            else:
                cookie_dict[str(cc[0]).strip()] = ''
        return cookie_dict

    # ip代理 隧道代理
    @staticmethod
    def proxies_choose(p=1, httpx=0):
        # 注意:目前只有 1,2 两个可以使用  httpx特殊请求
        if p is None:
            p = random.randint(1, 2)

        proxy = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy']
        port = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port']
        acc = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc']
        pwd = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']

        proxies = {
            "http": f"http://{acc}:{pwd}@{proxy}:{port}/",
            "https": f"http://{acc}:{pwd}@{proxy}:{port}/"
        }
        if httpx == 1:
            proxies = {
                "http://": f"http://{acc}:{pwd}@{proxy}:{port}/",
                "https://": f"http://{acc}:{pwd}@{proxy}:{port}/"
            }
        return proxies

    # scrapy 代理选择 数据返回
    @classmethod
    def proxies_choose_dict(cls, p):
        # 注意:目前只有 1,2,3 两个可以使用
        proxies_dict = {
            'proxy': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy'],
            'port': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port'],
            'acc': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc'],
            'pwd': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']
        }
        return proxies_dict

    # ip代理 抖查查代理
    @staticmethod
    def proxies_douchacha_ip(num=1):
        response = HttpJike.get(url=f'http://39.107.202.153:8088/get_short_proxy?num={num}')
        res = response.json
        return res['proxy_list']

    # 异步代理 的使用
    @staticmethod
    def aiohttp_proxy():
        ret = []
        ip_tunnel = config_dict['proxy']['tunnel']
        for i in ip_tunnel:
            ret.append({
                'proxy': f'http://{ip_tunnel[i]["proxy"]}:15818',
                'a': ip_tunnel[i]['acc'],
                'p': ip_tunnel[i]['pwd'],
            })
        return ret

    @staticmethod
    def get_headers(headers):
        if headers is None:
            return config_dict['base_headers']
        return headers

    @classmethod
    def get(cls, url, headers=None, proxies=None):
        req = cls()
        try:
            response = requests.get(
                url=url,
                headers=cls.get_headers(headers=headers),
                proxies=proxies
            )
            req.status_code = response.status_code
            req.ret_url = response.url
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    @classmethod
    def post(cls, url, headers=None, data=None):
        req = cls()
        try:
            response = requests.post(
                url=url,
                headers=cls.get_headers(headers=headers),
                data=json.dumps(data),
            )
            req.status_code = response.status_code
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    # 代理
    @classmethod
    def http_ip(self, ip):
        proxies = {
            'https': ip,
            'http': ip
        }
        return proxies


# 飞书
class Feishu:
    # 飞书 机器人推送
    def feishu_send_message(self, text, WEBHOOK_URL=''):
        if WEBHOOK_URL == '':
            WEBHOOK_URL = config_dict['feishu']['fs_url']

        data = {
            "timestamp": int(time.time()),
            "msg_type": "text",
            "content": {"text": text},
        }
        res = HttpJike.post(url=WEBHOOK_URL, data=data)
        if res.status_code == 200:
            print(res.json)

    # 飞书 应用token
    def feishu_get_token(self, app_id, app_secret):
        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            post_data = {"app_id": app_id,
                         "app_secret": app_secret}
            res = HttpJike.post(url=url, data=post_data)
            if res.status_code == 200:
                tenant_access_token = res.json["tenant_access_token"]
                return tenant_access_token
        except:
            pass

    # 飞书 批量新增
    def feishu_add_more_view(self, app_token, table_id, records, tenant_access_token):
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create'

        headers = {
            'Authorization': f"Bearer {tenant_access_token}",
            'Content-Type': "application/json; charset=utf-8",
        }
        data = {
            "records": records
        }
        res = HttpJike.post(url=url, headers=headers, data=data)
        if res.status_code == 200:
            data_data = res.json
            code = data_data.get('code')
            msg = data_data.get('msg')
            data = data_data.get('data')
            if code == 0 and msg == "success" and data:
                return 1


# 时间
class TimeJike:
    @staticmethod
    def zero_clock(day=0):
        t2 = time.time()
        a = time.localtime(t2)  # 时间戳 > 9元组
        y_m_d = f'{a[0]}-{a[1]}-{a[2]}'  # 9元组 > 格式化 2020-11-4
        t_t = time.strptime(y_m_d, '%Y-%m-%d')  # 再转 > 9元组
        t = int(int(time.mktime(t_t)) - 86400 * day)
        return t

    # 时间 -> 获取现在是今天的第多少秒
    @staticmethod
    def today_seconds():
        t2 = time.time()  # 当前时间戳
        a = time.localtime(t2)  # 时间戳 > 9元组
        y_m_d = f'{a[0]}-{a[1]}-{a[2]}'  # 9元组 > 格式化 2020-11-4
        t_t = time.strptime(y_m_d, '%Y-%m-%d')  # 再转 > 9元组
        t = int(int(time.mktime(t_t)))
        return int(t2 - t)

    # 时间 -> 获取这个小时开始时间戳
    @staticmethod
    def hours_start_time(hours=0):
        """
        :param hours: 几个小时前
        :return: 时间戳
        """
        t2 = time.time()
        a = time.localtime(t2)  # 时间戳 > 9元组
        y_m_d = f'{a[0]}-{a[1]}-{a[2]} {a[3]}:{0}'  # 9元组 > 格式化 2020-11-4
        y_m_d_s = time.strptime(y_m_d, '%Y-%m-%d %H:%M')  # 再转 > 9元组
        t = int(time.mktime(y_m_d_s)) - hours * 3600
        return t

    # 时间 -> 返回星期几 str
    @staticmethod
    def week(t=None):
        """
        :param t: 时间戳 默认=今日
        :return: 周几
        """
        if t is None:
            t = int(time.time())
        t_s0 = int(time.strftime("%w", time.localtime(t)))  # 获取今天星期数
        if t_s0 == 1:
            t_s = "周一"
        elif t_s0 == 2:
            t_s = "周二"
        elif t_s0 == 3:
            t_s = "周三"
        elif t_s0 == 4:
            t_s = "周四"
        elif t_s0 == 5:
            t_s = "周五"
        elif t_s0 == 6:
            t_s = "周六"
        else:
            t_s = "周日"
        return t_s

    # 时间 -> 20220404
    @staticmethod
    def ymd(t=None):
        if t is None:
            t = int(time.time())
        return time.strftime("%Y%m%d", time.localtime(t))

    # 时间 -> 2022-04-04
    @staticmethod
    def y_m_d(t=None):
        if t is None:
            t = int(time.time())
        return time.strftime("%Y-%m-%d", time.localtime(t))

    # 时间 -> 2022-04-04 13:59:49
    @staticmethod
    def y_m_d__h_m_s(t=None):
        if t is None:
            t = int(time.time())
        return time.strftime("%Y-%m-%d %X", time.localtime(t))

    # 时间 -> 小时:13
    @staticmethod
    def hour(t=None):
        if t is None:
            t = int(time.time())
        return int(time.strftime("%H", time.localtime(t)))

    # 时间 -> 分钟:13
    @staticmethod
    def minute(t=None):
        if t is None:
            t = int(time.time())
        return int(time.strftime("%M", time.localtime(t)))

    # 时间 -> 时,分,秒 int
    @staticmethod
    def hour_minute_seconds(timestamp=int(time.time())):
        """
        返回当前 时,分,秒 int
        :param timestamp: 时间戳
        :return: 时 分 秒
        """
        HOUR = timestamp // (60 * 60)
        MINUT = (timestamp - (HOUR * (60 * 60))) // 60
        SECONDS = timestamp - ((HOUR * (60 * 60)) + (MINUT * 60))
        return HOUR, MINUT, SECONDS


# 文本
class TextJike:
    # 清除字符串渣滓
    @staticmethod
    def word_change(xxx):
        """
        适用于mysql
        :param xxx:
        :return:
        """
        if xxx is not None:
            xxx = str(xxx)
            xxx = str(xxx).replace("'", " ")
            xxx = str(xxx).replace('"', ' ')
            xxx = str(xxx).replace('◕', ' ')
            xxx = str(xxx).replace('\\', ' ')
            xxx = str(xxx).replace('\n', ' ')
            xxx = str(xxx).replace('\r', ' ')
            xxx = str(xxx).replace('\t', ' ')
            xxx = str(xxx).replace('\f', ' ')
            xxx = str(xxx).replace('\v', ' ')
        return xxx

    # 字符串修改 --> 只要数字
    @staticmethod
    def only_number(xxx):
        try:
            if xxx:
                return int(re.sub('\D+', '', xxx))
        except:
            pass

    # 字符串修改 --> 全是数字
    @staticmethod
    def is_all_number(input_string):
        try:
            float(input_string)  # 尝试将字符串转换为浮点数
            return True  # 如果成功转换，说明字符串都是数字
        except ValueError:
            return False  # 如果转换失败，说明字符串包含非数字字符

    # 字符串修改 --> 去除数字
    @staticmethod
    def clear_number(xxx):
        try:
            if xxx:
                return int(re.sub('\d+', '', xxx))
        except:
            pass

    # 字符串修改 --> 去除html符号
    @staticmethod
    def clear_html(xxx):
        try:
            if xxx:
                return re.sub(pattern='<.+?>', repl='', string=xxx)
        except:
            pass

    # 字符串100万 --> 1000000
    @staticmethod
    def str_num_to_int(xxx):
        xxx = xxx.replace(' ', '')  # 去除空格
        if '万' in xxx:
            xxx_num = float(xxx[:-1])
            ret_xxx = xxx_num * 10000

        elif '亿' in xxx:
            xxx_num = float(xxx[:-1])
            ret_xxx = xxx_num * 100000000

        else:
            ret_xxx = xxx
        return ret_xxx


# 数据
class DataJike:
    # 列表_多个字典_排序  -----↓↓↓↓-----列表 字典 集合 -----↓↓↓↓-----
    @staticmethod
    def list_dicts_order(list_xxx, order_by, positive_or_negative=True):
        if list_xxx:
            return sorted(list_xxx, key=lambda x: x[order_by], reverse=positive_or_negative)

    # 列表 -> 变字典 自动计算 排序
    @staticmethod
    def dicts_order_auto(list_xxx, order_by=True):
        if list_xxx:
            ret_dict = {}
            for i in list_xxx:
                if i in ret_dict:
                    ret_dict[i] += 1
                else:
                    ret_dict[i] = 1
            lis = sorted(ret_dict.items(), key=lambda i: i[1], reverse=order_by)
            return lis

    # 两个列表操作 差集
    @staticmethod
    def diff(l1, l2):
        return list(set(l1).difference(set(l2)))

    # 平均分块
    @staticmethod
    def list_avg_split(list_data, each_num):
        all_list = []
        for i in range(0, len(list_data), each_num):
            all_list.append(list_data[i:i + each_num])
        return all_list

    # 字典合并
    @staticmethod
    def dict_marge(*dicts):
        result = {}
        for d in dicts:
            result.update(d)
        return result

    # 简单字典 返回最大键  {1: 82.0, 2: 18.0} --> max:1
    @staticmethod
    def dict_max(dict_data):
        result_max = max(dict_data, key=lambda x: dict_data[x])
        return result_max

    # 列表 平均值
    @staticmethod
    def list_avg(list_data):
        if len(list_data) < 1:
            return None
        else:
            return int(sum(list_data) / len(list_data))

    # 列表 去除指定元素
    @staticmethod
    def list_remove_by(list_old, removes=None):
        new_list = []
        if list_old and removes and type(removes) == list:
            removes = list(set(removes))  # 去重
            for i in list_old:
                if i not in removes:
                    new_list.append(i)
        return new_list

    # 列表 中位数
    @staticmethod
    def list_median(data):
        data = sorted(data)
        size = len(data)
        if size % 2 == 0:  # 判断列表长度为偶数
            median = (data[size // 2] + data[size // 2 - 1]) / 2
            data[0] = median
        if size % 2 == 1:  # 判断列表长度为奇数
            median = data[(size - 1) // 2]
            data[0] = median
        return data[0]

    # 文件 获取文件夹下所有文件信息
    @staticmethod
    def os_file_child_info(directory_path):
        all_file_info = []
        file_list = os.listdir(directory_path)

        # 遍历文件列表，获取每个文件的详细信息
        for file_name in file_list:
            file_path = os.path.join(directory_path, file_name)

            # 获取文件信息
            file_info = os.stat(file_path)

            # 打印文件信息（示例，你可以根据需求选择性输出）
            all_file_info.append({
                'name': file_name,
                'size': file_info.st_size,
                'last_up': int(file_info.st_mtime),
                'created': int(file_info.st_ctime),
                'is_directory': os.path.isdir(file_path),
                'is_file': os.path.isfile(file_path),
            })
        return all_file_info

    # dict 多重数据结构提取web链接
    def dict_web_url(self, data):
        links = []

        if isinstance(data, dict):
            for value in data.values():
                links.extend(self.dict_web_url(value))
        elif isinstance(data, list):
            for item in data:
                links.extend(self.dict_web_url(item))
        elif isinstance(data, str):
            # 使用正则表达式查找所有链接
            found_links = re.findall(r'https?://\S+', data)
            links.extend(found_links)

        return links


# 采集
class SpiderJike:
    # >>>>----------------       spider_func         ----------------<<<<<
    # ai api2d 余额查询
    @staticmethod
    def ai_api2d_token_count():
        url = "https://oa.api2d.net/dashboard/billing/credit_grants"
        token = config_dict['api2d']['token1']
        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        res = HttpJike.get(url=url, headers=headers)
        if res.status_code == 200:
            data_data = res.json
            token_count = data_data['total_granted']
            return token_count

    # 百度IP定位
    @staticmethod
    def api_baidu_ip(ip='60.12.139.18'):
        """
        http://api.map.baidu.com/location/ip?ak=您的AK&ip=您的IP&coor=bd09ll //HTTP协议
        https://api.map.baidu.com/location/ip?ak=您的AK&ip=您的IP&coor=bd09ll //HTTPS协议

        --参数
        ak    密钥   string    必填    E4jYvwZbl9slCjUALZpnl1xawvoIAlrP
        ip          string    可选
        sn    校验   string    可选
        coor  详细请求  string  可选
        -coor不出现、或为空：百度墨卡托坐标，即百度米制坐标
        -coor = bd09ll：百度经纬度坐标，在国测局坐标基础之上二次加密而来
        -coor = gcj02：国测局02坐标，在原始GPS坐标基础上，按照国家测绘行业统一要求，加密后的坐标
        """
        city = '北京'
        province = '北京'

        try:
            ak = 'E4jYvwZbl9slCjUALZpnl1xawvoIAlrP'
            url = f'http://api.map.baidu.com/location/ip?ak={ak}&ip={ip}&coor=bd09ll'
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)'
            }
            response = HttpJike.get(url=url, headers=headers)
            if response.status_code == 200:
                data_data = response.json
                content = data_data.get('content')
                status = data_data.get('status')
                if content is not None and status == 0:
                    address_detail = content.get('address_detail')
                    if address_detail is not None:
                        city_data = address_detail.get('city')
                        province_data = address_detail.get('province')

                        # 省会 城市 判断
                        if len(province_data) > 0:
                            province = province_data
                            if len(city_data) > 0:
                                city = city_data
                            else:
                                city = province
                        else:
                            pass
                        print(f'省会:{province},城市:{city}')
                        return data_data
                    else:
                        pass
                else:
                    pass
            else:
                pass
        except:
            pass
        return [province, city]

    # 和风天气
    @staticmethod
    def api_qweather(location):
        key = 'fd9e6c4c11254fe19f2b4f46c3653397'
        url = f'https://geoapi.qweather.com/v2/city/lookup?&location={location}&key={key}'
        response = HttpJike.get(url=url)
        if response.status_code == 200:
            j = response.json
            id = j['location'][0]['id']

            # 二,根据城市id 获取城市天气
            url = f'https://devapi.qweather.com/v7/weather/now?location={id}&key={key}'
            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
            }
            response = HttpJike.get(url=url)
            if response.status_code == 200:
                weather_now = response.json
                t_s = time.strftime("%X", time.localtime(time.time()))

                location = f'{location}'
                t_s = f'{t_s}'
                temp = f"{weather_now['now']['temp']}℃"  # 当前温度
                feelsLike = f"{weather_now['now']['feelsLike']}℃"  # 体感温度
                text_now = f"{weather_now['now']['text']}"  # 当前天气
                feng = f"{weather_now['now']['windDir']}{weather_now['now']['windScale']}级 {weather_now['now']['windSpeed']}公里/小时"  # 风
                humidity = f"{weather_now['now']['humidity']}%"  # 湿度
                precip = f"{weather_now['now']['precip']}毫米"  # 降水量值
                pressure = f"{weather_now['now']['pressure']}百帕"  # 大气压强
                vis = f"{weather_now['now']['vis']}公里"  # 能见度值
                cloud = f"{weather_now['now']['cloud']}%"  # 当前云量
                return {'location': location,
                        't_s': t_s,
                        'temp': temp,
                        'feelsLike': feelsLike,
                        'text_now': text_now,
                        'feng': feng,
                        'humidity': humidity,
                        'precip': precip,
                        'pressure': pressure,
                        'vis': vis,
                        'cloud': cloud,
                        }

    # 发送QQ邮件
    @staticmethod
    def send_email(title, text):
        """
        pip install PyEmail
        pip install email
        pip install smtplib
        """

        # 发送邮件配置
        import smtplib
        from email.mime.text import MIMEText
        # email 用于构建邮件内容
        from email.header import Header

        from_addr = '1079146598@qq.com'  # 发信方邮箱
        password = 'ouacnpxmtbavjecc'  # 收信方授权码
        to_addr = '3084447185@qq.com'  # 收信方邮箱
        # to_addr = '1048995287@qq.com'  # 王伟南

        smtp_server = 'smtp.qq.com'  # 发信服务器

        # ，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
        msg = MIMEText(text, 'plain', 'utf-8')  # 正文内容

        # 邮件头信息
        msg['From'] = Header(from_addr)
        msg['To'] = Header(to_addr)
        msg['Subject'] = Header(title)

        server = smtplib.SMTP_SSL(host=smtp_server)  # 开启发信服务
        server.connect(smtp_server, 465)  # 加密传输

        server.login(from_addr, password)  # 登录发信邮箱
        server.sendmail(from_addr, to_addr, msg.as_string())  # 发送邮件
        server.quit()  # 关闭服务器

    # fr1997 web 请求ip
    @staticmethod
    def api_fr1997_ip():
        url = 'https://dv.fr1997.cn/test_ip'
        res = HttpJike.get(url=url, proxies=HttpJike.proxies_choose(1))
        if res.status_code == 200:
            return res.json['test_ip']

    # 抖音视频数据解析
    @staticmethod
    def douyin_video_response(res_data, tp='django_video_info'):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}

        # 是否存在
        if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(res_data):
            base_ret_data['is_alive'] = 0
            return base_ret_data

        # 获取视频类型
        aweme_type = res_data["aweme_type"]
        if aweme_type == 68:
            base_ret_data['aweme_type'] = 68
            return base_ret_data

        like_num = res_data["statistics"]["digg_count"]
        forward_num = res_data["statistics"]["share_count"]
        comment_num = res_data["statistics"]["comment_count"]
        collect_count = res_data["statistics"]["collect_count"]

        # 播放时长
        try:
            release_time = round(int(res_data['video']['duration']) / 1000)  # 视频长度
        except:
            release_time = 0

        # 昵称
        nickname = res_data["author"]["nickname"]

        # 描述
        describe = res_data["author"]["signature"]

        # 标题
        desc = res_data["desc"]

        # 封面
        try:
            cover_img = res_data['video']['cover']['url_list'][0]
        except:
            cover_img = ''

        # 视频 vid
        try:
            v_id = res_data['video']['vid']
        except:
            v_id = res_data['video']['play_addr']['uri']

        # 视频创建时间比较特殊，如果没有创建时间，默认一个值
        create_time = res_data.get('create_time', config_dict['douyin']['douyin_video_create_time'])

        # sec_uid
        sec_uid = res_data['author']['sec_uid']

        # user_id
        user_id = res_data['author']['uid']

        # 视频下载地址
        try:
            download_addr_url_list = res_data['video']['download_addr']['url_list']
        except:
            download_addr_url_list = []

        # mp3 url
        try:
            mp3_url_list = res_data['music']['play_url']['url_list']

            if '.mp3' in res_data['music']['play_url']['url_list'][0]:
                pass
            else:
                mp3_url_list = []
        except:
            mp3_url_list = []

        # author_head
        author_head = res_data['author']['avatar_thumb']['url_list'][0]
        base_ret_data['video_id'] = res_data["aweme_id"]
        base_ret_data['v_id'] = v_id
        base_ret_data['title'] = desc
        base_ret_data['video_cover'] = cover_img

        base_ret_data['play_num'] = 0
        base_ret_data['good_count'] = like_num
        base_ret_data['comment_count'] = comment_num
        base_ret_data['share_count'] = forward_num
        base_ret_data['collect_count'] = collect_count
        base_ret_data['user_id'] = user_id

        base_ret_data['update_time'] = int(time.time()),
        base_ret_data['create_date'] = create_time
        base_ret_data['release_time'] = release_time
        base_ret_data['nickname'] = nickname
        base_ret_data['author_head'] = author_head
        base_ret_data['describe'] = describe

        base_ret_data['download_addr_url_list'] = download_addr_url_list
        base_ret_data['mp3_url_list'] = mp3_url_list

        if tp == 'django_video_info':
            return {
                "video_id": res_data["aweme_id"],
                "v_id": v_id,
                'video_description': desc,
                'video_cover': cover_img,

                'play_num': 0,  # 播放量
                'good_count': like_num,  # 点赞量
                'comment_count': comment_num,  # 评论量
                'share_count': forward_num,  # 分享数
                'collect_count': collect_count,  # 收藏数

                'update_time': int(time.time()),
                'create_date': create_time,
                'video_time_count': release_time,  # 视频时常
                'release_time': release_time,  # 视频时常
                'describe': describe,

                'nickname': nickname,
                'sec_uid': sec_uid,
                'user_id': user_id,
                'author_head': author_head,
            }
        elif tp == 'video_info':
            try:
                base_ret_data['follower_count'] = res_data['author']['follower_count']
            except:
                base_ret_data['follower_count'] = 0
            base_ret_data['sec_uid'] = res_data['author']['sec_uid']
            return base_ret_data
        elif tp == 'wav':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 改版 bit_rate中有很多链接，找到&cs=2为标准音频链接
            bit_rate = res_data['video']['bit_rate'][0]  # 保底一个
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 获取新的
            bit_rate = res_data['video']['bit_rate']
            for bt in bit_rate:
                wav_url_list = bt['play_addr']['url_list']
                if wav_url_list:
                    if '&cs=2' in wav_url_list[0]:
                        base_ret_data['wav_size'] = bt['bit_rate']
                        base_ret_data['wav_url'] = bt['play_addr']['url_list']

            return base_ret_data
        elif tp == 'wav_small':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']
            return base_ret_data
        else:
            return base_ret_data


# 抖音
class DouyinJike:
    # 抖音视频id短链
    def short_url(self, url):
        return HttpJike.get(url=url).ret_url

    # 抖音 链接 -> video_id
    def get_video_id(self, video_url, tp=1):
        # 最终 https://www.douy...in.com/video/7218785833724185917
        if '://v.douyin' in video_url:
            pat = re.compile(r'https://v.douyin.com/[-_a-zA-Z0-9]{5,10}/')
            res = pat.findall(video_url)
            if res:
                v_url = self.get_video_id(self.short_url(res[0]))
                return v_url
        if 'www.douyin.com' in video_url and 'modal_id' in video_url:
            url1 = video_url.split('modal_id=')
            if url1:
                url2 = url1[-1]
                video_ids = []
                for i in url2:
                    if i in '1234567890':
                        video_ids.append(i)
                    else:
                        break
                video_id = ''.join(video_ids)
                return video_id
        if '.douyin.com/video' in video_url:
            video_idstr1 = video_url.split('/')
            if len(video_url) >= 5:
                video_idstr2 = video_idstr1[4]
                # 去除末尾杂项
                video_ids = []
                for i in video_idstr2:
                    if i in '1234567890':
                        video_ids.append(i)
                    else:
                        break
                video_id = ''.join(video_ids)
                return video_id
        if '/www.douyin.com/user/' in video_url and 'modal_id' in video_url:  # 其他
            video_idstr1 = video_url.split('modal_id=')[-1]
            video_ids = []
            for i in video_idstr1:
                if i in '1234567890':
                    video_ids.append(i)
                else:
                    break
            video_id = ''.join(video_ids)
            return video_id
        if 'www.iesdouyin.com/share/video/' in video_url:
            video_id = video_url.split('www.iesdouyin.com/share/video/')[-1].split('/?')[0]
            return video_id

        # 强制识别 可能出现问题(强制识别 视频id为19位数字)
        pat = re.compile(r'\d{19}')
        res = pat.findall(video_url)
        if res:
            return res[0]

    # 抖音 链接 -> sec_uid
    def get_douyin_sec_uid(self, user_url, tp=1):  # https://v.douyin.com/i3TDetD
        try:
            if 'www.douyin.com' in user_url and 'MS4' in user_url:
                sec_uid = user_url.split('https://www.douyin.com/user/')[-1].split('?')[0]
                return sec_uid

            if '://v.douyin.com':
                url_pattern = r'https://v\.douyin\.com/\w+/'
                matches = re.findall(url_pattern, user_url)
                if matches:
                    user_url = matches[0]
                res = HttpJike.get(url=user_url).ret_url
                sec_uid = res.split('https://www.iesdouyin.com/share/user/')[-1].split('?')[0]
                return sec_uid
        except:
            pass

    # 抖音搜索 20231025 数据解析
    @staticmethod
    def douyin_search_data_20231025(keyword, data_data, res_page):
        status_code = data_data.get('status_code')
        data = data_data.get('data')
        if status_code == 0 and data:
            data_list = []
            for index, v in enumerate(data):
                aweme_info = v['aweme_info']

                # 如何判断选集？ mixId？
                mixId = None
                mixInfo = aweme_info.get('mix_info')
                if mixInfo:
                    mixId = mixInfo.get('mix_id')

                # 播放时长
                try:
                    release_time = round(int(aweme_info['video']['duration']) / 1000)  # 视频长度
                except:
                    release_time = 0

                author = aweme_info['author']

                # 用户的介绍
                signature = author.get('signature', '')

                # unique_id
                unique_id = author.get('unique_id', '')
                if len(unique_id) == 0:
                    unique_id = author.get('short_id', '')
                data_dict = {
                    'keyword': keyword,
                    'mixId': mixId,
                    'index': index,
                    'desc': aweme_info['desc'],
                    'aweme_id': aweme_info['aweme_id'],
                    'sec_uid': author['sec_uid'],
                    'user_id': author['uid'],
                    'unique_id': unique_id,
                    'enterprise_verify_reason': author.get('enterprise_verify_reason', ''),
                    'nickname': author['nickname'],
                    'followers_count': author['follower_count'],

                    'createTime': aweme_info['create_time'],
                    'like_count': aweme_info['statistics']['digg_count'],  # 电赞
                    'comment_num': aweme_info['statistics']['comment_count'],  # 评论
                    'share_count': aweme_info['statistics']['share_count'],  # 转发
                    'collect_count': aweme_info['statistics']['collect_count'],  # 收藏

                    'search_time': int(time.time()),
                    'source': 'app_dj_videopc',

                    'cover': aweme_info['video']['cover']['url_list'][0],  # 封面
                    'author_head': author['avatar_thumb']['url_list'][0],
                    'author_type': '其他',

                    # 至关重要的vid
                    'v_id': aweme_info['video']['play_addr']['uri'],
                    'p': res_page,  # 页数

                    # 视频时长
                    'release_time': release_time,

                    # 介绍
                    'signature': signature,
                }

                data_list.append(data_dict)
            return {'code': 200, 'msg': 'ok', 'data_list': data_list}
        else:
            return {'code': 500, 'msg': '没有数据'}

    # 缓存es 抖音关键词搜索视频
    @staticmethod
    def douyin_keyword_info_save(sava_data, source):
        sava_es_data = []
        for v in sava_data:
            keyword = v['keyword']
            index = v['index']
            aweme_id = v['aweme_id']
            desc = v['desc']
            sec_uid = v['sec_uid']
            nickname = v['nickname']
            createTime = v.get('createTime')
            like_count = v.get('like_count')
            mixId = v.get('mixId')
            v_id = v.get('v_id')
            sava_es_data.append({"index": {"_id": f"{keyword}__{index}"}})
            data_dict = {
                'aweme_id': aweme_id,
                'mixId': mixId,
                'index': index,  # 从1开始
                'desc': desc,
                'sec_uid': sec_uid,
                'nickname': nickname,
                'keyword': keyword,
                'createTime': createTime,
                'like_count': like_count,
                'search_time': int(time.time()),
                'source': source,

                # 至关重要的vid
                'v_id': v_id,
            }
            sava_es_data.append(data_dict)
        return sava_es_data, 'douyin_search_keyword_data'

    # 【api】 用户详情
    def api_douyin_user(self, sec_uid):
        cookies = mode_pro.ttwid_cookie_tt(get_cache=1)
        headers = {
            "authority": "www.douyin.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/plain, */*",
            "user-agent": config_dict['base_ua'],
            "referer": "https://www.douy" + "in.com/user/MS4wLjABAAAAM5BxLLRhN2jrzttuOUI3LEmFClP8t6dp0bf67Oi3deE",
            "accept-language": "zh-CN,zh;q=0.9",
            'cookie': f'msToken={mode_pro.get_douyin_token(107)};odin_tt=;passport_csrf_token=1;{random.choice(cookies)}'
        }
        device_id = ''.join(random.choice("0123456789") for _ in range(16))
        url = f"https://www.douyin.com/aweme/v1/web/user/profile/other/?sec_user_id={sec_uid}&device_id={device_id}&aid=1128"
        url = mode_pro.get_xbogus_new_gbk(url, config_dict['base_ua'])
        response = HttpJike.get(url=url, headers=headers, proxies=HttpJike.proxies_choose())
        if response.status_code == 200:
            data_data = response.json
            user_detail = data_data.get('user')

            data_json = self.analysis_douyin_user(user_detail)  # 数据获取
            return data_json

    # 【api】 视频详情
    def api_douyin_video(self, video_id, use_proxies=1, res_tp='video_info'):
        cookies = mode_pro.ttwid_cookie_tt(get_cache=1)
        headers = {
            "authority": "www.douyin.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "accept": "application/json, text/plain, */*",
            "user-agent": config_dict['base_ua'],
            "referer": "https://www.douy" + "in.com/user/MS4wLjABAAAAM5BxLLRhN2jrzttuOUI3LEmFClP8t6dp0bf67Oi3deE",
            "accept-language": "zh-CN,zh;q=0.9",
            'cookie': f'msToken={mode_pro.get_douyin_token(107)};odin_tt=;passport_csrf_token=1;{random.choice(cookies)}'
        }

        url = f'https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={video_id}&pc_client_type=1&version_code=190500&version_name=19.5.0'
        url = mode_pro.get_xbogus_new_gbk(url, config_dict['base_ua'])
        try:
            if use_proxies:
                response = HttpJike.get(url=url, headers=headers, proxies=HttpJike.proxies_choose())
            else:
                response = HttpJike.get(url=url, headers=headers)
            if response.status_code == 200:
                data_data = response.json

                # 是否存在
                if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(data_data):
                    return {'aweme_type': 1, 'is_alive': 0, 'err': 'del'}

                video_detail = data_data['aweme_detail']
                data_json = mode_spider.douyin_video_response(video_detail, tp=res_tp)  # 数据获取
                return data_json
        except Exception as E:
            return {'aweme_type': 1, 'is_alive': 0, 'err': E}

    # 【api】 用户主页视频列表 amemv版本
    def user_video_list_mv(self, sec_uid, max_cursor='0', timeout=30):
        ret_data = {
            'list': []
        }
        headers = {
            'authority': 'www.douyin.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.douyin.com',
            "user-agent": config_dict['base_ua'],
        }
        params = {
            "sec_uid": sec_uid,
            'aid': '1128',
            "count": 21,
            "max_cursor": max_cursor,  # 需要 max_cursor 跳转到下一页
        }
        try:
            response = requests.get(f'https://www.amemv.com/web/api/v2/aweme/post/', params=params,
                                    headers=headers, proxies=HttpJike.proxies_choose(), timeout=timeout)
            if response.status_code == 200:
                data_data = response.json()
                max_cursor = data_data.get('max_cursor')
                has_more = data_data.get('has_more')
                ret_data['max_cursor'] = max_cursor
                ret_data['has_more'] = has_more
                status_code = data_data.get('status_code')
                if status_code == 0:
                    aweme_list = data_data["aweme_list"]
                    for v in aweme_list:
                        aweme_id = v['aweme_id']
                        author_info = v.get('author', {})
                        nickname = author_info.get('nickname', '')
                        uid = author_info.get('uid', '')
                        sec_uid = author_info.get('sec_uid', '')

                        statistics = v.get('statistics', {})
                        digg_count = statistics.get('digg_count', 0)
                        share_count = statistics.get('share_count', 0)
                        # comment_count = statistics.get('comment_count', 0)  # 没有
                        # collect_count = statistics.get('collect_count', 0)  # 没有
                        # create_time = statistics.get('create_time', 0)  # 没有

                        video_info = v.get('video', {})
                        release_time = round(int(video_info.get('duration', 0)) / 1000)
                        vid = video_info.get('vid', '')

                        ret_data['list'].append({
                            'aweme_id': aweme_id,
                            'aweme_type': v['aweme_type'],
                            'title': v['desc'],
                            'digg_count': digg_count,
                            'share_count': share_count,

                            'nickname': nickname,
                            'sec_uid': sec_uid,
                            'uid': uid,

                            'release_time': release_time,
                            'vid': vid,
                        })
        except:
            pass

        return ret_data

    # api 抖音用户 来之于django
    def api_douyin_user_info(self, sec_uid):
        url = "http://pythonapi.yinliu.club/douyin_users_info/"
        data = {
            'token': config_dict['token']['django'],
            'user_ids': sec_uid,
        }
        res = requests.post(url=url, data=data)
        return res.json()

    # 抖音作品类型判断
    def field_aweme_type(self, aweme_type):
        if type(aweme_type) == int:
            return aweme_type
        else:
            return 0

    # 【数据解析】 用户主页列表
    def analysis_douyin_video_list(self, aweme_list):
        save_data = []
        for v in aweme_list:
            author = v['author']

            # 链接，
            sec_uid = author['sec_uid']

            # 链接，
            aweme_id = v['aweme_id']

            # 类型
            aweme_type = self.field_aweme_type(v.get('aweme_type', 0))

            # 点赞数
            digg_count = v['statistics']['digg_count']

            # 评论数
            comment_count = v['statistics']['comment_count']

            # 评论数
            collect_count = v['statistics']['collect_count']

            # 评论数
            share_count = v['statistics']['share_count']

            release_time = round(int(v['duration']) / 1000)  # 视频长度

            # 标题
            desc = mode_text.word_change(v['desc'])
            if len(str(desc)) < 0:
                desc = ''

            # 发布时间。
            create_time = v['create_time']
            create_time_str = time.strftime("%Y-%m-%d %X", time.localtime(create_time))  # 2021-04-12 14:36:20
            save_data.append({
                'sec_uid': sec_uid,
                'aweme_id': aweme_id,
                'aweme_type': aweme_type,
                'title': desc,

                'digg_count': digg_count,
                'comment_count': comment_count,
                'collect_count': collect_count,
                'share_count': share_count,
                'release_time': release_time,
                'create_time': create_time,
                'create_time_str': create_time_str,
            })
        return save_data

    # 【数据解析】 用户详情
    def analysis_douyin_user(self, res_data):
        aweme_count = res_data['aweme_count']
        follower_count = res_data['follower_count']
        nickname = res_data['nickname']
        unique_id = res_data.get('unique_id', '')
        if len(unique_id) == 0:
            unique_id = res_data.get('short_id', '')
        user_id = res_data['uid']
        total_favorited = res_data['total_favorited']
        author_head = res_data['avatar_168x168']['url_list'][0]
        introduction = mode_text.word_change(res_data['signature'])
        # 用户类型 1=个人  2=黄V  3=蓝V  4=注销  5=未知
        user_type = 5
        organization = ''
        custom_verify = res_data['custom_verify']
        enterprise_verify_reason = res_data.get('enterprise_verify_reason', '')
        if len(custom_verify) > 0:
            user_type = 2
            organization = custom_verify
        if len(enterprise_verify_reason) > 0:
            user_type = 3
            organization = enterprise_verify_reason

        return {
            'nickname': nickname,
            'unique_id': unique_id,
            'user_id': user_id,
            'introduction': introduction,
            'video_count': aweme_count,
            'follower_count': follower_count,
            'good_count': total_favorited,
            'user_type': user_type,
            'organization': organization,
            'author_head': author_head,
            'user_update_date': int(time.time()),
        }

    # 【数据解析】 视频详情
    def douyin_video_response(self, res_data, tp='django_video_info'):
        base_ret_data = {'aweme_type': 1, 'is_alive': 1}

        # 是否存在
        if '因作品权限或已被删除，无法观看，去看看其他作品吧' in str(res_data):
            base_ret_data['is_alive'] = 0
            return base_ret_data

        # 获取视频类型
        aweme_type = res_data["aweme_type"]
        if aweme_type == 68:
            base_ret_data['aweme_type'] = 68
            return base_ret_data

        like_num = res_data["statistics"]["digg_count"]
        forward_num = res_data["statistics"]["share_count"]
        comment_num = res_data["statistics"]["comment_count"]
        collect_count = res_data["statistics"]["collect_count"]

        # 播放时长
        try:
            release_time = round(int(res_data['video']['duration']) / 1000)  # 视频长度
        except:
            release_time = 0

        # 昵称
        nickname = res_data["author"]["nickname"]

        # 描述
        describe = res_data["author"]["signature"]

        # 标题
        desc = res_data["desc"]

        # 封面
        try:
            cover_img = res_data['video']['cover']['url_list'][0]
        except:
            cover_img = ''

        # 视频 vid
        try:
            v_id = res_data['video']['vid']
        except:
            v_id = res_data['video']['play_addr']['uri']

        # 视频创建时间比较特殊，如果没有创建时间，默认一个值
        create_time = res_data.get('create_time', config_dict['douyin']['douyin_video_create_time'])

        # sec_uid
        sec_uid = res_data['author']['sec_uid']

        # user_id
        user_id = res_data['author']['uid']

        # author_head
        author_head = res_data['author']['avatar_thumb']['url_list'][0]
        base_ret_data['video_id'] = res_data["aweme_id"]
        base_ret_data['v_id'] = v_id
        base_ret_data['title'] = desc
        base_ret_data['video_cover'] = cover_img

        base_ret_data['play_num'] = 0
        base_ret_data['good_count'] = like_num
        base_ret_data['comment_count'] = comment_num
        base_ret_data['share_count'] = forward_num
        base_ret_data['collect_count'] = collect_count

        base_ret_data['update_time'] = int(time.time()),
        base_ret_data['create_date'] = create_time
        base_ret_data['release_time'] = release_time
        base_ret_data['nickname'] = nickname
        base_ret_data['describe'] = describe

        if tp == 'django_video_info':
            return {
                "video_id": res_data["aweme_id"],
                "v_id": v_id,
                'video_description': desc,
                'video_cover': cover_img,

                'play_num': 0,  # 播放量
                'good_count': like_num,  # 点赞量
                'comment_count': comment_num,  # 评论量
                'share_count': forward_num,  # 分享数
                'collect_count': collect_count,  # 收藏数

                'update_time': int(time.time()),
                'create_date': create_time,
                'video_time_count': release_time,  # 视频时常
                'release_time': release_time,  # 视频时常
                'describe': describe,

                'nickname': nickname,
                'sec_uid': sec_uid,
                'user_id': user_id,
                'author_head': author_head,
            }
        elif tp == 'video_info':
            base_ret_data['follower_count'] = res_data['author']['follower_count']
            base_ret_data['sec_uid'] = res_data['author']['sec_uid']
            return base_ret_data
        elif tp == 'wav':
            # 获取音频
            bit_rate = res_data['video']['bit_rate'][-1]
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 改版 bit_rate中有很多链接，找到&cs=2为标准音频链接
            bit_rate = res_data['video']['bit_rate'][0]  # 保底一个
            base_ret_data['sec_uid'] = sec_uid
            base_ret_data['wav_size'] = bit_rate['bit_rate']
            base_ret_data['wav_url'] = bit_rate['play_addr']['url_list']

            # 获取新的
            bit_rate = res_data['video']['bit_rate']
            for bt in bit_rate:
                wav_url_list = bt['play_addr']['url_list']
                if wav_url_list:
                    if '&cs=2' in wav_url_list[0]:
                        base_ret_data['wav_size'] = bt['bit_rate']
                        base_ret_data['wav_url'] = bt['play_addr']['url_list']
            return base_ret_data
        else:
            return base_ret_data

    # 获取ttwid
    @staticmethod
    def get_ttwid_20240111():
        result = None
        try:
            json = {"region": "cn", "aid": 1768, "needFid": False, "service": "www.ixigua.com",
                    "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": True}
            r = requests.post("https://ttwid.bytedance.com/ttwid/union/register/", json=json,
                              proxies=HttpJike.proxies_choose())
            cookie = r.headers['Set-Cookie']
            match = re.search("ttwid=([^;]+)", cookie)
            if match:
                result = match.group(1)
            else:
                result = ""
        except:
            print("err ttwid_cookie获取失败")
        if result:
            return result


# django
class DjangoJike:
    # 配置
    @staticmethod
    def django_config():
        sc = 'status_code'  # 返回码
        msg = 'message'  # 返回消息

        return {
            "status_codes": {
                "code_200": {sc: 200, msg: '成功-200'},
                "code_400": {sc: 400, msg: '错误-400'},
                "code_500": {sc: 500, msg: '错误-500'},
                "code_xxx": {sc: 555, msg: '错误-xxx'},
                "code_token": {sc: 556, msg: '错误-token'},
                "code_method": {sc: 557, msg: '错误-method'},
            },
            "save_logs": 0,
            "save_logs_post": [
                '/',
                '/web/love/index',
                '/web/love/photo',
                '/test/test',
                '/test/logs',
            ],
            "save_logs_get": [
                '/',
                '/web/love/index',
                '/web/love/photo',
                '/test/test',
                '/test/logs',
            ],
        }

    # 存储日志
    @staticmethod
    def django_save_log(request, code=200):
        meta = request.META
        method = request.method
        form_data = request.POST
        user_ip = meta.get('HTTP_X_FORWARDED_FOR', '127.0.0.2')  # django版本不一样，参数不一样
        user_ua = meta.get('HTTP_USER_AGENT', '')
        user_path_info = meta.get('PATH_INFO', '')

        values = meta.items()
        info = []
        for k, v in values:
            info.append(f'{k}:{v}')

        # 排除一些请求
        for no_save in ['/static/', '/favicon.ico']:
            if no_save in user_path_info:
                return 0

        create_time = int(time.time())
        create_time_str = time.strftime("%Y-%m-%d %X", time.localtime(create_time))  # 2021-04-12 14:36:20
        save_table = config_dict['mysql_table']['fr1997']['django_logs']['name']
        mode_pro.mysql_db(method="ins", table=save_table, save_data={
            'code': code,
            'method': method,
            'form_data': form_data,
            'user_ua': user_ua,
            'user_ip': user_ip,
            'info': str(info),
            'user_path_info': user_path_info,
            'create_time': create_time,
            'create_time_str': create_time_str,
        }, conn_tp=5)
        return {
            'info': info,
            'user_ua': user_ua,
            'user_ip': user_ip,
            'user_path_info': user_path_info,
        }

    # 装饰器 请求限制
    def django_res_limit(self, func):
        """
            get 不验证token   post  需要验证
        """

        def wrapper(request):
            method = request.method
            form_data = request.POST
            url_path = str(request.path)
            # 存储日志(存储的是请求，不是结果)
            if method == 'GET' and url_path in self.django_config()['save_logs_get']:
                self.django_save_log(request)  # 存储django日志
            elif method == 'POST' and url_path in self.django_config()['save_logs_post']:
                self.django_save_log(request)  # 存储django日志

            # POST 要验证token
            try:
                if method == 'GET':
                    return func(request)
                elif method == 'POST':
                    token = form_data.get('token', '')  # 验证参数
                    if token == config_dict['token']['django'] or url_path in config_dict['django']['no_token_check']:
                        return func(request)
                    else:
                        django_code = "code_token"
                else:
                    django_code = "code_method"
            except Exception as E:
                print(E)
                django_code = "code_xxx"
            from django.http import JsonResponse  # 2.返回json对象
            ret = self.django_return(code=django_code)
            return JsonResponse(ret)

        return wrapper

    # django 返回配置
    def django_return(self, **kwargs):
        sc = 'status_code'  # 返回码
        msg = 'message'  # 返回消息
        code = kwargs.get('code')
        status_codes = self.django_config()['status_codes']
        return {
            sc: status_codes[code][sc],
            msg: status_codes[code][msg],
        }


# mode
class ModeFunc:
    def __init__(self):
        self.path = mode_pros.run_machine()['platform']

    # >>>>----------------       数据库 redis数据库        ----------------<<<<<
    def db_redis(self, RedisDb=0, db=0):
        redis_cfg = 'redis_loc'
        if RedisDb == 0:
            redis_cfg = 'redis_loc'
        elif RedisDb == 10:
            redis_cfg = 'redis_spider1'
        elif RedisDb == 11:  # 内网
            redis_cfg = 'redis_spider1'
        elif RedisDb == 3:
            redis_cfg = 'redis_spider3'

        if self.path == 1:
            redis_host = '127.0.0.1'
        else:
            redis_host = config_dict['redis'][redis_cfg]['host']
        redis_port = config_dict['redis'][redis_cfg]['port']
        redis_pwd = config_dict['redis'][redis_cfg]['pwd']
        return redis.StrictRedis(host=redis_host, port=int(redis_port), password=redis_pwd, db=db)

    # Redis 表记录
    @staticmethod
    def redis_task(task_name):
        """
            tp:选用哪个数据库
            type:存储类型
                kv=键值对   start_：前缀
        """
        redis_task = {
            'douyin_user_cloud': {
                'RedisDb': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_cloud', 'ttl': 6000
            },  # 抖音用户云词 几万
            'douyin_user_krm': {
                'RedisDb': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_krm', 'ttl': 6000
            },  # 抖音krm
            'douyin_user_ranks': {
                'RedisDb': 3, 'db': 6, 'type': 'kv', 'start_': 'douyin_user_ranks', 'ttl': 6000
            }  # 抖音krm
        }
        return redis_task[task_name]

    # >>>>----------------       数据库 mysql数据库         ----------------<<<<<
    def db_mysql(self, path=1):
        if path == 1:
            db_cfg = "mysql_jike_in"
        elif path == 2:
            db_cfg = "mysql_jike_test"
        elif path == 3:
            db_cfg = "mysql_loc"
        elif path == 5:
            db_cfg = "mysql_my_tx"
        else:
            db_cfg = "mysql_jike_out"
        mysql_host = config_dict["mysql"][db_cfg]['host']
        mysql_user = config_dict["mysql"][db_cfg]['user']
        mysql_passwd = config_dict["mysql"][db_cfg]['pwd']
        mysql_db = config_dict["mysql"][db_cfg]['db']
        mysql_port = int(config_dict["mysql"][db_cfg]['port'])
        conn = pymysql.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db, port=int(mysql_port))
        return conn

    # db Mysql 操作 20230719新
    def mysql_db(self, method, table, conn_tp=0, **kwargs):
        """
            method
                - s -- select
                - up --date_more_byid
                - ins -- insert
                - iss -- insert_all
                - tc -- create_table 创建表
                - te -- table_exist 查询 表是否存在
        """
        sql = kwargs.get('sql', '')
        save_data = kwargs.get('save_data')

        # mysql链接 【自动】0=内网 1=外网
        conn = self.db_mysql(path=conn_tp)

        # 通用sql
        sql_table_exist = f"SELECT * FROM information_schema.tables WHERE table_name = '{table}'"

        # 数据库操作
        try:
            with conn.cursor() as cursor:
                if method == 'insert' or method == 'ins':
                    save_data = kwargs['save_data']
                    columns = ', '.join(save_data.keys())
                    placeholders = ', '.join(['%s'] * len(save_data))
                    params = tuple(save_data.values())
                    sql = f"INSERT ignore INTO {table} ({columns}) VALUES ({placeholders})"
                    cursor.execute(sql, params)
                    conn.commit()
                elif method == 'insert_all' or method == 'iss':
                    fields = list(save_data[0].keys())
                    placeholders = ', '.join(f'%({i})s' for i in fields)
                    fields_str = ','.join(fields)
                    sql_inserts = f"INSERT ignore INTO {table} ({fields_str}) values({placeholders})"
                    n = cursor.executemany(sql_inserts, save_data)
                    conn.commit()
                    return n
                elif method == 'insert_creat_all' or method == 'isc':
                    pass
                    # # 根据索引插入或更新 没有索引最后 没有更新默认
                    # key = kwargs.get('key')
                    # if key in None:
                    #
                    # update_key = []
                    #
                    # fields = list(save_data[0].keys())
                    # placeholders = ', '.join(f'%({i})s' for i in fields)
                    # fields_str = ','.join(fields)
                    # sql_inserts = f"INSERT INTO {table} ({fields_str}) values({placeholders}) on DUPLICATE {key} update"
                    # return sql_inserts
                    # # n = cursor.executemany(sql_inserts, save_data)
                    # # conn.commit()
                    # # return n
                elif method == 'table_exist' or method == 'te':
                    # 查询 表是否存在
                    return cursor.execute(sql_table_exist)
                elif method == 'create_table' or method == 'tc':  # 创建一个表
                    table_exist = cursor.execute(sql_table_exist)
                    if table_exist:
                        del_and_create = kwargs.get('del_and_create', 0)
                        if del_and_create:
                            print('表已经存在 删除并创建')
                            self.mysql_db(method='dt', table=table, conn_tp=conn_tp)
                        else:
                            print('表已经存在')
                            return '表已经存在'
                    """
                        TINYINT = [-128,127]
                        SMALLINT = [-32768,32767]
                    """
                    fields_sql = []
                    field_cfg = kwargs['field_cfg']
                    for f in field_cfg['fields']:
                        name = f['f_name']
                        field_type = f['field_type']
                        comment = f.get('comment', '待增加注释')

                        if field_type == 'VARCHAR':
                            length = f.get('length', 255)
                            default = f.get('default', '')
                            fields_sql.append(f"{name} {field_type}({length}) DEFAULT '{default}' COMMENT '{comment}'")
                        elif field_type == 'INT' or field_type == 'TINYINT' or field_type == 'SMALLINT':
                            length = f.get('length', 11)
                            default = f.get('default', 0)
                            fields_sql.append(f"{name} {field_type}({length}) DEFAULT {default} COMMENT '{comment}'")
                    if fields_sql:
                        this_time = time.strftime("%Y-%m-%d %X", time.localtime(int(time.time())))
                        table_notes = f'{this_time} 【高阳】创建此表'  # 表备注
                        sql_create_base = f"CREATE TABLE {table} ({field_cfg['id']} INT AUTO_INCREMENT PRIMARY KEY,{','.join(fields_sql)}) COMMENT='{table_notes}'"
                        cursor.execute(sql_create_base)

                        # 增加唯一索引
                        field_index = field_cfg['field_index']
                        if field_index:
                            if len(field_index) == 1:
                                sql_index = f"ALTER TABLE {table} ADD UNIQUE INDEX field_index ({field_index[0]});"
                            else:
                                sql_index = f"ALTER TABLE {table} ADD CONSTRAINT field_index UNIQUE ({','.join(field_index)});"
                            cursor.execute(sql_index)
                        print(f"创建{table}成功")
                        return f"创建{table}成功"
                elif method == 'sql':
                    cursor.execute(sql)
                    conn.commit()
                elif method == 'update_more_byid' or method == 'up':  # 更新 根据id进行批量更新
                    if save_data:
                        fields = list(save_data[0].keys())
                        update_fields = [f'{i}=%s' for i in fields[:-1]]
                        sql_update = f"UPDATE {table} SET {','.join(update_fields)} WHERE {fields[-1]} = %s"
                        tuple_data_list = [tuple(data.values()) for data in save_data]
                        cursor.executemany(sql_update, tuple_data_list)
                        conn.commit()
                elif method == 'select' or method == 's':
                    cursor.execute(sql)
                    return cursor.fetchall()
                elif method == 'del_table' or method == 'dt':
                    sql_del = f'DROP TABLE {table}'
                    cursor.execute(sql_del)
                    conn.commit()
                else:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except Exception as e:
            print(f"数据库链接错误:{e}")
        finally:
            conn.close()

    # >>>>----------------       数据库 es数据库        ----------------<<<<<
    def db_es(self):
        if self.path == 1:
            es_cfg = 'es_jike_in'
        else:
            es_cfg = 'es_jike_out'
        es_ip = config_dict['es'][es_cfg]['ip']
        es_user = config_dict['es'][es_cfg]['user']
        es_pwb = config_dict['es'][es_cfg]['pwd']
        es_port = config_dict['es'][es_cfg]['port']
        es = Elasticsearch([f'{es_ip}:{es_port}'], http_auth=(es_user, es_pwb))
        return es

    # ES 查询
    def es_search_new(self, table, query, size=1, sort_info=None, is_ret_num=1, ret_num=0, **kwargs):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
        }

        # 排序
        if sort_info and sort_info != 0:
            body['sort'] = sort_info
        else:
            body['sort'] = {
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }

        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        _shards = response.get('_shards')
        if _shards:
            successful = _shards.get('successful')
            if successful > 0:
                value = response.get('hits')['total']['value']
                hits_list = response.get('hits')['hits']
                print(f'总个数:{value} 取出:{len(hits_list)}')
                if ret_num == 0:
                    return hits_list
                else:
                    return [hits_list, value]

    # ES 查询
    def es_search_new_20231215(self, table, query, _source, size=1, sort_info=None, is_ret_num=1, ret_num=0, **kwargs):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
            "_source": _source,
        }

        # 排序
        if sort_info and sort_info != 0:
            body['sort'] = sort_info
        else:
            body['sort'] = {
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }

        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        _shards = response.get('_shards')
        if _shards:
            successful = _shards.get('successful')
            if successful > 0:
                value = response.get('hits')['total']['value']
                hits_list = response.get('hits')['hits']
                print(f'总个数:{value} 取出:{len(hits_list)}')
                if ret_num == 0:
                    return hits_list
                else:
                    return [hits_list, value]

    # ES 查询 单条
    def es_search_one(self, table, _id, is_print=1):
        body = {
            "track_total_hits": True,
            "query": {
                "match": {"_id": _id}
            }
        }
        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        hits_list = response.get('hits')['hits']
        if is_print:
            value = response.get('hits')['total']['value']
            hits_list = response.get('hits')['hits']
            print(f'总个数:{value} 取出:{len(hits_list)}')
        return hits_list

    # ES 查询 纯es
    def es_search_es(self, table, query):

        es = self.db_es()
        response = es.search(
            index=table,
            body=query
        )
        return response

    # ES 数量
    def es_count(self, table):
        try:
            body = {
                "size": 1,
                "track_total_hits": True
            }
            es = self.db_es()
            response = es.search(
                index=table,
                body=body
            )
            count = response.get('hits')['total']['value']
            return count
        except:
            return -1

    # ES 数量
    def es_count_with_query(self, table, query):
        try:
            body = {
                "query": query,
                "size": 1,
                "track_total_hits": True
            }
            es = self.db_es()
            response = es.search(
                index=table,
                body=body
            )
            count = response.get('hits')['total']['value']
            return count
        except:
            return -1

    # ES 合并查询
    def es_search_merge(self, queries, table):
        es = self.db_es()

        def process_query(query):
            result = es.search(index=table, body=query)
            return result

        # 创建线程池
        pool = ThreadPoolExecutor(max_workers=5)  # 根据需求设置最大工作线程数

        # 提交查询任务到线程池
        futures = [pool.submit(process_query, query) for query in queries]

        # 获取查询结果
        results = [future.result() for future in futures]

        return results

    # ES 查询 分页
    def es_search_page(self, table, query, sort, size=1, offset=0, is_ret_num=1, is_print=0):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
            "from": offset,
            "sort": sort,
        }

        # 排序方式
        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )
        _shards = response.get('_shards')
        if _shards:
            successful = _shards.get('successful')
            if successful > 0:
                hits_list = response.get('hits')['hits']
                if is_print:
                    value = response.get('hits')['total']['value']
                    hits_list = response.get('hits')['hits']
                    print(f'总个数:{value} 取出:{len(hits_list)}')
                return hits_list

    # ES 查询 多表合并查询
    def es_search_alias(self, table, query, size=1, sort_info=None, is_ret_num=1, is_print=0, ret_num=0,
                        **kwargs):
        body = {
            "query": query,
            "track_total_hits": True if is_ret_num == 1 else False,
            "size": size,
        }

        _source = kwargs.get("_source")
        if _source is not None:
            body['_source'] = _source

        # 根据规则排序
        if sort_info:
            body['sort'] = sort_info
        else:
            body['sort'] = {
                "_script": {
                    "script": "Math.random()",
                    "type": "number"
                }
            }

        es = self.db_es()
        response = es.search(
            index=table,
            body=body
        )

        hits = response['hits']
        db_total = hits['total']['value']
        hits_list = hits['hits']
        print(f'总个数:{db_total} 取出:{len(hits_list)}')

        if ret_num == 0:
            return hits_list
        else:
            return [hits_list, db_total]

    # ES 更新
    def es_create_update(self, doc, index, split_num=0):
        es = self.db_es()
        if doc:
            if split_num:
                each_item = mode_data.list_avg_split(doc, split_num * 2)
                for it_doc in each_item:
                    time.sleep(1)
                    es.bulk(body=it_doc, index=index)
            else:
                es.bulk(body=doc, index=index)

    # ES 更新 (自动判断内外网)
    def es_create_update_noIndex(self, doc, split_num=0):
        es = self.db_es()
        if doc:
            if split_num:
                each_item = mode_data.list_avg_split(doc, split_num * 2)
                for it_doc in each_item:
                    time.sleep(1)
                    es.bulk(body=it_doc)
            else:
                es.bulk(body=doc)

    # ES 更新 分表
    def es_create_update_alias(self, doc):
        es = self.db_es()
        if doc:
            es.bulk(body=doc)

    # ES 删除
    def es_del(self, query, index):
        es = self.db_es()
        es.delete_by_query(index=index, body=query, doc_type='_doc')

    # ES 多id查询
    def es_in_or_notin(self, table, shoulds, query=None):
        """
        :param table: 数据表
        :param shoulds: 需要查询的 _id
        :return: [存在,数据info,不存在]
        """
        is_in = []
        is_in_data = {}
        es = self.db_es()
        if shoulds:
            if query is None:
                query = {
                    "bool": {
                        "must": [
                            {"terms": {"_id": shoulds}}
                        ],
                        # "must_not": {"match": {"update_time_1": 0}}
                    }
                }
            response = es.search(
                index=table,
                body={
                    "query": query,
                    "size": 1500,  # 返回数量
                    "track_total_hits": 'true',  # 显示总量有多少条
                }
            )
            if response:
                _shards = response.get('_shards')
                if _shards:
                    successful = _shards.get('successful')
                    if successful == 1:
                        # 数据集
                        hits_list = response.get('hits')['hits']
                        print('本次取出符合条件的总数:', len(hits_list))

                        for index_x, i in enumerate(hits_list):
                            _s = i['_source']
                            _id = i['_id']
                            is_in.append(_id)
                            is_in_data[f'{_id}'] = _s

        shoulds_not = [i for i in shoulds if str(i) not in is_in]
        return is_in, is_in_data, shoulds_not

    # ES 多id查询
    def es_in_or_notin_20231215(self, table, shoulds, _source, split_num=200):
        """
        :param table: 数据表
        :param shoulds: 需要查询的 _id
        :return: [存在,数据info,不存在]
        """
        is_in = []
        is_in_data = {}
        shoulds_not = []
        es = self.db_es()

        each_item = mode_data.list_avg_split(shoulds, split_num)
        for it_shoulds in each_item:
            time.sleep(1)
            if it_shoulds:
                query = {
                    "bool": {
                        "must": [
                            {"terms": {"_id": it_shoulds}}
                        ],
                    }
                }
                body = {
                    "query": query,
                    "size": split_num,
                    "_source": _source,
                    "track_total_hits": 'true',
                }
                response = es.search(index=table, body=body)
                if response:
                    _shards = response.get('_shards')
                    if _shards:
                        successful = _shards.get('successful')
                        if successful > 0:
                            # 数据集
                            hits_list = response.get('hits')['hits']
                            print('本次取出符合条件的总数:', len(hits_list))

                            for index_x, i in enumerate(hits_list):
                                _s = i['_source']
                                _id = i['_id']
                                is_in.append(_id)
                                is_in_data[f'{_id}'] = _s

            it_shoulds_not = [i for i in it_shoulds if str(i) not in is_in]
            shoulds_not += it_shoulds_not
        return is_in, is_in_data, shoulds_not

    # ES 多id查询(多表)
    def es_in_or_notins(self, table, shoulds, query=None, is_print=0, is_index=0):
        """
        :param table: 数据表
        :param shoulds: 需要查询的 _id
        :return: [存在,数据info,不存在]
        """
        is_in = []
        is_in_data = {}
        es = self.db_es()
        if shoulds:
            if query is None:
                query = {
                    "bool": {
                        "must": [
                            {"terms": {"_id": shoulds}}
                        ],
                        # "must_not": {"match": {"update_time_1": 0}}
                    }
                }
            response = es.search(
                index=table,
                body={
                    "query": query,
                    "size": 1500,  # 返回数量
                    "track_total_hits": 'true',  # 显示总量有多少条
                }
            )
            if response:
                _shards = response.get('_shards')
                if _shards:
                    successful = _shards.get('successful')
                    if successful > 0:
                        # 数据集
                        hits_list = response.get('hits')['hits']
                        if is_print:
                            print('本次取出符合条件的总数:', len(hits_list))

                        for index_x, i in enumerate(hits_list):
                            _s = i['_source']
                            _id = i['_id']
                            is_in.append(_id)
                            if is_index == 1:
                                _s['_index'] = i['_index']
                            is_in_data[f'{_id}'] = _s

        shoulds_not = [i for i in shoulds if str(i) not in is_in]
        return is_in, is_in_data, shoulds_not

    # 分词 老版本
    @staticmethod
    def word_split_old(txt, num=100, clear_myself="???"):
        import jieba

        try:
            num = int(num)
        except:
            num = 100

        # 文本过滤 [去空格 去数字]
        txt = str(txt).replace('\n', '').replace('\r', '').replace('\\', '')
        txt = str(txt).replace(' ', '')
        txt = str(txt).replace("'", " ").replace('"', ' ').replace('◕', ' ').replace(':', ' ').replace('：', ' ')
        words = jieba.lcut(txt)  # 使用精确模式对文本进行分词
        counts = {}  # 通过键值对的形式存储词语及其出现的次数

        # 单个词语不计算在内
        for word in words:
            if word != clear_myself:
                if len(word) == 1:
                    continue
                else:
                    counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1

        # 根据词语出现的次数进行从大到小排序
        items = list(counts.items())
        items.sort(key=lambda x: x[1], reverse=True)
        if num > len(items):
            num = len(items)

        # 分级选择
        data_list = []
        for i in range(num):
            data_dict = {}
            word, count = items[i]
            data_dict['word'] = word
            data_dict['count'] = count
            if count >= 100:
                data_dict['category'] = '100'
            elif count >= 50:
                data_dict['category'] = '50'
            elif count >= 10:
                data_dict['category'] = '10'
            elif count >= 7:
                data_dict['category'] = '7'
            elif count >= 4:
                data_dict['category'] = '4'
            else:
                data_dict['category'] = '1'
            data_list.append(data_dict)
            # print("{0:<5}{1:>5}".format(word, count))
        return data_list

    # 汉字 => 拼音
    def chinese_to_pinyin(self, chinese="你好", ret=1):
        """
            ret = 1  -->  [['ni3'], ['hao3']]
            ret = 2  -->  nh
            ret = 3  -->  n

            英文的全部转换为小写

            更多复杂判断 都在这里写
                符号开头的返回 ”other“
                数字开头的返回 ”number“
        """
        try:
            chinese = chinese.lower()
            if chinese:
                # 将中文转换为拼音，设置输出格式为带声调的拼音
                pinyin_list = pinyin(chinese, style=Style.TONE3)

                # 提取每个拼音的第一个字母
                first_letters = [p[0][0] for p in pinyin_list]

                # 将字母列表连接成字符串
                first_letters_string = ''.join(first_letters)
                if ret == 2:
                    return first_letters_string
                elif ret == 3:
                    first_word = first_letters_string[:1]
                    if first_word in config_dict['numbers'] or first_word in config_dict['numbers_str']:  # 数字开头
                        return "number"
                    elif first_word == ' ':
                        return "empty"
                    elif first_word not in config_dict['low_word']:  # 符号开头
                        return "other"
                    else:
                        return first_letters_string[:1]
                else:
                    return pinyin_list
            else:
                return "empty"
        except:
            return "other"

    # 关键词日数据 快速查询
    def keyword_day_index_select(self, keyword_list):
        # 获取今日时间戳 获取12个小时时间戳
        order_time = int(time.time()) - 600
        t0 = mode_time.zero_clock()
        if order_time < t0:
            order_time = t0 + 1
        if order_time < 1694491630:  # Bug修改
            order_time = 1694491630

        query1 = {
            "bool": {
                "filter": [
                    {
                        "terms": {
                            "keyword": keyword_list
                        }
                    },
                    {
                        "range": {"update_time": {"gte": order_time}}
                    }
                ]
            }
        }
        is_in = []
        is_in_data = {}
        ret_hits_list = self.es_search_alias(table='douyin_keyword_index', query=query1, size=1000)
        if ret_hits_list:
            for index_x, i in enumerate(ret_hits_list):
                _s = i['_source']
                _id = i['_id']
                is_in.append(_id)
                is_in_data[f'{_id}'] = _s
        should_not = [i for i in keyword_list if str(i) not in is_in]
        return is_in, is_in_data, should_not

    # 巨量广告cookie
    def qianchuan_index_cookie(self):

        # 缓存到内存
        data_list = cache_get('jike_qianchuan_ad_cookie')
        if not data_list:
            data_list = []
            sql = f"SELECT * FROM `cd_task` WHERE id IN (17,27,33,38);"
            ret = self.mysql_db(method='s', table='cd_task', sql=sql)
            for i in ret:
                data_dict = {}
                json_data = eval(i[7])
                csrftoken = json_data['csrftoken']
                sid_tt = json_data['sid_tt']
                aadvid = json_data['aadvid']
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Origin': 'https://ad.ocean' + 'engine.com',
                    'Referer': f'https://ad.ocean' + f'engine.com/bp/material/traffic_analysis.html?aadvid={aadvid}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                    'X-CSRFToken': csrftoken,
                }
                cookies = {'csrftoken': csrftoken, 'sid_tt': sid_tt}
                data_dict['headers'] = headers
                data_dict['cookies'] = cookies
                data_dict['aadvid'] = aadvid
                data_dict['sid_tt'] = sid_tt
                data_dict['csrftoken'] = csrftoken
                data_dict['id_id'] = i[0]
                data_list.append(data_dict)
            cache_set('jike_qianchuan_ad_cookie', data_list, 200)
        return data_list

    # 关键词日数据 数据分析
    @staticmethod
    def keyword_day_index_get(data):
        """
        [{'t': 1691164800, 'v': 2595}, {'t': 1691251200, 'v': 2292}, {'t': 1691337600, 'v': 2048}, {'t': 1691424000, 'v': 1965}, {'t': 1691510400, 'v': 2095}, {'t': 1691596800, 'v': 2503}, {'t': 1691683200, 'v': 2177}, {'t': 1691769600, 'v': 2166}, {'t': 1691856000, 'v': 1997}, {'t': 1691942400, 'v': 2025}, {'t': 1692028800, 'v': 2030}, {'t': 1692115200, 'v': 2159}, {'t': 1692201600, 'v': 2648}, {'t': 1692288000, 'v': 2107}, {'t': 1692374400, 'v': 2392}, {'t': 1692460800, 'v': 2378}, {'t': 1692547200, 'v': 2173}, {'t': 1692633600, 'v': 2093}, {'t': 1692720000, 'v': 2020}, {'t': 1692806400, 'v': 1969}, {'t': 1692892800, 'v': 2244}, {'t': 1692979200, 'v': 2924}, {'t': 1693065600, 'v': 2697}, {'t': 1693152000, 'v': 2454}, {'t': 1693238400, 'v': 2431}, {'t': 1693324800, 'v': 2221}, {'t': 1693411200, 'v': 2254}, {'t': 1693497600, 'v': 1748}, {'t': 1693584000, 'v': 2087}, {'t': 1693670400, 'v': 1912}]
        """
        day_index = []
        keyword_pv_trend = data.get('keyword_pv_trend')
        if keyword_pv_trend:
            for i in keyword_pv_trend:
                t = i['date']
                v = i['pv']
                timestamp1 = int(time.mktime(time.strptime(t, '%Y-%m-%d')))
                day_index.append({'t': timestamp1, 'v': v})
        return day_index

    # 关键词日数据 存储
    def keyword_day_index_save(self, save_data):
        should_keyword = []
        keyword_index_doc = []
        keyword_index_sign_doc = []
        if save_data:
            for i in save_data:
                _id = i['keyword']
                should_keyword.append(_id)
            is_in, is_in_data, shoulds_not = self.es_in_or_notins('dso_douyin_keyword_alias', should_keyword)
            for i in save_data:
                _id = i['keyword']
                i['index_avg'] = mode_data.list_avg(i['day_index'])
                keyword_index_doc.append({"index": {"_id": f"{_id}"}})
                keyword_index_doc.append(i)

                # 同步到关键词表
                if _id in is_in_data:
                    _index = is_in_data[_id]['_index']
                    keyword_index_sign_doc.append({'update': {'_index': _index, '_id': _id}})
                    keyword_index_sign_doc.append({'doc': {'index_avg': i['index_avg']}})
        self.es_create_update(doc=keyword_index_doc, index='douyin_keyword_index')
        self.es_create_update_noIndex(doc=keyword_index_sign_doc)

    # ip 信息
    def get_user_ip(self, ip):
        url = f'http://whois.pconline.com.cn/ipJson.jsp?ip={ip}&json=true'
        Default_return = {
            'ip': ip,
            'country': '',
            'province': '',
            'city': '',
            'isp': '',
            'city_id': '',
            'create_time': int(time.time()),
            'addr': '',
        }

        if ip == '101.35.29.36':
            return Default_return

        if ip.split('.')[0] == '127':
            return Default_return

        if ip.split('.')[0] == '192' and ip.split('.')[1] == '168':
            return Default_return

        # 请求
        try:
            res = HttpJike.post(url=url)
            if res.status_code == 200:
                data_data = res.json()
                country = data_data.get('country')
                city = data_data.get('city')
                city_id = data_data.get('cityCode')
                province = data_data.get('pro')
                addr = data_data.get('addr')

                isp = '其他'
                for k in ['电信', '移动', '联通']:
                    if k in addr:
                        isp = k
                        break

                self.mysql_db(method="insert", table='member_ips', save_data={
                    'ip': ip,
                    'country': country,
                    'province': province,
                    'city': city,
                    'isp': isp,
                    'city_id': str(city_id),
                    'create_time': int(time.time()),
                    'addr': addr,
                }, conn_tp=5)
                return {
                    'ip': ip,
                    'country': country,
                    'province': province,
                    'city': city,
                    'isp': isp,
                    'city_id': str(city_id),
                    'create_time': int(time.time()),
                    'addr': addr,
                }
        except:
            pass
        return Default_return

    # 抖查查 代理(缓存到mysql中的ip)
    def douchacha_ips_mysql(self, num=1):
        t0 = int(time.time()) - 120
        sql = f'SELECT ip FROM cd_douchacha_ip where update_time > {t0}'
        ips = []
        data_data = self.mysql_db(method="select", table="cd_douchacha_ip", sql=sql)
        for i in data_data:
            ips.append(i[0])

        dcc_proxies = {
            'ip': [],
            'aiohttp_ip': [],
            'request_ip': [],
        }
        for ip in ips:
            dcc_proxies['ip'].append(ip)
            dcc_proxies['aiohttp_ip'].append(f"http://{ip}")
            dcc_proxies['request_ip'].append(HttpJike.http_ip(ip))
        return dcc_proxies

    # 获取js文件的绝对路径
    def get_js_base_path(self, js_name):
        base_path = f'gy_pyhton_project/all_project/old/js/{js_name}.js'
        if self.path == 1:
            return f'/www/wwwroot/{base_path}'
        else:
            return f'C://Users/30844\Documents\project_all\python_project\mofan/{base_path}'

    # 抖音xb
    def get_xbogus_new(self, url, ua, mstoken=''):
        # 获取js文件绝对路径
        js_path = self.get_js_base_path(js_name='dy_x_bogus_v2')

        # 重编url
        url_p = urlparse(url)
        params_dict = dict()
        for i in url_p.query.split("&"):
            key, values = i.split('=')[0], i.split('=')[-1]
            if key not in ["msToken", "X-Bogus"]:
                params_dict[key] = values
        param_str = "&".join([f"{i}={params_dict[i]}" for i in params_dict])
        url = f"{url_p.scheme}://{url_p.netloc}{url_p.path}?{param_str}"
        url_para = url.split('?')[1] + '&msToken='

        with open(js_path, 'r', encoding='UTF-8') as file:
            result = file.read()
            context = execjs.compile(result)

            # 提前对参数进行处理
            md5_url = mode_pros.md5_base(url_para)

            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()
            res = context.call("get_xbogus", url_para, ua, md5her)
            result_url = f'{url}&msToken={mstoken}&X-Bogus={res}'
            return result_url

    # 抖音xb
    def get_xbogus_new_gbk(self, url, ua, mstoken=''):
        # 获取js文件绝对路径
        js_path = self.get_js_base_path(js_name='dy_x_bogus_v2')

        # 重编url
        url_p = urlparse(url)
        params_dict = dict()
        for i in url_p.query.split("&"):
            key, values = i.split('=')[0], i.split('=')[-1]
            if key not in ["msToken", "X-Bogus"]:
                params_dict[key] = values
        param_str = "&".join([f"{i}={params_dict[i]}" for i in params_dict])
        url = f"{url_p.scheme}://{url_p.netloc}{url_p.path}?{param_str}"
        url_para = url.split('?')[1] + '&msToken='

        with open(js_path, 'r', encoding='gbk') as file:
            result = file.read()
            context = execjs.compile(result)

            # 提前对参数进行处理
            md5_url = mode_pros.md5_base(url_para)

            str1 = bytes.fromhex(md5_url)
            hash_object = hashlib.md5(str1)
            md5her = hash_object.hexdigest()
            res = context.call("get_xbogus", url_para, ua, md5her)
            result_url = f'{url}&msToken={mstoken}&X-Bogus={res}'
            return result_url

    # 抖音 msToken生成方式
    @staticmethod
    def get_douyin_token(string_len=16):
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        for _ in range(string_len):
            random_str += base_str[random.randint(0, length)]
        return random_str

    # 抖音cookie ttwid版本 db数据库
    def ttwid_cookie_tt(self, num=200, get_cache=0):
        if self.path == 1:  # 服务器运行强制默认缓存数据
            get_cache = 1

        cookie_tt = []
        if get_cache == 1:
            cookie_tt = cache_get('jike_ttwid_cookies')
        else:
            sql = f'SELECT douyin_cookie_ttwid FROM `cd_cookie_douyin` where douyin_cookie_ttwid is not null order by rand() limit {num}'
            all_cookie = mode_pro.mysql_db(method='s', table='cd_cookie_douyin', sql=sql)
            for i in all_cookie:
                cookie_tt.append(i[0])
        return cookie_tt

    # 查看某个文件夹所有文件
    @staticmethod
    def get_all_file(directory_path):
        fs = []
        try:
            # 使用 os.listdir 获取目录中的所有文件和子目录
            files = os.listdir(directory_path)

            # 输出所有文件和子目录的名称
            for file in files:
                fs.append(file)

        except Exception as e:
            print(f"Error listing files in directory: {e}")
        return fs

    # 获取知乎cookie
    def get_zhihu_cookie(self):
        cookies = cache_get('jike_zhihu_cookies')
        if not cookies:
            cookies = []
            sql = f"SELECT * FROM cd_zhihu_cookie where id > 0"
            all_cookie = self.mysql_db(method='s', table='cd_zhihu_cookie', sql=sql)
            for each in all_cookie:
                cookie = each[1]
                cookies.append(cookie)
            cache_set('jike_zhihu_cookies', cookies, 50)
        return cookies

    # 知乎加密 python版本
    def x_zse_96_b64encode(self, md5_bytes: bytes):
        h = {
            "zk": [1170614578, 1024848638, 1413669199, -343334464, -766094290, -1373058082, -143119608, -297228157,
                   1933479194, -971186181, -406453910, 460404854, -547427574, -1891326262, -1679095901, 2119585428,
                   -2029270069, 2035090028, -1521520070, -5587175, -77751101, -2094365853, -1243052806, 1579901135,
                   1321810770, 456816404, -1391643889, -229302305, 330002838, -788960546, 363569021, -1947871109],
            "zb": [20, 223, 245, 7, 248, 2, 194, 209, 87, 6, 227, 253, 240, 128, 222, 91, 237, 9, 125, 157, 230, 93,
                   252,
                   205, 90, 79, 144, 199, 159, 197, 186, 167, 39, 37, 156, 198, 38, 42, 43, 168, 217, 153, 15, 103, 80,
                   189,
                   71, 191, 97, 84, 247, 95, 36, 69, 14, 35, 12, 171, 28, 114, 178, 148, 86, 182, 32, 83, 158, 109, 22,
                   255,
                   94, 238, 151, 85, 77, 124, 254, 18, 4, 26, 123, 176, 232, 193, 131, 172, 143, 142, 150, 30, 10, 146,
                   162,
                   62, 224, 218, 196, 229, 1, 192, 213, 27, 110, 56, 231, 180, 138, 107, 242, 187, 54, 120, 19, 44, 117,
                   228, 215, 203, 53, 239, 251, 127, 81, 11, 133, 96, 204, 132, 41, 115, 73, 55, 249, 147, 102, 48, 122,
                   145, 106, 118, 74, 190, 29, 16, 174, 5, 177, 129, 63, 113, 99, 31, 161, 76, 246, 34, 211, 13, 60, 68,
                   207, 160, 65, 111, 82, 165, 67, 169, 225, 57, 112, 244, 155, 51, 236, 200, 233, 58, 61, 47, 100, 137,
                   185, 64, 17, 70, 234, 163, 219, 108, 170, 166, 59, 149, 52, 105, 24, 212, 78, 173, 45, 0, 116, 226,
                   119,
                   136, 206, 135, 175, 195, 25, 92, 121, 208, 126, 139, 3, 75, 141, 21, 130, 98, 241, 40, 154, 66, 184,
                   49,
                   181, 46, 243, 88, 101, 183, 8, 23, 72, 188, 104, 179, 210, 134, 250, 201, 164, 89, 216, 202, 220, 50,
                   221, 152, 140, 33, 235, 214],
            "zm": [120, 50, 98, 101, 99, 98, 119, 100, 103, 107, 99, 119, 97, 99, 110, 111]
        }

        def left_shift(x, y):
            x, y = ctypes.c_int32(x).value, y % 32
            return ctypes.c_int32(x << y).value

        def Unsigned_right_shift(x, y):
            x, y = ctypes.c_uint32(x).value, y % 32
            return ctypes.c_uint32(x >> y).value

        def Q(e, t):
            return left_shift((4294967295 & e), t) | Unsigned_right_shift(e, 32 - t)

        def G(e):
            t = list(struct.pack(">i", e))
            n = [h['zb'][255 & t[0]], h['zb'][255 & t[1]], h['zb'][255 & t[2]], h['zb'][255 & t[3]]]
            r = struct.unpack(">i", bytes(n))[0]
            return r ^ Q(r, 2) ^ Q(r, 10) ^ Q(r, 18) ^ Q(r, 24)

        def g_r(e):
            n = list(struct.unpack(">iiii", bytes(e)))
            [n.append(n[r] ^ G(n[r + 1] ^ n[r + 2] ^ n[r + 3] ^ h['zk'][r])) for r in range(32)]
            return list(
                struct.pack(">i", n[35]) + struct.pack(">i", n[34]) + struct.pack(">i", n[33]) + struct.pack(">i",
                                                                                                             n[32]))

        def g_x(e, t):
            n = []
            i = 0
            for _ in range(len(e), 0, -16):
                o = e[16 * i: 16 * (i + 1)]
                a = [o[c] ^ t[c] for c in range(16)]
                t = g_r(a)
                n += t
                i += 1
            return n

        local_48 = [48, 53, 57, 48, 53, 51, 102, 55, 100, 49, 53, 101, 48, 49, 100, 55]
        local_50 = bytes([63, 0]) + md5_bytes  # 随机数  0 是环境检测通过
        local_50 = ZhihuSign.pad(bytes(local_50))
        local_34 = local_50[:16]
        local_35 = [local_34[local_11] ^ local_48[local_11] ^ 42 for local_11 in range(16)]
        local_36 = g_r(local_35)
        local_38 = local_50[16:]
        local_39 = g_x(local_38, local_36)
        local_53 = local_36 + local_39
        local_55 = "6fpLRqJO8M/c3jnYxFkUVC4ZIG12SiH=5v0mXDazWBTsuw7QetbKdoPyAl+hN9rgE"
        local_56 = 0
        local_57 = ""
        for local_13 in range(len(local_53) - 1, 0, -3):
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_53[local_13] ^ Unsigned_right_shift(58, local_58) & 255
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 1] ^ Unsigned_right_shift(58, local_58) & 255) << 8
            local_58 = 8 * (local_56 % 4)
            local_56 = local_56 + 1
            local_59 = local_59 | (local_53[local_13 - 2] ^ Unsigned_right_shift(58, local_58) & 255) << 16
            local_57 = local_57 + local_55[local_59 & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 6) & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 12) & 63]
            local_57 = local_57 + local_55[Unsigned_right_shift(local_59, 18) & 63]
        return '2.0_' + local_57

    # 巨量广告数据
    def qianchuan_ad_keyword_hot(self, industry_id="19060101", city=None, cookie=None, search_type='hot_search_words',
                                 business_words_num=500, offset=0, limit=0):
        ret_data = []
        ret_err = 0

        if cookie is None:
            all_cookie = mode_pro.qianchuan_index_cookie()
            cookie = random.choice(all_cookie)
        headers = cookie['headers']
        cookies = cookie['cookies']
        aadvid = cookie['aadvid']
        day0 = mode_time.zero_clock(0)
        day2 = mode_time.zero_clock(2)
        day7 = mode_time.zero_clock(7)

        city_change = {
            "北京-北京": "北京",
            "天津-天津": "天津",
            "台湾-台湾": "台湾",
            "香港-香港": "香港",
            "澳门-澳门": "澳门",
            "重庆-重庆": "重庆",
            "上海-上海": "上海",
        }

        # 热搜词=hot_search_words，商机词=business_words，飙升词=up_words
        if search_type == 'hot_search_words':
            stat_time_type = 7
            metric_type = 1
            filed1 = 'search_rank_pv_filter'
            metrics = ["search_rank_query_pv", "search_rank_pv_filter"]
            orderBy = 'search_rank_query_pv'
            startTime = day7 * 1000
        elif search_type == 'business_words':
            stat_time_type = 7
            metric_type = 2
            filed1 = 'search_rank_cost_filter'
            metrics = ["search_rank_cost", "search_rank_cost_filter"]
            orderBy = 'search_rank_cost'
            startTime = day7 * 1000
        else:
            stat_time_type = 2
            metric_type = 3
            filed1 = 'search_rank_surging_filter'
            metrics = ["search_rank_surging_pv", "search_rank_surging_rate", "search_rank_surging_filter"]
            orderBy = 'search_rank_surging_pv'
            startTime = day2 * 1000

        # 请求参数
        filters = [{"field": "stat_time_type", "operator": 7, "type": 3, "values": [f"{stat_time_type}"]},
                   {"field": "metric_type", "operator": 7, "type": 1, "values": [f"{metric_type}"]},
                   {"field": "industry_id", "operator": 7, "type": 3, "values": industry_id},
                   {"field": filed1, "operator": 1, "type": 3, "values": ["1"]}]
        city = eval(city)
        for index_ct, ct in enumerate(city):
            if ct in city_change:
                city[index_ct] = city_change[ct]
        filters.append({"field": "region", "operator": 7, "type": 2, "values": city})

        data = {
            "dataTopic": "ad_query_traffic_data",
            "dimensions": ["query"],
            "endTime": day0 * 1000,
            "filters": filters,
            "metrics": metrics,
            "orderBy": [{"field": orderBy, "type": 1}], "page": {"limit": limit, "offset": offset},
            "platform": 1,
            "startTime": startTime,
            "extraInfo": {"refer_origin": "ad.oceane" + "ngine.com/statistics_pages/tool_apps/flow_analysis/search",
                          "refer_code": "ad_platform_search_traffic_analysis"}
        }
        response = requests.post(
            f'https://ad.oceanengine.com/nbs/api/statistics/customize_report/data?aadvid={aadvid}',  # 分类热词
            headers=headers, cookies=cookies, data=json.dumps(data))
        if response.status_code == 200:
            data_data = response.json()
            code = data_data.get('code')
            msg = data_data.get('msg')
            if code == 0 and msg == '':
                ret_err = 1
                data_main = data_data.get('data')
                if data_main:
                    rows = data_main.get('rows')
                    rank = 1

                    if search_type == 'hot_search_words':
                        for r in rows:
                            ret_data.append({
                                'keyword': r['dimensions']['query'],
                                'search_day7_value': r['metrics']['search_rank_query_pv'],
                                'search_day7_rank': rank
                            })
                            rank += 1
                    elif search_type == 'business_words':
                        for r in rows:
                            ret_data.append({
                                'keyword': r['dimensions']['query'],
                                'search_rank_cost': r['metrics']['search_rank_cost'],
                                'search_rank': rank
                            })
                            rank += 1
                    else:
                        for r in rows:
                            ret_data.append({
                                'keyword': r['dimensions']['query'],
                                'search_value': r['metrics']['search_rank_surging_pv'],
                                'search_value_rate': r['metrics']['search_rank_surging_rate'],
                                'search_rank': rank
                            })
                            rank += 1

        return ret_err, ret_data

    def api_chat_gpt(self, content):
        url = "https://openai.api2d.net/v1/chat/completions"  # 测试

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer fk215502-0oylzDR9jHuhUTw2hOy9yaNWY6zuPsPP'
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": content}]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        except:
            pass

    # 巨量广告cookie
    def wechat_search_keyword_cookie(self):
        data_list = []
        sql = f"SELECT * FROM `cd_task` WHERE id IN (43);"
        ret = self.mysql_db(method='s', table='cd_task', sql=sql)
        for i in ret:
            data_dict = {}
            json_data = eval(i[7])
            gdt_token = json_data['gdt_token']
            g_tk = json_data['g_tk']
            owner = json_data['owner']
            mp_tk = json_data['mp_tk']
            campaign_id = json_data['campaign_id']
            data_dict['gdt_token'] = gdt_token
            data_dict['g_tk'] = g_tk
            data_dict['owner'] = owner
            data_dict['mp_tk'] = mp_tk
            data_dict['campaign_id'] = campaign_id

            data_list.append(data_dict)
        return data_list


# cos
class Cos:

    def __init__(self, **kwargs):
        # 选择服务器
        server_select = kwargs.get("server_select", 'jike')
        if server_select == 'personal':
            self.secret_id = config_dict['cos']['gaoyang']['secret_id']
            self.secret_key = config_dict['cos']['gaoyang']['secret_key']
        else:
            self.secret_id = config_dict['cos']['secret_id']
            self.secret_key = config_dict['cos']['secret_key']
        self.region = config_dict['cos']['region']
        self.scheme = config_dict['cos']['scheme']
        self.config = CosConfig(Region=self.region,
                                SecretId=self.secret_id,
                                SecretKey=self.secret_key,
                                Scheme=self.scheme)
        self.client = CosS3Client(self.config)

    # 创建存储桶
    def create_bucket(self, bucket_name):
        response = self.client.create_bucket(
            Bucket=bucket_name
        )

    # 查看文件是否纯在
    def file_exist(self, Bucket, path, file):
        try:
            response = self.client.head_object(
                Bucket=Bucket,
                Key=f'{path}{file}',  # video/qq.png
            )
            return response
        except:
            return False

    # 上传文件
    def upload_file(self, Bucket, loc_path, path, file):
        try:
            response = self.client.upload_file(
                Bucket=Bucket,
                LocalFilePath=loc_path,  # 本地文件的路径 'qq.png'
                Key=f'{path}{file}',  # 上传到桶之后的文件名  'video/qq.png'
                PartSize=1,  # 上传分成几部分
                MAXThread=10,  # 支持最多的线程数
                EnableMD5=False  # 是否支持MD5
            )
            return response
        except:
            return False

    # 获取链接
    def get_url(self, Bucket, path, file):
        try:
            download_url = self.client.get_presigned_url(
                Bucket=Bucket,
                Key=f'{path}{file}',  # video/qq.png
                Method='GET',
            )
            return download_url
        except Exception as E:
            print('Fr包err cnd获取路径失败', E)


# myself 高阳本人信息
class MyGy:

    def __init__(self, **kwargs):
        self.fr1997_config_dict = cache_get("fr1997_config_dict")

    # 获取信息
    def get_myself_info(self):
        return self.fr1997_config_dict

    # 获取出生年龄等信息
    def get_age_info(self):
        name = self.fr1997_config_dict['name']
        return name


mode_feishu = Feishu()  # 飞书app api
mode_time = TimeJike()  # 时间处理
mode_text = TextJike()  # 文本处理
mode_data = DataJike()  # 数据处理
mode_spider = SpiderJike()  # 数据请求
mode_django = DjangoJike()  # django配置
mode_douyin = DouyinJike()  # douyin配置
mode_pros = ModeStatic()  # 其它函数
mode_cos = Cos()  # cos
mode_fr_cos = Cos(server_select='personal')  # cos 高阳
mode_myself = MyGy()

mode_pro = ModeFunc()  # main

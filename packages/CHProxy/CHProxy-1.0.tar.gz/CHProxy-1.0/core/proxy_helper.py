import sqlite3
import time

import requests
from typing import List

from core.proxy_info import ProxyInfo


class ProxyHelper(object):
    user_name = ""
    password = ""
    token = ""
    connection: sqlite3.Connection

    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password
        self.initialize_database()

    def initialize_database(self):
        self.connection = sqlite3.connect('proxy.db')
        cursor = self.connection.cursor()
        cursor.execute(
            '''
                        CREATE TABLE IF NOT EXISTS proxies (
                            proxy_id INTEGER PRIMARY KEY,
                            ip TEXT,
                            http_port TEXT,
                            http_port_secured TEXT,
                            s5_port TEXT,
                            s5_port_secured TEXT,
                            expire_at_timestamp INTEGER,
                            province TEXT,
                            city TEXT,
                            carrier TEXT
                        )
                    '''
            )
        self.connection.commit()

    def get_proxy_from_db(self, province=None, city=None, carrier=None) -> ProxyInfo:
        cursor = self.connection.cursor()
        query = 'SELECT * FROM proxies WHERE expire_at_timestamp > ?'
        params = [int(time.time())]

        if province is not None:
            query += ' AND province = ?'
            params.append(province)

        if city is not None:
            query += ' AND city = ?'
            params.append(city)

        if carrier is not None:
            query += ' AND carrier = ?'
            params.append(carrier)

        cursor.execute(query, params)
        row = cursor.fetchone()
        return self.proxy_info_from_row(row) if row else None

    @staticmethod
    def proxy_info_from_row(row):
        keys = ['proxy_id', 'ip', 'http_port', 'http_port_secured', 's5_port',
                's5_port_secured',
                'expire_at_timestamp',
                'province', 'city', 'carrier']
        data = dict(zip(keys, row))
        return ProxyInfo(data)

    def delete_proxy_from_db(self, proxy_info: ProxyInfo):
        cursor = self.connection.cursor()
        query = 'DELETE FROM proxies WHERE ip = ?'
        cursor.execute(query, (proxy_info.ip,))

    def save_proxy_to_db(self, proxy_info):
        cursor = self.connection.cursor()
        query = '''
            INSERT INTO proxies (
                proxy_id, ip, http_port, http_port_secured, 
                s5_port, s5_port_secured, expire_at_timestamp, province, city, carrier
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(proxy_id) DO UPDATE SET
                ip=excluded.ip,
                http_port=excluded.http_port,
                http_port_secured=excluded.http_port_secured,
                s5_port=excluded.s5_port,
                s5_port_secured=excluded.s5_port_secured,
                expire_at_timestamp=excluded.expire_at_timestamp,
                province=excluded.province,
                city=excluded.city,
                carrier=excluded.carrier
        '''
        cursor.execute(
            query, (
                proxy_info.proxy_id, proxy_info.ip, proxy_info.http_port,
                proxy_info.http_port_secured, proxy_info.s5_port,
                proxy_info.s5_port_secured,
                proxy_info.expire_at_timestamp, proxy_info.province, proxy_info.city,
                proxy_info.carrier
            )
            )
        self.connection.commit()

    @staticmethod
    def test_proxy(proxy_info: ProxyInfo):
        url = "https://www.baidu.com"
        proxy = f"http://{proxy_info.ip}:{proxy_info.http_port}"
        proxies = {
            "http": proxy,
            "https": proxy
        }
        try:
            response = requests.get(url, proxies=proxies, timeout=5)
            if response.status_code == 200:
                return True
        except Exception as e:
            print(e)
        return False

    def get_token(self):
        url = f"https://api.caihongdaili.com/api/login?username={self.user_name}&password={self.password}"
        request = requests.get(url)
        response = request.json()
        if response['status'] != 0:
            raise Exception(
                f"Failed to get token: {response['msg']} data: {response['data']}"
                )
        return response['data']['token']

    def get_proxy(
            self, province=None, city=None, carrier=None, expire=60 * 60 * 24
            ) -> ProxyInfo:
        proxy_info = self.get_proxy_from_db(province, city, carrier)
        if proxy_info:
            if self.test_proxy(proxy_info):
                return proxy_info
            self.release_proxy(proxy_info)

        if not self.token:
            self.token = self.get_token()
        url = (
            f"http://api.caihongdaili.com/proxy/unify/get?token={self.token}&product_type=exclusive&proxy_type=http"
            f"&amount=1&expire={expire}")
        if province:
            url += f"&province={province}"
        if city:
            url += f"&city={city}"
        if carrier:
            url += f"&carrier={carrier}"
        request = requests.get(url)
        response = request.json()
        if response['status'] != 0:
            if response["msg"] == 'line resource limit':
                using_proxy_list = self.get_using_proxy()
                self.release_proxy_list(using_proxy_list)
                return self.get_proxy(province, city, carrier, expire)
            raise Exception(
                f"Failed to get proxy: {response['msg']} data: {response['data']}"
                )
        proxy_info = ProxyInfo(response['data'][0])
        if self.test_proxy(proxy_info) is False:
            self.release_proxy(proxy_info)
            return self.get_proxy(province, city, carrier, expire)
        self.save_proxy_to_db(proxy_info)  # 将新获取的代理信息保存到数据库
        return proxy_info

    def add_ip_write(self, ip):
        url = f'https://api.caihongdaili.com/proxy/ipwhite/add?token={self.token}&ip={ip}'
        request = requests.get(url)
        response = request.json()
        if response['status'] != 0:
            raise Exception(
                f"Failed to add ip write: {response['msg']} data: {response['data']}"
                )
        return response['data']

    def get_using_proxy(self) -> List[ProxyInfo]:
        url = f'https://api.caihongdaili.com/proxy/list?token={self.token}'
        request = requests.get(url)
        response = request.json()
        if response['status'] != 0:
            raise Exception(
                f"Failed to get using proxy: {response['msg']} data: {response['data']}"
                )
        proxys = []
        for data in response['data']:
            proxy_info = ProxyInfo(data)
            proxys.append(proxy_info)
        return proxys

    def release_proxy_list(self, proxy_list: List[ProxyInfo]):
        for proxy in proxy_list:
            self.release_proxy(proxy)
        return True

    def release_proxy(self, proxy_info: ProxyInfo):
        if not self.token:
            self.token = self.get_token()
        url = f'https://api.caihongdaili.com/api/ip/proxy/release?token={self.token}&id={proxy_info.proxy_id}'
        request = requests.get(url)
        response = request.json()
        if response['status'] != 0:
            raise Exception(
                f"Failed to release proxy: {response['msg']} data: {response['data']}"
                )
        self.delete_proxy_from_db(proxy_info)
        return True

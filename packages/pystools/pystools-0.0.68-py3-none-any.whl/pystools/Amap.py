# -*- coding: utf-8 -*-
import json

import urllib3

http = urllib3.PoolManager(cert_reqs='CERT_NONE')
class Amap:
    def __init__(self, key, secret=None,**kwargs):
        self.__dict__.update(locals())
        self.key = key
        self.secret = secret
    def geo(self,address):
        url = f'https://restapi.amap.com/v3/geocode/geo?' \
              f'address={address}' \
              f'&output=json' \
              f'&key={self.key}'

        resp = http.request('GET', url)
        resp_msg = resp.data.decode('utf-8')
        status = resp.status
        if status != 200:
            raise Exception(f"status:{status},response:{resp_msg}")

        addr_json = json.loads(resp_msg)
        return addr_json

    def ipconfig(self,ip):
        url = f"https://restapi.amap.com/v3/ip?ip={ip}&output=json&key={self.key}"
        resp = http.request("GET", url)
        resp_data = resp.data
        resp_msg = resp.data.decode('utf-8')
        status = resp.status
        if status != 200:
            raise Exception(f"status:{status},response:{resp_msg}")
        ipinfos = json.loads(resp_data)
        return ipinfos

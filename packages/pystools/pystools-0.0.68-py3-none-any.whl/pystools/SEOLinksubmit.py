# -*- coding: utf-8 -*-
import json

import urllib3
from typing import List

http = urllib3.PoolManager()


def baidu_linksubmit(submit_url, links: List[str]):
    headers = {
        'Content-Type': 'text/plain'
    }
    data = "\n".join(links)
    response = http.request('POST', submit_url, headers=headers, body=data)
    print(response.status)
    resp_status = response.status

    resp = {
        "success": 0,
        "status": resp_status,
        "data": response.data
    }
    if resp_status != 200:
        return resp

    resp_body = response.data.decode('utf-8')
    resp_json = json.loads(resp_body)
    success = resp_json.get('success', None)
    error = resp_json.get('error', None)

    resp["data"] = resp_json
    if success:
        resp["success"] = 1
    if error:
        resp["success"] = 0
    return resp


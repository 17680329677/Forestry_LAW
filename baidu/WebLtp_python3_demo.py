#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import urllib.request
import urllib.parse
import json
import hashlib
import base64
# 接口地址
url = "http://ltpapi.xfyun.cn/v1/sdgp"
# 开放平台应用ID
x_appid = "5dcb67fc"
# 开放平台应用接口秘钥
api_key = "ae692f6e6934e1cdeb788e7854181443"
# 语言文本
TEXT = "为了促进绿化事业的发展，改善城市生态环境，根据国务院《城市绿化条例》以及有关法律、行政法规，结合本市实际，制定本条例。"


def main():
    body = urllib.parse.urlencode({'text': TEXT}).encode('utf-8')
    param = {"type": "dependent"}
    x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
    x_time = str(int(time.time()))
    x_checksum = hashlib.md5(api_key.encode('utf-8') + str(x_time).encode('utf-8') + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib.request.Request(url, body, x_header)
    result = urllib.request.urlopen(req)
    result = result.read()
    print(result.decode('utf-8'))
    return


if __name__ == '__main__':
    main()

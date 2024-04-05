import base64
import os

import typer
import requests


def captcha(file_abs_path: str, aliyun_ocr_appcode: str, pri_id='dn') -> str:
    with open(file_abs_path, 'rb') as f:
        b64_string = base64.b64encode(f.read()).decode('utf-8')

    host = 'https://yzmcolor.market.alicloudapi.com'
    request_path = '/yzmSpeed'
    url = host + request_path
    header = {'Authorization': 'APPCODE ' + aliyun_ocr_appcode,
              "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
    data = {
        'pri_id': pri_id,
        'v_pic': b64_string
    }
    resp = requests.post(url, data=data, headers=header)
    if resp.status_code != 200:
        return ''
    try:
        v_code = resp.json()['v_code']
        print(v_code)
        return v_code
    except:
        return ''


if __name__ == '__main__':
    typer.run(captcha)

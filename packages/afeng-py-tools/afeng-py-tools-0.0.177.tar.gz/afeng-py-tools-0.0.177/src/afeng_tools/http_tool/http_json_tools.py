import requests


def get_json(url: str, params: dict = None, headers: dict = None, cookies: dict = None, encoding: str = 'utf-8'):
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    if response.status_code == 200:
        response.encoding = encoding
        return response.text


def post_json(url: str, headers: dict = None, params: dict = None, files: dict = None,
              cookies: dict = None, data: dict = None, json: dict = None, encoding: str = 'utf-8'):
    response = requests.post(url, headers=headers, params=params, data=data, json=json, files=files, cookies=cookies)
    if response.status_code == 200:
        response.encoding = encoding
        return response.json()


if __name__ == '__main__':
    result = post_json('http://www.zmtt.net/checkUpdate', json={"version": "2.0"})
    print(result)

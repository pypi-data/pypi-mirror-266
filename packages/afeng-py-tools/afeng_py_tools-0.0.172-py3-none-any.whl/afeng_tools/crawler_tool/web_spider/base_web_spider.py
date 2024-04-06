from typing import Literal

import requests


class BaseWebSpider:
    @classmethod
    def handle_response(cls, response,
                        response_type: Literal['text', 'content', 'json'] = 'text',
                        response_encoding: str = 'utf-8'):
        if response.status_code == 200:
            response.encoding = response_encoding
            if response_type == 'json':
                return response.json()
            else:
                return getattr(response, response_type)

    @classmethod
    def request_get(cls, url: str, params: dict = None,
                    headers: dict = None, cookies: dict = None,
                    allow_redirects: bool = True, proxies=None,
                    response_type: Literal['text', 'content', 'json'] = 'text',
                    response_encoding: str = 'utf-8'):
        print(url)
        response = requests.get(url, params=params, headers=headers, cookies=cookies,
                                allow_redirects=allow_redirects, proxies=proxies)
        return cls.handle_response(response, response_type=response_type, response_encoding=response_encoding)


if __name__ == '__main__':
    test_spider = BaseWebSpider()
    tmp_resp = test_spider.request_get('https://quotes.toscrape.com/tag/change/page/1/')
    print(tmp_resp)
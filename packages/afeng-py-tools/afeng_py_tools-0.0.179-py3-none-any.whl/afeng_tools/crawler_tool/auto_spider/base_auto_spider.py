import requests


def run_demo():
    response = requests.get('https://db.hbskw.com/pcms/index.php?m=content&c=index&a=lists&catid=34')
    if response.status_code == 200:
        response.encoding = 'utf-8'
        print(response.text)

if __name__ == '__main__':
    run_demo()
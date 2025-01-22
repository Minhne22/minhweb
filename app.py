import requests
from flask import Flask
import json
from pymongo import MongoClient
from requests.exceptions import HTTPError
import os
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return 'ok'

# Config DB
client = MongoClient("mongodb+srv://hahawelookcat:iXdyJYg1PSV140SZ@cluster0.my3yb.mongodb.net/")
db = client["minh"]
# query = {"bankcode": "john_doe"}


def check_and_insert(query):
    """
    Kiểm tra xem dữ liệu đã tồn tại trong collection hay chưa.
    Nếu chưa tồn tại, lưu dữ liệu và trả về True.
    Nếu đã tồn tại, trả về False.

    :param db: Đối tượng cơ sở dữ liệu MongoDB
    :param collection_name: Tên collection trong database
    :param query: Query để kiểm tra dữ liệu đã tồn tại
    :param new_data: Dữ liệu mới cần lưu
    :return: True nếu lưu thành công, False nếu dữ liệu đã tồn tại
    """
    collection = db['minh']

    # Kiểm tra dữ liệu đã tồn tại chưa
    if collection.find_one(query):
        return False  # Dữ liệu đã tồn tại

    # Nếu chưa tồn tại, thêm mới vào collection
    collection.insert_one(query)
    return True

# No db
NODBFILE = 'banks.txt'
if not os.path.exists(NODBFILE):
    open(NODBFILE, 'a+', encoding='utf8').close()


def no_db(banks):
    current = open(NODBFILE, encoding='utf8').read()
    no_existed = []
    for bank in banks:
        if bank not in current:
            no_existed.append(bank)
    with open(NODBFILE, 'a+', encoding='utf8') as f:
        f.write('\n'.join(no_existed) + '\n')
    return no_existed


CONFIG_FILE = 'config.json'
CONFIG = json.loads(open(CONFIG_FILE, encoding='utf8').read())

class telegram_bot:
    def __init__(self):
        self.bot_token = CONFIG['telegram_bot_token']
        self.admins = CONFIG['admins_id']
    
    def send_message(self, message):
        for admin in self.admins:
            while True:
                try:
                    response = requests.post(
                        f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={admin}&text={message}'
                    )
                    print(response.json())
                    break
                except Exception as e:
                    print(e)



class sunwin_oop:
    def __init__(self):
        self.auth_form = CONFIG['login']
        self.auth_token = ''
        
    def relogin(self):
        headers = {
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Accept-Language': 'vi-VN,vi;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Content-Length': '244',
            'User-Agent': 'Game/2.0.0 CFNetwork/1568.200.51 Darwin/24.1.0',
            'Content-Type': 'application/json',
            'Host': 'api.azhkthg1.net',
            'Accept': '*/*',
        }
        try:
            response = requests.post(
                'https://api.azhkthg1.net/id',
                headers=headers,
                json = self.auth_form
            ).json()
            return response
        except HTTPError as e:
            print(e)
        except Exception as e:
            return {
                'status': 1,
                'data': {
                    'message': str(e)
                }
            }
            
            
    
    def get_bank_code(self):
        while True:
            try:
                headers = {
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Authorization': self.auth_token,
                    'Accept': '*/*',
                    'User-Agent': 'Game/2.0.0 CFNetwork/1568.200.51 Darwin/24.1.0',
                    # 'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'vi-VN,vi;q=0.9',
                    'Host': 'api.azhkthg1.net',
                }
                response = requests.get(
                    'https://api.azhkthg1.net/paygate?command=fetchBankAccounts',
                    headers=headers
                ).json()
                return response
            except HTTPError as e:
                print(e)
            except Exception as e:
                return {
                    'code': 1,
                    'msg': str(e)
                }

def main():
    # Config telegram 
    telegram_client = telegram_bot()
    telegram_client.send_message('Bot run')
    # Login
    sun_client = sunwin_oop()
    get_tok = sun_client.relogin()
    token = get_tok['data']['accessToken']
    print(token)
    sun_client.auth_token = token
    # Bank
    while True:
        all_bank = sun_client.get_bank_code()
        if all_bank['status'] == 0:
            banks = []
            for bank in all_bank['data']['items']:
                bank_name = bank['fullName']
                for detail in bank['accounts']:
                    banks.append(f'{bank_name}|{detail["accountName"]}|{detail["accountNumber"]}')
            # Database
            # for bank in banks:
            #     if check_and_insert({'bankcode': bank}):
            #         telegram_client.send_message(bank)

            # No DB
            check = no_db(banks)
            for bank in check:
                telegram_client.send_message(bank)
        else:
            get_tok = sun_client.relogin()
            token = get_tok['data']['accessToken']
            print(token)
            sun_client.auth_token = token


if __name__ == '__main__':
    Thread(target=main).start()
    app.run()

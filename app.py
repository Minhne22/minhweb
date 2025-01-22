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
 
 
if name == '__main__': 
    Thread(target=main).start() 
    app.run()
import requests
import json

class ApiClient:
    def __init__(self, base_url="http://213.239.225.119", token=None):
        self.base_url = base_url
        self.token = token

    def login(self, username, password):
        headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                   }
        login_url = f"{self.base_url}:81/api/auth/login"
        data = f'username={username}&password={password}'
        response = requests.post(login_url, data=data,headers=headers)
        if response.status_code == 200:
            if response.json().get("error_code") == 0:
                self.token = response.json().get('data').get('access_token')
                return self.token
            
        raise ValueError("نام کاربری یا رمز عبور اشتباه است")

    def chat(self, bot_id,message):
        if not self.token:
            raise ValueError("لطفا ابتدا لاگین کنید")
        
        chat_url = f"{self.base_url}:5001/api/bot/{bot_id}/chat"
        headers = {'Authorization': f"Bearer {self.token}"}
        data = json.dumps({'data': message})
        response = requests.post(chat_url, headers=headers, data=data)
        return response.json()

    def bots(self):
        if not self.token:
            raise ValueError("لطفا ابتدا لاگین کنید")
        
        history_url = f"{self.base_url}:81/api/account/bot"
        headers = {'Authorization': f"Bearer {self.token}"}
        response = requests.get(history_url, headers=headers)
        return response.json()


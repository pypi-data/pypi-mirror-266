import requests


class APIClient:
    def __init__(self, base_url, username, usertoken):
        self.session = requests.Session()
        self.username = username
        self.usertoken = usertoken
        self.base_url = base_url
        self.login_url = f'http://{self.base_url}:80/tokenAPI'
        self.token = None

    def login(self):
        """LOG IN"""
        data = {'username': self.username, 'usertoken': self.usertoken}
        try:
            response = self.session.post(url=self.login_url, json=data)
            response.raise_for_status()
            self.token = response.json().get('token')
            return True
        except requests.RequestException as e:
            print(f"Login failed: {e}")
            return False

    def call_api(self, api_type, song_quality, song_singer, song_source):
        """CALL API"""
        if not self.token:
            if not self.login():
                print("⚠️ Login failed")
                return None

        headers = {'Authorization': f'Bearer {self.token}'}
        data = {
            'username': self.username,
            'GT': api_type,
            'HQ': song_quality,
            'SP': song_singer,
            'OA': song_source,
        }
        try:
            call_url = f'http://{self.base_url}:80/aivoxAPI'
            response = self.session.get(url=call_url, headers=headers, json=data, stream=True)
            response.raise_for_status()
            if response.json().get('status') == 'success':
                return response
            else:
                print("API call failed")
        except requests.RequestException as e:
            print(f"API call failed: {e}")

        return None

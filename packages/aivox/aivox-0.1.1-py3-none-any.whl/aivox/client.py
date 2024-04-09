import requests


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.is_logged_in = False

    def login(self, username, password):
        """LOGIN TOKEN"""
        response = self.session.post(f"{self.base_url}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            self.session.headers.update({'Authorization': f"Bearer {response.json()['token']}"})
            self.is_logged_in = True
            return True
        return False

    def generate(self, endpoint, data):
        """CONNCET API"""
        if not self.is_logged_in:
            print("Error: Not logged in or login failed.")
            return None
        response = self.session.post(f"{self.base_url}{endpoint}", json=data)
        return response.json()

    def playing(self, username, password, endpoint, data):
        """ENJOY MUSIC"""
        if not self.is_logged_in:
            if not self.login(username, password):
                return {"status": 'error', "message": "Login failed"}
        return self.generate(endpoint, data)

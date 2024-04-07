import requests

API_URL = "https://api.telegram.org/bot{token}/{method}"
FILE_URL = "https://api.telegram.org/file/bot{token}/{path}"

class API:
    def __init__(self, token):
        self.token = token
    
    def request(self, method, params=None, files=None):
        url = API_URL.format(token=self.token, method=method)
        response = requests.post(url, data=params, files=files)
        return response.json()

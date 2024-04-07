from api import API

class Base:
    def __init__(self, token):
        self.api = API(token)
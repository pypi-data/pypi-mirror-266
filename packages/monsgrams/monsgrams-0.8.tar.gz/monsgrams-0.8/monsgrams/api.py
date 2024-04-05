class TelegramAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"

    async def send_message(self, chat_id, text):
        url = self.base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()

    async def get_updates(self, offset=None):
        url = self.base_url + "getUpdates"
        params = {"offset": offset} if offset else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def send_dice(self, chat_id):
        url = self.base_url + "sendDice"
        data = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()

    async def get_chat(self, chat_id):
        url = self.base_url + "getChat"
        params = {"chat_id": chat_id}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def send_emoji(self, chat_id, emoji):
        url = self.base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": emoji}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()
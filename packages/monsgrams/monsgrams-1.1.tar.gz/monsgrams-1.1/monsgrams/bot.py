import asyncio
import aiohttp

class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.commands = {}

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

    async def reply(self, chat_id, message_id, text):
        url = self.base_url + "sendMessage"
        data = {"chat_id": chat_id, "text": text, "reply_to_message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()

    async def delete_message(self, chat_id, message_id):
        url = self.base_url + "deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()

    async def get_user_profile_photos(self, user_id):
        url = self.base_url + "getUserProfilePhotos"
        params = {"user_id": user_id}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def send_photo(self, chat_id, photo, caption=None):
        url = self.base_url + "sendPhoto"
        data = {"chat_id": chat_id, "photo": photo}
        if caption:
            data["caption"] = caption
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()

    async def polling_loop(self):
        offset = None
        while True:
            updates = await self.get_updates(offset)
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")
                user_id = message.get("from", {}).get("id")
                chat_type = message.get("chat", {}).get("type")
                if text.startswith("/"):
                    command_name = text.split()[0][1:]
                    command = self.commands.get(command_name)
                    if command:
                        context = BotContext(self, chat_id, user_id, chat_type)
                        await command(context)
                    else:
                        print("not found cmd")

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

class BotContext:
    def __init__(self, bot, chat_id, from_user_id, chat_type):
        self.bot = bot
        self.chat_id = chat_id
        self.user_id = from_user_id
        self.chat_type = chat_type
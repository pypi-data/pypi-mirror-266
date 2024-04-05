import asyncio
import aiohttp
from monsgrams.context import BotContext
from monsgrams.api import TelegramAPI

class Bot(TelegramAPI):
    def __init__(self, token):
        super().__init__(token)
        self.commands = {}

    async def get_updates(self, offset=None):
        return await super().get_updates(offset)

    def command(self, name):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

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

    async def send_message(self, chat_id, text):
        return await super().send_message(chat_id, text)
    
    async def send_dice(self, chat_id):
        return await super().send_dice(chat_id)
    
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

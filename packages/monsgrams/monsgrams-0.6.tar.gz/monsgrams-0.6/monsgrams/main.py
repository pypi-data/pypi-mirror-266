import asyncio
import aiohttp
from api import TelegramAPI

class Bot:
    def __init__(self, token):
        self.api = TelegramAPI(token)
        self.commands = {}

    async def get_updates(self, offset=None):
        url = self.api.base_url + "getUpdates"
        params = {"offset": offset} if offset else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

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
                if text.startswith("/"):
                    command_name = text.split()[0][1:]
                    command = self.commands.get(command_name)
                    if command:
                        await command(self, chat_id)
                    else:
                        print("not found cmd")


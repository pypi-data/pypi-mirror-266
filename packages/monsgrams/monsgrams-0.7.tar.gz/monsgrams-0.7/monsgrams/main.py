import asyncio
import aiohttp
from api import TelegramAPI
from context import BotContext

class Bot:
    def __init__(self, token):
        self.api = TelegramAPI(token)
        self.commands = {}

    async def get_updates(self, offset=None):
        return await self.api.get_updates(offset)

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
                from_user_id = message.get("from", {}).get("id")
                chat_type = message.get("chat", {}).get("type")
                if text.startswith("/"):
                    command_name = text.split()[0][1:]
                    command = self.commands.get(command_name)
                    if command:
                        context = BotContext(self, chat_id, from_user_id, chat_type)
                        await command(context)
                    else:
                        print("not found cmd")

    async def send_message(self, chat_id, text):
        return await self.api.send_message(chat_id, text)
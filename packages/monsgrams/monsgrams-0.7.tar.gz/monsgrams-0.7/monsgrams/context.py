class BotContext:
    def __init__(self, bot, chat_id, from_user_id, chat_type):
        self.bot = bot
        self.chat_id = chat_id
        self.from_user_id = from_user_id
        self.chat_type = chat_type
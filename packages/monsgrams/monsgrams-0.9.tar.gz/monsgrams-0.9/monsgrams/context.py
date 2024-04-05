class BotContext:
    def __init__(self, bot, chat_id, user_id, chat_type):
        self.bot = bot
        self.chat_id = chat_id
        self.user_id = user_id
        self.chat_type = chat_type

    def __str__(self):
        return str({
            "bot": self.bot,
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "chat_type": self.chat_type
        })

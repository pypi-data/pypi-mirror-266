**This library provides interesting opportunities for creating telegram bots.
convenient syntax, decorators.**

# EXAMPLE USE!
```python
from monsgrams import Bot
bot = TelegramBot("YOUR_BOT_TOKEN")

@bot.command("start")
async def start_command(bot, chat_id):
    await bot.send_message(chat_id, "Hello! I am bot. How are you?")

async def main():
    await polling_loop(bot)

if __name__ == "__main__":
    asyncio.run(main())

```

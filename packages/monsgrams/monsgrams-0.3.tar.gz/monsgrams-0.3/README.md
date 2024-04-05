**This library provides interesting opportunities for creating telegram bots.
convenient syntax, decorators.**

# EXAMPLE USE!
```python
from monsgrams import Bot
bot = Bot("your_token")

@bot.command("start")
async def start(ctx, chat_id):
    await ctx.send_message(chat_id, "Hello!")

bot.startPolling()
```

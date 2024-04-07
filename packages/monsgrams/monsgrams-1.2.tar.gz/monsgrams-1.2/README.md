**This library provides interesting opportunities for creating telegram bots.
convenient syntax, decorators.**

# EXAMPLE USE!
```python
from bot import Bot

bot = Bot("your_token")

@bot.event
def on_message(message):
  if message.text == "/start":
    message.reply("Cool this lib!")

bot.listen_message()
```
DOCS - wtiting..
(in future: grub-project.vercel.app/wiki/monsgrams/)
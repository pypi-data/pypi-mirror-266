**This library provides interesting opportunities for creating telegram bots.
convenient syntax, decorators.**

# EXAMPLE USE!
```python
bot = Bot("7181251700:AAF26R-70RNWYXprybRMqtthnTRjJU7LeNM")

@bot.command("start")
async def start_command(context):
    await context.bot.send_message(context.chat_id, f"Hello! I am bot. How are you? User ID: {context.from_user_id}, Chat Type: {context.chat_type}")

async def main():
    await bot.polling_loop()

if __name__ == "__main__":
    asyncio.run(main())
```
DOCS - WRITING.
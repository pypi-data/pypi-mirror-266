import aiohttp

class TelegramAPI:
  def __init__(self, token):
    self.token = token
    self.base_url = f"https://api.telegram.org/bot{token}/"
  def send_message(self, chat_id, text):
    url = self.base_url + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    async with aiohttp.ClientSession as session:
      async with session.post(url, json=data) as response:
        return response.json()
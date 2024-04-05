import requests

class Bot:
  def __init__(self, token):
    self.token = token
    self.base_url = f"https://api.telegram.org/bot{token}/"
    self.command = {}
  
  def send_message(self, chat_id, text):
    url = self.base_url + "send_message"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=data)
    return response.json()
  
  def get_updates(self, offset=None):
    url = self.base_url = + "getUpdates"
    params = {"offset": offset} if offset else {}
    response = requests.get(url, params=prams)
    return response.json()
  
  def command(self, name):
    def decorator(func):
      self.commands[name] = func
      return func
    return decorator
  
  async def connect(self):
    offset = None
    while True:
      updates = self.get_updates(offset)
      for update in updates.get("result", []):
        offset = update["update_id"] + 1
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")
        if text.startswith("/"):
          command_name = text.split[0][1:]
          if command:
            await command(self, chat_id)
          else:
            print("command not found")
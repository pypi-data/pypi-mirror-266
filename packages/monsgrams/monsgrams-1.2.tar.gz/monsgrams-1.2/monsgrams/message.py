class Sender:
    def __init__(self, sender_data):
        self.id = sender_data.get('id', '')
        self.name = sender_data.get('first_name', '')
        self.surname = sender_data.get('last_name', '')
        self.username = sender_data.get('username', '')
        self.language_code = sender_data.get('language_code', '')
        self.avatar = None

    def get_avatar(self, bot):
        if not self.avatar:
            params = {'user_id': self.id}
            response = bot.api.request('getUserProfilePhotos', params=params)
            if response['ok']:
                photos = response['result']['photos']
                if photos:
                    photo_file_id = photos[0][0]['file_id']
                    file_path = self.get_file_path(bot, photo_file_id)
                    self.avatar = file_path
        return self.avatar

    def get_file_path(self, bot, file_id):
        params = {'file_id': file_id}
        response = bot.api.request('getFile', params=params)
        if response['ok']:
            file_path = response['result']['file_path']
            return f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
        return None

class Chat:
    def __init__(self, chat):
        self.id = chat.get('id', '')
        self.title = chat.get('title', '')
        self.link = f"t.me/{chat.get('username', '')}"
        self.is_forum = chat.get('is_forum', '')
        self.type = chat.get('type', '')

class Message:
    def __init__(self, message_data, bot):
        self.id = message_data['message_id']
        self.sender = Sender(message_data['from'])
        self.chat = Chat(message_data['chat'])
        self.date = message_data['date']
        self.text = message_data.get('text', '')
        self.bot = bot
        self.log = message_data

    def send(self, text, markup=False):
        params = {'chat_id': self.chat.id, 'text': text, 'parse_mode': 'Markdown' if markup else None}
        self.bot.api.request('sendMessage', params=params)

    def reply(self, text, markup=False):
        params = {'chat_id': self.chat.id, 'text': text, 'reply_to_message_id': self.id, 'parse_mode': 'Markdown' if markup else None}
        self.bot.api.request('sendMessage', params=params)
    
    def send_photo(self, photo, caption=None):
        params = {'chat_id': self.chat.id}
        files = {'photo': open(photo, 'rb')}  # Corrected the typo here
        if caption:
            params['caption'] = caption
        return self.bot.api.request('sendPhoto', params=params, files=files)
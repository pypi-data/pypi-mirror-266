import time
from base import Base

class Bot(Base):
    def __init__(self, token):
        super().__init__(token)
        self.last_update_id = None
        self.message_handlers = []

    def get_updates(self, offset=None, limit=None, timeout=None):
        params = {'offset': offset, 'limit': limit, 'timeout': timeout}
        response = self.api.request('getUpdates', params=params)
        if response['ok']:
            updates = response['result']
            if updates:
                self.last_update_id = updates[-1]['update_id'] + 1
            return updates
        else:
            return []

    def listen_message(self):
        while True:
            updates = self.get_updates(offset=self.last_update_id, timeout=30)
            for update in updates:
                if 'message' in update:
                    message_data = update['message']
                    message = Message(message_data, self)
                    self.handle_message(message)
            time.sleep(1)

    def event(self, func):
        self.message_handlers.append(func)
        return func

    def handle_message(self, message):
        for handler in self.message_handlers:
            handler(message)

from message import Message

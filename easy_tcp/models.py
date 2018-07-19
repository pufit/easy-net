from .errors import BadRequest
import json


class Message:

    def __init__(self, message_type: str, data=None):
        self.type = message_type
        self.data = data if data else {}

    @classmethod
    def from_json(cls, message: bytes):
        try:
            message_dict = json.loads(message.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise BadRequest
        message_type = message_dict.get('type')
        if not message_type:
            raise BadRequest
        return cls(message_type, message_dict.get('data'))

    def dump(self):
        return json.dumps({
            'type': self.type,
            'data': self.data
        })
